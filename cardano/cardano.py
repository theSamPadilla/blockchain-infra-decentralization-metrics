"""
Cardano nodes
ref: https://docs.blockfrost.io/
"""
from typing import List, Dict
import pandas as pd
import requests
import time
import socket
import json
from datetime import datetime
import os


with open("config/SettingsConfig.json", "r") as f:
    buff = json.load(f)
    BLOCKFROST_PROJECT = buff["blackfrost_project"]
    OUTPUT_FOLDER = buff["output_folder"]
    f.close()

if BLOCKFROST_PROJECT is None:
    print("BLOCKFROST_PROJECT env var not set")
    exit(1)

HEADERS = {
    "Content-Type": "application/json",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "project_id": BLOCKFROST_PROJECT,
}
BASE_URL = "https://cardano-mainnet.blockfrost.io/api/v0"
LIMIT = 100

# Pools
def get_stake_pools() -> pd.DataFrame:
    """
    Get stake pools from Blockfrost
    ref: https://docs.blockfrost.io/#tag/Cardano-Pools/paths/~1pools/get

    @return: pd.DataFrame
    """
    # NOTE: using the /pools endpoint for more info
    url = f"{BASE_URL}/pools/extended"

    parameters = {
        "count": LIMIT,
        "page": 1,
    }

    response = requests.get(url, headers=HEADERS, params=parameters).json()
    df = pd.DataFrame(response)

    # start 5 minute timer
    start = time.time()
    while len(response) == LIMIT:
        # check timer
        if time.time() - start > 300:
            print("Timed out getting stake pools")
            break
        parameters["page"] += 1
        print(f"Getting page {parameters['page']}")
        response = requests.get(url, headers=HEADERS, params=parameters).json()
        df = pd.concat([df, pd.DataFrame(response)])

    # sort by active_stake
    df = df.sort_values(by="active_stake", ascending=False)
    return df

def dns_lookup(hostname):
    """
    Lookup DNS hostname

    @param hostname: str - hostname
    @return: str
    """
    if hostname is None:
        return None
    try:
        result = socket.gethostbyname(hostname)
        return result
    except socket.gaierror:
        return None

def get_pool_relays(pool_id: str) -> pd.DataFrame:
    """
    Get pool relays
    ref: https://docs.blockfrost.io/#tag/Cardano-Pools/paths/~1pools~1%7Bpool_id%7D~1relays/get

    @param pool_id: str - pool id
    @return: pd.DataFrame
    """
    print(f"Getting relays for pool {pool_id}")
    url = f"{BASE_URL}/pools/{pool_id}/relays"
    response = requests.get(url, headers=HEADERS).json()
    df = pd.DataFrame(response)

    df["pool_id"] = pool_id
    return df

def get_pools_relays(pool_ids: List[str]) -> pd.DataFrame:
    """
    Get pools relays

    @param pool_ids: List[str] - list of pool ids
    @return: pd.DataFrame
    """
    df = pd.DataFrame()
    total = len(pool_ids)
    count = 0
    for pool_id in pool_ids:
        count += 1
        print(f"Getting relays for pool {pool_id} ({count}/{total})")
        # NOTE: out of kindness for this team & their great free API, I won't go any faster
        time.sleep(0.1)  
        df = pd.concat([df, get_pool_relays(pool_id)])
    df["dns_ip"] = df["dns"].apply(dns_lookup)
    return df

def main() -> Dict:

    # Get pools & ids
    pools = get_stake_pools()
    pool_ids = pools["pool_id"].unique().tolist()
    
    # NOTE: trim list to speed up testing
    #pool_ids = pool_ids[:30]

    # use ids to get relays
    pool_relays = get_pools_relays(pool_ids)

    # join pools and relays on pool_id
    pools_relays = pd.merge(pools, pool_relays, on="pool_id")

    # Now we want ip to be the ip address of the relay
    # If dns_ip is not null, use that
    pools_relays["ip"] = pools_relays["dns_ip"]
    # If dns_ip is null, use ipv4
    pools_relays.loc[pools_relays["ip"].isnull(), "ip"] = pools_relays["ipv4"]
    # If ipv4 is null, use ipv6
    pools_relays.loc[pools_relays["ip"].isnull(), "ip"] = pools_relays["ipv6"]

    # Filter out pools with no ip
    pools_relays = pools_relays[~pools_relays["ip"].isnull()]
    # For each pool_id, select the first row
    pools_relays = pools_relays.groupby("pool_id").first().reset_index()

    # rename so we have a good column name for the ip
    rename = {
        "pool_id": "address",
        "active_stake": "stake",
    }
    pools_relays = pools_relays.rename(columns=rename)

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

    # select ip, stake, address
    pools_relays = pools_relays[["ip", "stake", "address"]]
    pools_relays["is_validator"] = True
    # Add extra_info column
    pool_relays['extra_info'] = {}

    # convert to dict
    validators_dict = {
        "timestamp": str(datetime.now().strftime("%m-%d-%Y_%H:%M")),
        "collection_method": "api",
        "chain_data": "",
        "nodes": pools_relays.set_index("ip").T.to_dict() 
        }

    return validators_dict

if __name__ == "__main__":
    validators_dict = main()

    # save to json
    today = datetime.today().strftime("%Y-%m-%d")
    with open(f'{OUTPUT_FOLDER}/cardano.json', 'w') as f:
        json.dump(validators_dict, f, indent=4)
    print(f"Done. Check {OUTPUT_FOLDER}")
