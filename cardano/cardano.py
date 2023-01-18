"""
Cardano nodes
ref: https://docs.blockfrost.io/
"""
from typing import List
import pandas as pd
import requests
import time

HEADERS = {
    "Content-Type": "application/json",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    # TODO: add secrets
    "project_id": "",
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


pools = get_stake_pools()
print(pools)
pools.to_csv("pools.csv", index=False)
pool_ids = pools["pool_id"].unique().tolist()


def get_pool_relays(pool_id: str) -> pd.DataFrame:
    """
    Get pool relays
    ref: https://docs.blockfrost.io/#tag/Cardano-Pools/paths/~1pools~1%7Bpool_id%7D~1relays/get

    @param pool_id: str - pool id
    @return: pd.DataFrame
    """
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
    return df


pool_relays = get_pools_relays(pool_ids)
print(pool_relays)
pool_relays.to_csv("pool_relays.csv", index=False)

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


