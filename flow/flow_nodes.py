import base64
import json
import re
import subprocess
from datetime import datetime

import pandas as pd
import requests


def string_to_base64(string: str):
    """Converts a string to base64"""
    message_bytes = string.encode("ascii")
    base64_bytes = base64.b64encode(message_bytes)
    string_message = base64_bytes.decode("ascii")
    return string_message


def base64_to_string(res: str):
    """Converts a base64 string to a string"""
    res_bytes = base64.b64decode(res)
    res = res_bytes.decode("utf-8")
    return json.loads(res)


def run_script_flow(payload):
    """Runs a script on the flow blockchain"""
    url = "https://rest-mainnet.onflow.org/v1/scripts"
    res = requests.post(url, json=payload)
    if res.status_code == 200:
        res = res.json()
        return res
    print(res)
    raise


def get_id_nodes():
    """Returns a list of all the node ids"""
    script = """import FlowIDTableStaking from 0x8624b52f9ddcd04a

    // This script returns the current identity table length

    pub fun main(): [String] {
        return FlowIDTableStaking.getNodeIDs()
    }
    """

    script_message = string_to_base64(script)

    payload = {
        "script": script_message,
    }

    if response := run_script_flow(payload):
        return base64_to_string(response)


def get_node_info(node: dict):
    """Returns a dictionary with all the info about a node"""
    script = """import FlowIDTableStaking from 0x8624b52f9ddcd04a

    // This script gets all the info about a node and returns it

    pub fun main(nodeID: String): FlowIDTableStaking.NodeInfo {

        return FlowIDTableStaking.NodeInfo(nodeID: nodeID)
    }
    """

    dumped_node = json.dumps(node)

    script_message = string_to_base64(script)
    arguments_message = string_to_base64(dumped_node)

    payload = {
        "script": script_message,
        "arguments": [arguments_message],
    }

    if response := run_script_flow(payload):
        return base64_to_string(response)


def get_ip_address(address: str):
    """Returns the ip address of a node"""
    ping = subprocess.getoutput(f"ping -c 1 {address} ")
    id_pattern = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
    address = m.group() if (m := re.search(id_pattern, ping)) is not None else "Unknown"
    return address


def group_to_dict(group):
    """Converts a group of nodes to a dictionary"""
    return {
        group.iloc[0]["ip_address"]: {
            "is_validator": True,
            "stake": group["tokenStaked"].iloc[0],
            "address": group["networkingAddress"].iloc[0],
            "extra_info": {
                "id": group["id"].iloc[0],
                "role": group["role"].iloc[0],
                "networkingKey": group["networkingKey"].iloc[0],
                "stakingKey": group["stakingKey"].iloc[0],
                "tokensCommitted": group["tokensCommitted"].iloc[0],
                "tokensUnstaking": group["tokensUnstaking"].iloc[0],
                "tokensUnstaked": group["tokensUnstaked"].iloc[0],
                "tokensRewarded": group["tokensRewarded"].iloc[0],
                "delegators": group["delegators"].iloc[0],
                "delegatorIDCounter": group["delegatorIDCounter"].iloc[0],
                "tokensRequestedToUnstake": group["tokensRequestedToUnstake"].iloc[0],
                "initialWeight": group["initialWeight"].iloc[0],
            },
        }
    }


## Main ##
def main():
    id_node_raw = get_id_nodes()
    id_node_list = id_node_raw["value"]

    nodes = []

    print(f"Analyzing {len(id_node_list)} nodes...")
    for _ in id_node_list:
        nodes_fields = get_node_info(_)["value"]["fields"]

        nodes_data = {
            "id": nodes_fields[0]["value"]["value"],
            "role": nodes_fields[1]["value"]["value"],
            "networkingAddress": nodes_fields[2]["value"]["value"],
            "networkingKey": nodes_fields[3]["value"]["value"],
            "stakingKey": nodes_fields[4]["value"]["value"],
            "tokenStaked": nodes_fields[5]["value"]["value"],
            "tokensCommitted": nodes_fields[6]["value"]["value"],
            "tokensUnstaking": nodes_fields[7]["value"]["value"],
            "tokensUnstaked": nodes_fields[8]["value"]["value"],
            "tokensRewarded": nodes_fields[9]["value"]["value"],
            "delegators": nodes_fields[10]["value"]["value"],
            "delegatorIDCounter": nodes_fields[11]["value"]["value"],
            "tokensRequestedToUnstake": nodes_fields[12]["value"]["value"],
            "initialWeight": nodes_fields[13]["value"]["value"],
        }

        nodes.append(nodes_data)

    print("\tDone.")

    roles = {
        "3": "execution",
        "2": "consensus",
        "1": "collection",
        "4": "verification",
        "5": "access",
    }

    nodes_df = pd.DataFrame(nodes)

    print("\nou Transforming dataframe result. This may take several minutes...")
    nodes_df["role"] = nodes_df["role"].apply(lambda x: roles[x])
    nodes_df["ip_address"] = nodes_df["networkingAddress"].apply(
        lambda x: get_ip_address(x.split(":")[0])
    )

    print("\tDone.")
    result = nodes_df.groupby("ip_address").apply(group_to_dict).tolist()
    
    ## NOTE: we want this format output
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

    today = datetime.today().strftime("%Y-%m-%d")
    
    dict_result = {
        "timestamp": today,
        "collection_method": "api",
        "chain_data": {},
        "nodes": {list(node)[0]: node[list(node)[0]] for node in result}
    }

    with open(f"flow_output_{today}.json", "w") as f:
        json.dump(dict_result, f, indent=4, ensure_ascii=False)
        f.close()


if __name__ == "__main__":
    main()
