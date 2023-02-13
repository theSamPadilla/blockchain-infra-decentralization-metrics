# Solana Node Scraper
> forked from [theSamPadilla/solana-node-scraper](https://github.com/theSamPadilla/solana-node-scraper)

## Overview
This tool was built to analyze the infrastructure providers of all the nodes running on Solana.

The tool tracks the infrastructure providers defined in the ProvidersConfig.json file and calculates metrics on:
- Total number of RPC nodes, validator nodes, and stake.
- Percentage of RPC nodes, validator nodes, and stake.

Optionally, the tool also takes a list of infrastructure providers and outputs a full lsit of all the nodes running on them.

---
## Requirements
- [Solana CLI](https://docs.solana.com/cli/install-solana-cli-tools)
- [Python](https://www.python.org/downloads/)
- Other dependencies in requirments.txt

### Note:
This script can be ran independently to perform a final analysis of the Solana network, without having to use `../main.py`. You just need to update the `solana/config/SettingsConfig.json` to specify the desired output folder.

`main.py` at the root directory of this repo is a refactoring of this code.

---
## Usage
The scraper takes 3 optional parameters in the following format:

- `--exec.mode=[value]` -> Defines the execution method. Options are ("full" or "liveliness") Default is "full".
    - "full" mode runs a full analysis of all the gossip discoverable nodes.
    - "liveliness" checks only the liveliness state of nodes previously seen for the provider objects in "/memory"

- `--providers=[val1],[val2]` -> Defines the providers for which to track nodes, based on the config/ProviderConfig.json.
    Only accepted values are the "short" attribute defined for each ASN in the ProviderConfig.json. See below for the format of the ProviderConfig file.

- `--help` -> Prints this message.

---
## Config Files
The scraper takes two files to be placed under "/config":
1. **SettingsConfig.json** -> Defines the full path for the Solana CLI executable.
2. **ProvidersConfig.json** -> Defines the providers to track according to the following format:
    - The keys are [ASN numbers](https://www.bgplookingglass.com/list-of-autonomous-system-numbers) for the providers you want to track.
    - The values have the provider name, description, website, and "short". The "short" key is used when passing providers along with the --providers flag.

The tool comes pre-loaded with the ASNs for the top 10 infrastructure providers for Solana. If you want to track specific providers beyond that, you can use some of the *misc functions* below to find them.

### Misc Functions
Added at the bottom of the script, these functions are not used by the tool, but serve as a reference to get more infomation on the network ASNs.

1. `GetTopAsnDescriptions() -> description:count`
- Use it to get a sorted list of the all the ASNs descriptions for all the gosisp nodes in the network by how many times each appeared.
2. `GetAsnDescriptionMap() -> asn:description`
- Use it to get the ASN number provider and its description for all the unique ASNs seen in the network.

---
## Contributing and Supporting
**To Contribute:**
Check [contributing.md](contributing.md) and go at it. Feel free to fork and use for your own projects according to the Apache License too.

**To Support:**
- Follow [@theSamPadilla](https://twitter.com/thesampadilla), the author of the scraper, on Twitter :) 