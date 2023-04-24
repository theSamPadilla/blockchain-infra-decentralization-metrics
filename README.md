# Blockchain Infra Decentralization Metrics
This repo is a collection of scripts that measure the infrastructure decentralization of multiple blockchains.

This project measures:
- Stake distribution across infrastructure providers.
- Stake distribution across geographies.
- RPC nodes distribution across infrastructure providers
- RPC nodes distribution across geographies

## How it Works
The individual scripts inside each chain directory get/crawl the IP addresses of the validators and nodes, and finds their respective stake and other relevant information. Each script outputs the data for their chain to a JSON file inside the `json` folder in the root directory. That JSON file **must** follow the specification below. Some of the scripts or programs inside each directory may need some work, so contributions are welcomed.

The `main.py` script uses the JSON files for a given chain to find the infrastructure provider and the geographic location where each node is running.

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

- **[MANDATORY]** `--blockchain=[value]`
    - Defines the target blockchain.
    - There must exist a file in the `json/` directory matching `[value]` (i.e. `[value].json`).

- `--providers=[val1],[val2]`
    - Defines the providers for which to track nodes, based on the `config/ProviderConfig.json`.
    - Only accepted values are the "short" attribute defined for each ASN in the `ProviderConfig.json`.
        - The keys are ASN numbers for the providers you want to track.
        - The values have the provider name, description, website, and "short".

- `--countries=[val1],[val2]`
    - Defines the countries for which to track nodes, based on the ISO Alpha-2 country code convention.
    - Only accepted values are the ISO Alpha-2 country code. A table of each country code to its respective country can be found at `config/CountryConfig.json`.

- `--output` -> Prints an overview of the results upon completion.

- `--help` -> Prints this message.

## Things to note
1. Criteria for `active` in flow is defined by those nodes whose stake is lower than the minimum specified requirement for that node role - as per [Flow's documentation](https://developers.flow.com/nodes/node-operation/node-roles).
2. RPC node data is not available for all chains, and some stake data may be incomplete for some chains. See each chain's documentation for more information.
3. For chains in which the IPs were acquired via crawling, there is no way to guarantee that the crawler has found an exhaustive list of all the nodes in the network.
4. No IP data is found in this repo, just tools.

---
# Disclaimer & License
This is not an officially supported Google product.

Apache Header:
```
Copyright 2022 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```