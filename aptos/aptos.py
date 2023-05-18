import subprocess, json, socket
from datetime import datetime

def treatIP(ip: str) -> str:
    splitted = ip.split("/")
    #Check if ipv4
    if splitted[1] == "ip4":
        return splitted[2], None
    
    #Else resolve dns and return resolved
    elif splitted[1] == "dns":
        hostname = splitted[2]
        try:
            result = socket.gethostbyname(hostname)
            return result, hostname
        except Exception as e:
            print(f"Error processing address {splitted[2]}. Unrecognized (ip or dns) at {splitted[1]}")
            print(f"Error {e}. Panicking!")
            exit(0)

def main():
    # Execute subprocess command
    command = ['aptos', 'node', 'show-validator-set', '--url', 'https://mainnet.aptoslabs.com']
    result = subprocess.run(command, capture_output=True, text=True)

    # Check if the subprocess command was successful
    if result.returncode != 0:
        print(f"Error processing command. Make sure the aptos CLI is installed and accessible via the PATH variable.")
        exit(0)

    # Capture the JSON result
    json_result = json.loads(result.stdout)

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

    ip_dict = {}

    print("Processing Aptos IPs, this may take a few minutes...", flush=True)
    n = len(json_result["Result"]["active_validators"])
    i = 0

    # Iterate over the JSON result and cast into desired format
    for validator in json_result["Result"]["active_validators"]:
        print(f"\tProcessing Validator... [{i}/{n}]", flush=True)
        #Check there exists at least one address
        if not validator["config"]["validator_network_addresses"]:
            print("\nNo IP address for the validator.")
            print("Panicking!")
            exit(0)
        ip = validator["config"]["validator_network_addresses"][0]
        stake = float(validator["consensus_voting_power"]) / 100000000
        address = validator["account_address"]
        index = validator["config"]["validator_index"]

        #Check for fullnode IP
        if validator["config"]["fullnode_network_addresses"]:
            fullnode = validator["config"]["fullnode_network_addresses"][0]
            fullnode = treatIP(fullnode)
        else:
            fullnode = ""
        pubkey = validator["config"]["consensus_public_key"]
        
        #Treat validator ip
        ip, domain = treatIP(ip)

        #Add to ip dict
        ip_dict[ip] = {
            "is_validator": True,
            "stake": stake,
            "address": address,
            "extra_info": {"domain name": domain, "validator_index": index, "fullnode_address": fullnode, "consensus_pubkey": pubkey}
        }

        i += 1

    # Get output folder and write final resutl
    with open("config/SettingsConfig.json", "r") as f:
        buff = json.load(f)
        OUTPUT_FOLDER = buff["output_folder"]
        f.close()
    
    validators_dict = {
        "timestamp": str(datetime.now().strftime("%m-%d-%Y_%H:%M")),
        "collection_method": "cli",
        "chain_data": "Decimal: 8",
        "nodes": ip_dict
        }

    with open(f'{OUTPUT_FOLDER}/aptos.json', 'w') as f:
        json.dump(validators_dict, f, indent=4)
    print(f"\nDone. Check {OUTPUT_FOLDER}")

if __name__ == '__main__':
    main()
