# Solana Node Scraper

## Overview
This tool was built to analyze the infrastructure providers of all the nodes running on Solana and as an internal tool for our Google Cloud Digital Assets team to track our progress with the Solana community.

The tool tracks the infrastructure providers defined in the ProvidersConfig.json file and calculates metrics on:
- Total number of RPC nodes, validator nodes, and stake.
- Percentage of RPC nodes, validator nodes, and stake.

Optionally, the tool also takes a list of infrastructure providers and outputs a full lsit of all the nodes running on them.

This repo also contains a simple bash file to run the scraper and upload the files to a Google Cloud Storage Bucket. Crontask it and monitor the infrastructrue decentralization of Solana improve right in front of your eyes.

---
## Requirements
- [Solana CLI](https://docs.solana.com/cli/install-solana-cli-tools)
- [Python](https://www.python.org/downloads/)
- Other dependencies in requirments.txt

Run the script under the same relative directory structure of this repo.

---
## Usage
The scraper takes 4 optional parameters in the following format:

- `--exec.mode=[value]` -> Defines the execution method. Options are ("full" or "liveliness") Default is "full".
    - "full" mode runs a full analysis of all the gossip discoverable nodes.
    - "liveliness" checks only the liveliness state of nodes previously seen for the provider objects in "/memory"

- `--providers=[val1],[val2]` -> Defines the providers for which to track nodes, based on the config/ProviderConfig.json.
    Only accepted values are the "short" attribute defined for each ASN in the ProviderConfig.json. See below for the format of the ProviderConfig file.

- `--from.script` -> Sends the output files to upload/ for upload to GCS and silences runtime messages. Use recommended for bash scripts only.

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
- Check out the work we are doing at [Google Cloud Web3](https://cloud.google.com/web3). Reach out to our team if you have any questions.
- Follow [@theSamPadilla](https://twitter.com/thesampadilla), the author of the scraper, on Twitter :) 

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