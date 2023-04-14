import requests
from datetime import datetime
import time
import json
import pandas as pd
from typing import Dict

def get_validators() -> pd.DataFrame:
    """
    Get validators from avascan api

    @return: pandas dataframe
    """

    url = "https://api-beta.avascan.info/v2/network/mainnet/staking/validations"
    params = {
        "status": "active",
    }
    response = requests.get(url, params=params).json()
    _next = response["link"].get("next")
    next_url = f"https://api-beta.avascan.info{_next}"

    tmp_df = pd.DataFrame(response["items"])
    df = tmp_df.copy()

    # NOTE: timeout is >2x the time it takes to get ~1.2k, 2.5min
    timeout = time.time() + (60 * 6)  # 6 minutes from now

    while not tmp_df.empty:
        print("running", int(timeout - time.time()))
        if time.time() > timeout:
            break

        # Handling rate limiting
        time.sleep(1.2)

        response = requests.get(next_url).json()
        if "link" not in response.keys():
            break
        _next = response["link"].get("next")
        next_url = f"https://api-beta.avascan.info{_next}"
        tmp_df = pd.DataFrame(response["items"])

        df = pd.concat([df, tmp_df], axis=0)


    # unpack everything
    df["address"] = df["nodeId"]
    df["ip"] = df["node"].apply(lambda x: x.get("ip","unknown"))
    df["stake"] = df["stake"].apply(lambda x: int(x["total"]) // 1000000000)
    df["is_validator"] = True
    df["extra_info"] = df.apply(lambda x: {"name": x["name"], "manager": x["manager"]}, axis=1)

    # select only relevant rows
    df = df[["address","ip","stake","is_validator","extra_info"]]
    return df

def main() -> Dict:
    # Get validators
    validators = get_validators()

    # copy the addresses to other_addresses to group all later
    validators["other_addresses"] = validators["address"]

    # group by IPs, sum the stake of all the IPs (even if they map to the same pool), aggregate the addresses where they appear
    validators = validators.groupby('ip').agg({'stake': 'sum', 'extra_info': 'first', 'is_validator': 'first', 'other_addresses': lambda x: list(x), 'address': 'first'}).reset_index()

    # update extra info
    validators["extra_info"] = validators.apply(lambda x: {"name": x["extra_info"]["name"] if not pd.isna(x["extra_info"]["name"]) else "", "manager": x["extra_info"]["manager"] if not pd.isna(x["extra_info"]["manager"]) else "", "other_addresses": x["other_addresses"] if len(set(x["other_addresses"])) > 1 else ""}, axis=1)
    
    # drop extra column and return address
    validators.drop(columns=["other_addresses"], inplace=True)
    validators_dict = validators.set_index('ip').T.to_dict()
    return validators_dict

# save to json
if __name__ == "__main__":
    validators_dict = main()

    # save to json
    today = datetime.today().strftime("%Y-%m-%d")

    with open("config/SettingsConfig.json", "r") as f:
        buff = json.load(f)
        OUTPUT_FOLDER = buff["output_folder"]
        f.close()

    # NOTE: we want this format output
    # {
    # "timestamp": <str> # When was the analysis last ran
    # "collection_method": <str>, <"crawl" for nodes manually crawled, or "api" for IPs found via the chain RPC API>
    # "chain_data": {Any other information to add about the chain},
    # "nodes": {
    #     <IP Address> : {
    #         "is_validator": <bool>, #Differentiate between RPC nodes and validator nodes.
    #         "stake": <int>, #Stake of the validator or null if RPC node.
    #         "address": <string>, #On-chain address of the validator.
    #         "extra_info": {
    #             <Any other info you want to add that may be useful in processing (validator name, skip rate, etc)>
    #         }
    #     },
    #     <IP Address 2> : {},
    #     <IP Address 3> : {},
    #     .
    #     .
    # }}

    result = {
        "timestamp": today,
        "collection_method": "api",
        "chain_data": {},
        "nodes": validators_dict
    }


    with open(f'{OUTPUT_FOLDER}/avalanche.json', 'w') as f:
        json.dump(result, f, indent=4)
    print(f"Done. Check {OUTPUT_FOLDER}")
