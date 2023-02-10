# Blockchain Infra Decentralization Metrics
This repo is a collection of scripts that measure the infrastructure decentralization of multiple blockchains.

This project measures:
- Stake distribution across infrastructure providers.
- Stake distribution across geographies.
- RPC nodes distribution across infrastructure providers*
- RPC nodes distribution across geographies*
**RPC node data is not available for all chains*

## How it Works
The individual scripts inside each chain directory name looks/crawls the IP addresses of the validators and finds their respective stake. Each script outputs the data for their chain to a JSON file follwoing the specification below.
The main script then uses the JSON files to find the infrastructure provider and the geographic location where each validator is running for each chain.

## JSON specification
The output should be a JSON objects in the following format:
```
{
    "timestamp": <str> # When was the analysis last ran
    "chain_data": {Any other information to add about the chain and the collection method of IPs},
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