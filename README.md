# Blockchain Infra Decentralization Metrics
This repo is a collection of scripts that measure the infrastructure decentralization of multiple blockchains.

This project measures:
- Stake distribution across infrastructure providers.
- Stake distribution across geographies.
- RPC nodes distribution across infrastructure providers*
- RPC nodes distribution across geographies*
**RPC node data is not available for all chains*

## How it Works
The individual scripts inside each chain directory gets/crawls the IP addresses of the validators and finds their respective stake and other relevant information. Each script outputs the data for their chain to a JSON file inside the `json` folder in the root directory. That JSON file **must** follow the specification below.

The `main.py` script uses the JSON files for a given to find the infrastructure provider and the geographic location where each node is running.

## JSON specification
The output should be a JSON objects in the following format:
```
{
    "timestamp": <str> # When was the analysis last ran
    "collection_method": <str>, <"crawl" for nodes manually crawled, or "api" for IPs found via the chain RPC API>
    "chain_data": {Any other information to add about the chain},
    "nodes": [
        <IP Address> : {
            "is_validator": <bool>, #Differentiate between RPC nodes and validator nodes.
            "stake": <int>, #Stake of the validator or null if RPC node.
            "address": <string>, #On-chain address of the validator.
            "extra_info": {
                <Any other info you want to add that may be useful in processing (validator name, skip rate, etc)>
            }
        },
        <IP Address 2> : {},
        <IP Address 3> : {},
        .
        .
    ]
}
```