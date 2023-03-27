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
    "nodes": {
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
    }
}
```

## Usage
The tool takes 1 mandatory parameter and 2 optional parameters in the following format:

- **[MANDATORY]** `--blockchain=[value]` -> Defines the target blockchain. There must exist a file in the `json/` directory matching `[value]` (i.e. `[value].json`).

- `--providers=[val1],[val2]` -> Defines the providers for which to track nodes, based on the `config/ProviderConfig.json`.
    Only accepted values are the "short" attribute defined for each ASN in the `ProviderConfig.json`. See below for the format of the `ProviderConfig.json` file.

- `--countries=[val1],[val2]` -> Defines the countries for which to track nodes, based on the ISO Alpha-2 country code convention.
    Only accepted values are the ISO Alpha-2 country code. A table of each country code to its respective country can be found at `config/CountryConfig.json`.

- `--output` -> Prints an overview of the results upon completion.

- `--help` -> Prints this message.

## Things to note
1. Criteria for `active` in flow is defined by those nodes whose stake is lower than the minimum specified requirement for that node role - as per [Flow's documentation](https://developers.flow.com/nodes/node-operation/node-roles).

## Contributing and Supporting
**To Contribute:**
Check [contributing.md](contributing.md) and go at it. Feel free to fork and use for your own projects according to the Apache License too.

**To Support:**
- Follow [@theSamPadilla](https://twitter.com/thesampadilla), the author of the scraper, on Twitter :) 