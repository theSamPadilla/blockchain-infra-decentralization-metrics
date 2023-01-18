import requests
from datetime import datetime
import time
import json
import pandas as pd

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
    next_url = f"https://{BASE_URL}{_next}"
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
    df["address"] = df["beneficiaries"].apply(lambda x: x[0])
    df["ip"] = df["node"].apply(lambda x: x.get("ip","unknown"))
    df["stake"] = df["stake"].apply(lambda x: x["total"]) # NOTE: need to scale
    df["is_validator"] = True
    df["extra_info"] = df.apply(lambda x: {"name": x["name"], "manager": x["manager"]}, axis=1)

    # select only relevant rows
    df = df[["address","ip","stake","is_validator","extra_info"]]
    return df

# Get validators
validators = get_validators()

today = datetime.today().strftime("%Y-%m-%d")
validators.to_csv(f"avalanche-validators-{today}.csv", index=False)
print(validators)

# Want data in this format
"""
[
    {
        <IP Address> : {
            "is_validator": <bool> #Differentiate between RPC nodes and validator nodes.
            "stake": <int> #Stake of the validator or null if RPC node.
            "address": <string> #On-chain address of the validator.
            "extra_info": {
                <Any other info you want to add that may be useful in processing (validator name, skip rate, etc)>
            }
        }
    }
]
"""

# drop validators where ip = 'unkown'
validators = validators[validators['ip'] != 'unknown']
validators_dict = validators.set_index('ip').T.to_dict()

# save to json
with open(f'avalanche-validators-{today}.json', 'w') as f:
    json.dump(validators_dict, f)
print(validators_dict)
