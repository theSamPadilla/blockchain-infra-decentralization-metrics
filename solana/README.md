# Solana Node Scraper
> forked from [theSamPadilla/solana-node-scraper](https://github.com/theSamPadilla/solana-node-scraper)

## Overview
This is a slimmed down version of the original tool built to analyze the infrastructure providers of all the nodes running on Solana.

This script analyzes the gossip nodes available on Solana and sorts them according to the format specified on `../README.md`.

---
## Requirements
- [Solana CLI](https://docs.solana.com/cli/install-solana-cli-tools)
- [Python](https://www.python.org/downloads/)
- Other dependencies in requirments.txt

---
## Usage
The scraper takes a `--help` optional parameters.

If the flag is not present, it will run the analysis and output a `solana.json` file according to the format specified on `../README.md`, at the `output` key in the `config/SettingsConfig.json`.

---
## Config Files
The tool takes one file to be placed under "/config":
1. **SettingsConfig.json** -> Defines the full path for the Solana CLI executable and output path.