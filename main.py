#!/usr/bin/python3
############################################
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
############################################
import sys, json, subprocess, os
import pickle
import ipwhois
from datetime import date, datetime
from ipwhois.net import Net #type: ignore
from ipwhois.asn import IPASN #type: ignore

## Load Settings ##
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
PROVIDER_CONFIG_PATH = BASE_DIR + "/config/ProviderConfig.json"

## Classes ##
class Blockchain:
    def __init__(self, target):
        self.target = target
        self.objectPath = "{base_dir}/memory/{target}/{target}_object.pickle".format(base_dir=BASE_DIR, target=target)
        self.totalStake = 0
        self.totalNodes = 0
        self.totalNonValidatorNodes = 0
        self.totalValidators = 0
        self.unidentifiedIPs = {}

        #Main Data Strucutre
        self.providersData = {"Other": {"Total Non-Validator Nodes": 0, "Total Validators": 0, "Total Nodes": 0, "Total Stake": 0}, "Unidentified": {"Total Non-Validator Nodes": 0, "Total Validators": 0, "Total Nodes": 0, "Total Stake": 0}} #*Data on rpc, validators, and stake per main provider.
        
        #Set object creation date and analysis date
        self.objectCreationDate = date.today().strftime("%m-%d-%Y")
        self.analysisDate = date.today().strftime("%m-%d-%Y") # will get overwritten by the timestamp in the JSON

    def Save(self):
        #Write object binary to the file
        print("\tSaving %s object." % self.target, flush=True)
        os.makedirs(os.path.dirname(self.objectPath), exist_ok=True)
        with open(self.objectPath, "wb") as f:
            pickle.dump(self, f)
            f.close()
        print("\tDone.", flush=True)

    def CalculatePercentages(self, target_ips):
        print("\tCalculating Provider Percentages.", flush=True)
        for provider in self.providersData:
            stake = self.providersData[provider]["Total Stake"]
            rpc = self.providersData[provider]["Total Non-Validator Nodes"]
            validators = self.providersData[provider]["Total Validators"]
            total = self.providersData[provider]["Total Nodes"]

            self.providersData[provider]["Percentage of Total Stake"] = stake * 100 / self.totalStake
            if self.totalNonValidatorNodes: self.providersData[provider]["Percentage of Non-Validator Nodes"] = rpc * 100 / self.totalNonValidatorNodes
            self.providersData[provider]["Percentage of Validators"] = validators * 100 / self.totalValidators
            self.providersData[provider]["Percentage of Total Nodes"] = total * 100 / self.totalNodes
        print("\tDone.", flush=True)

    def SaveProviderDistribution(self):
        path = "{base}/{output}/{target}/network/ProviderDistribution_{time}.json".format(base=BASE_DIR, output=OUTPUT_FOLDER, target=self.target, time=str(datetime.now().strftime("%m-%d-%Y_%H:%M")))
        to_write = {
            'Analysis Date': self.analysisDate,
            'Total Nodes': self.totalNodes,
            'Total Non-Validator Nodes': self.totalNonValidatorNodes,
            'Total Validator Nodes': self.totalValidators,
            'Total stake': self.totalStake,
            'Provider Distribution': self.providersData
        }

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(to_write, f, indent=4, default=str)
            f.close()
    
class Provider:
    def __init__(self, short, provider, target_chain):
        #Info
        self.short = short
        self.provider = provider
        self.target_chain = target_chain
        self.analysisDate = date.today().strftime("%m-%d-%Y") #This will get overwritten by the timestamp in the JSON file
        self.objectPath = "{base}/memory/{target_chain}/providers/{short}_object.pickle".format(base=BASE_DIR, target_chain=target_chain, short=short)

        #Counts
        self.validatorCount = 0
        self.nonValidatorNodeCount = 0
        self.cumulativeStake = 0
        self.nodeDict = {} #*{IP:{key, extra data}}

        #Historic Data
        self.objectCreationDate = date.today().strftime("%m-%d-%Y")
        
    def SaveProviderNode(self, ip: str, node_info: dict):   
        #Save only new ndoes
        if ip not in self.nodeDict:

            #Check if the IP is a validator
            if node_info["is_validator"]:
                self.validatorCount += 1
                if not node_info['stake']:
                    stake = 0
                else:
                    stake = int(node_info['stake'])
                self.cumulativeStake += stake
            
            #Non validator node
            else:
                self.nonValidatorNodeCount += 1
                stake = None

            #Save data to object
            self.nodeDict[ip] = {
                "Address": node_info["address"],
                "Is Validator": node_info["is_validator"],
                "Stake": stake,
                "Validator Info": node_info["extra_info"]
            }

    def Save(self):
        # Update analysis date before saving the object
        self.analysisDate = BLOCKCHAIN_OBJ.analysisDate
        
        print("\tSaving %s object" % self.provider, flush=True)      
        os.makedirs(os.path.dirname(self.objectPath), exist_ok=True)
        with open(self.objectPath, "wb") as f:
            pickle.dump(self, f)
            f.close()
        print("\tDone.", flush=True)

    def SaveNodeJSONInfo(self):
        path = "{base}/{output}/{target}/providers/{provider}_Nodes_{time}.json".format(base=BASE_DIR, output=OUTPUT_FOLDER, target=self.target_chain, provider=self.provider, time=str(datetime.now().strftime("%m-%d-%Y_%H:%M")))
        to_write = {
            'Analysis Date': self.analysisDate,
            'Total Nodes': len(self.nodeDict),
            'Validator Nodes': self.validatorCount,
            'Non-Validator Nodes': self.nonValidatorNodeCount,
            'Monitoring since date': self.objectCreationDate,
            'Analysis Date': date.today().strftime("%m-%d-%Y"),
            'Cumulative stake': self.cumulativeStake,
            'Percentage of total stake': (self.cumulativeStake * 100) / BLOCKCHAIN_OBJ.totalStake, 
            'Nodes': self.nodeDict
        }

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(to_write, f, indent=4, default=str)
            f.close()

## Main ##
def main(target_blockchain, providers_to_track):
    print("\n-----RUNTIME-----")
    
    #Make target blockchain (global) and provider objects if providers_to_track not empty
    MakeTargetBlockchainObject(target_blockchain)
    short_to_object_map = {}
    if providers_to_track:
        short_to_object_map = MakeProviderObjects(providers_to_track, target_blockchain)

    #Analyze all nodes for provided blockchain
    GetNetworkProviderDistribution(providers_to_track, short_to_object_map, target_blockchain)

    #Save objects
    print("\n\nSaving Objects...", flush=True)
    BLOCKCHAIN_OBJ.Save()
    for obj in short_to_object_map.values():
        obj.Save()
    print("Done.", flush=True)

    #Save the node JSON
    print("\n\nOutputting information to JSON files...")
    for obj in short_to_object_map.values():
        obj.SaveNodeJSONInfo()
    BLOCKCHAIN_OBJ.SaveProviderDistribution()
    print("Done.", flush=True)

    #Output results flag passed
    if OUTPUT_MESSAGE:
        PrintCompletion(short_to_object_map, target_blockchain)

## Helper Functions ##
def MakeTargetBlockchainObject(target_blockchain):
    global BLOCKCHAIN_OBJ

    #Set paths
    p = "{base}/memory/{target}/blockchain_object.pickle".format(base=BASE_DIR, target=target_blockchain)
    
    #First time creating the object.
    if not os.path.exists(p):
        print("Building %s object for the first time." % target_blockchain, flush=True)
        BLOCKCHAIN_OBJ = Blockchain(target_blockchain)
        print("Done.", flush=True)
    
    #Loading from memory
    else:
        print("Fetching %s object from memory..." % target_blockchain, flush=True)
        with open(p,'rb') as f:
            BLOCKCHAIN_OBJ = pickle.load(f)
            f.close()

        BLOCKCHAIN_OBJ.providersData = {"Other": {"Total RPC Nodes": 0, "Total Validators": 0, "Total Stake": 0}}

    return

def MakeProviderObjects(providers_to_track: dict, target_blockchain: str) -> dict:
    short_to_object_map = {} #* short -> provider object

    print("\n\nBuilding provider objects...", flush=True)

    for short in providers_to_track:
        #Set path and provider name
        path = "{base}/memory/{target}/{short}_object.pickle".format(base=BASE_DIR, target=target_blockchain, short=short)
        name = providers_to_track[short]

        #First time creating the object.
        if not os.path.exists(path):
            print("\tBuilding provider object for %s provider the first time." % name, flush=True)
            obj = Provider(short, name, target_blockchain)
            print("\tDone.", flush=True)

        #Loading from memory
        else:
            print("\tFetching provider object for %s from memory..." % name, flush=True)
            with open(path,'rb') as f:
                obj = pickle.load(f)
                f.close()
            print("\tDone.", flush=True)

        #Append object to list
        short_to_object_map[short] = obj

    return short_to_object_map

def GetNetworkProviderDistribution(providers_to_track: dict, short_to_object_map: dict, target_blockchain: str):
    #Get IP address JSON file
    path = "json/{target}.json".format(target=target_blockchain)
    with open(path, "r") as f:
        json_analysis = json.load(f)
        f.close()

    # Update blockchain object analysisDate
    BLOCKCHAIN_OBJ.analysisDate = json_analysis["timestamp"] #This is purely for human-readability, no need to be date type.
    target_ips = json_analysis["nodes"]

    print("\n\nAnalyzing %d Nodes. This may take a few minutes..." % len(target_ips), flush=True)

    #Iterate over all IP addresses
    for ip, node_info in target_ips.items():
        #!TODO
        """Build a catch for reverse DNS lookups"""
        
        #Nest the Network object building in a try/except
        try:
            #Build Network objects and set variables
            net = Net(ip)
            obj = IPASN(net)
            results = obj.lookup()
            asn = results['asn']
            provider_name = "Other" #Set provider name as Other. Will get overwritten for relevant providers defined in the file
        except Exception as e:
            #Capture unespecified IPs and set None asn
            BLOCKCHAIN_OBJ.unidentifiedIPs[ip] = target_ips[ip]
            print("\t[WARN] - Undefined IP: %s for %s" % (e, ip), flush=True)
            asn = None
            provider_name = "Unidentified"
        
        #If the ASN is in the ASN lookup, overwrite provider
        if asn in PROVIDER_ASN_LOOKUP:
            provider_name = PROVIDER_ASN_LOOKUP[results['asn']]['provider']
            
            #Create entry if provider hasn't yet been seen
            if provider_name not in BLOCKCHAIN_OBJ.providersData:
                BLOCKCHAIN_OBJ.providersData[provider_name] = {
                    "Total Non-Validator Nodes": 0,
                    "Total Validators": 0,
                    "Total Nodes": 0,
                    "Total Stake": 0
                }

            #Catch the providers_to_track nodes and save them to the object
            if provider_name in providers_to_track.values():
                short = list(providers_to_track.keys())[list(providers_to_track.values()).index(provider_name)]
                short_to_object_map[short].SaveProviderNode(ip, node_info)

        #If it is validator (eve if unidentified), sum validator and stake to provider dict and blockchain object.
        if node_info["is_validator"]:
            if not node_info["stake"]: #Catch null stake entries for validators
                stake = 0
            else:
                stake = int(node_info["stake"])
            BLOCKCHAIN_OBJ.providersData[provider_name]['Total Validators'] += 1
            BLOCKCHAIN_OBJ.providersData[provider_name]['Total Stake'] += stake
            BLOCKCHAIN_OBJ.totalStake += stake
            BLOCKCHAIN_OBJ.totalValidators += 1
        
        #Else just sum RPC to provider dict and blockchain object
        else:
            BLOCKCHAIN_OBJ.providersData[provider_name]['Total Non-Validator Nodes'] += 1
            BLOCKCHAIN_OBJ.totalNonValidatorNodes += 1

        #Add another node to the network and to the provider
        BLOCKCHAIN_OBJ.totalNodes += 1
        BLOCKCHAIN_OBJ.providersData[provider_name]['Total Nodes'] += 1

    #Calculate the percentages after a full analysis
    BLOCKCHAIN_OBJ.CalculatePercentages(target_ips)

    print("Done.", flush=True)


## Usage Functions ##
def PrintCompletion(short_to_object_map, target):   
    print("\n\n\n-----RESULTS for %s-----" % target.upper())
    
    if not short_to_object_map.values():
        print("\nNo providers to track specified.")
    else:
        print("\nProvider Overview:")
        for obj in short_to_object_map.values():
            print("\n%s:" % obj.provider)
            print("\tMonitoring since %s" % (obj.objectCreationDate))
            print("\tThere are", obj.validatorCount, "VALIDATORS running on %s." % obj.provider)
            print("\tThere have been", len(obj.nodeDict), "different nodes (IPs) seen running on %s since the start of this monitoring." % obj.provider)
    
    print("\n\nThere is a total of %d IPs seen on %s" % (BLOCKCHAIN_OBJ.totalNodes, target))
    print("There is a total of %d validator nodes on %s" % (BLOCKCHAIN_OBJ.totalValidators, target))
    print("%d IPs could not be identified on %s" % (len(BLOCKCHAIN_OBJ.unidentifiedIPs), target))
    print("\nCheck output files in output dir, farewell")

def PrintUsage():
    print("\n-----USAGE-----")
    print("Welcome to the Blockchain Infra Analytics Tool. This tool analyzes the number",
        "of nodes of each provider specified in the PorviderLookup.json file, for a specified chain in the command line")

    print("\n\n-----PARAMETERS-----")
    print("The tool takes 1 mandatory parameter and 3 optional parameters in the following format:")
    print("\n>[MANDATORY] --blockchain=<value> -> Defines the target blockchain to analyze. Value must exist in the `json/` directory without the \".json\" extension.")
    print("\n> --providers=<val1>,<val2> -> Defines the providers for which to track nodes, based on the config/ProviderConfig.json and following",
        "the format defined on the README. Default is None.")
    print("\n> --output -> Prints an overview of the results upon completion.")
    print("\n> --help -> Prints this message.")

    print("\n\n-----OUTPUT-----")
    print("The tool will build one file: \"output/<target_chain>/network/ProviderDistribution-<date>.json\" containing the infrasturcure analysis of the chain.")
    print("If \"--providers\" is specified, the tool will build a provider-<date>.json for every provider specified under \"output/<target_chain>/providers/\", containing a list of all nodes running on that provider.")

    print("\nFor a full description, see the README.md\n")

    exit(0)
        
def GetArguments(args: list) -> tuple:
    #Print usage and exit
    if "--help" in args:
        PrintUsage()
            
    #Disregard the first arg (filename)
    args.pop(0)

    #Set arg constraints
    allowed_blockchains = GetBlockchainNames()
    if "--blockchain" not in ''.join(args):
        print("ERROR: Missing mandatory \"--blockchain\" flag.")
        print("\tValid values are:", allowed_blockchains)
        exit(1)
    
    allowed_commands = {"--providers", "--blockchain", "--output", "--help"}
    allowed_providers = LoadConfigFileAndGetAllowedProviders()

    #Set global output folder and flag
    global OUTPUT_FOLDER, OUTPUT_MESSAGE
    OUTPUT_FOLDER = "results/"
    OUTPUT_MESSAGE = False
    if "--output" in ''.join(args):
        OUTPUT_MESSAGE = True
        args.remove("--output")
    
    #Initialize list of providers to track
    providers_to_track = {} #* short -> provider_name

    #Get commands and values
    for arg in args:
        buff = arg.split("=")

        #Check for good format
        if len(buff) != 2:
            print("ERROR: The argument %s has the wrong format." % arg)
            print("\tValid format is: \"--<argument>=<value>\"")
            exit(1)

        #Unpack command and value
        command, value = buff[0], buff[1]

        #Check that command is supported
        if command not in allowed_commands:
            print("ERROR: The argument %s is not supported." % command)
            print("\tValid arguments are:", allowed_commands)
            exit(1)

        #Target blockchain
        if command == "--blockchain":
            #Check for allowed blockchain
            if value not in allowed_blockchains:
                print("ERROR: There is no file named %s.json in the `json/` folder. Can't perform analysis." % value)
                print("\tValid values are:", allowed_blockchains)
                exit(1)
            else:
                target_blockchain = value

        #Providers
        elif command == "--providers":
            providers = value.split(",")
        
            #Check for valid providers
            for short in providers:
                short = short.upper()
                if short not in allowed_providers:
                    print("ERROR: Wrong format or the provider %s is not a valid provider." % short)
                    print("\tThe expected format is --providers=<val1>,<val2>,... (no spaces between values)")
                    print("\tValid providers, based on the config file, are:", list(allowed_providers.keys()))
                    exit(1)

                #Add to list
                else:
                    providers_to_track[short] = allowed_providers[short]

    return target_blockchain, providers_to_track


## Load Functions ##
def LoadConfigFileAndGetAllowedProviders() -> list:
    """Loads providers from ProvidersConfig.json file"""
    global PROVIDER_ASN_LOOKUP
    
    #Set the provider ASN lookup from the provider config file
    with open(PROVIDER_CONFIG_PATH, "r") as f:
        PROVIDER_ASN_LOOKUP = json.load(f)
        f.close()
    
    #Get allowed provider set
    allowed_providers = {} #*short.upper() -> provider_name
    for provider in PROVIDER_ASN_LOOKUP.values():
        if "short" in provider:
            allowed_providers[provider['short'].upper()] = provider["provider"]

    return allowed_providers

def GetBlockchainNames() -> list:
    """Gets the possible parameters for the `--blockchain` argument from the `json/` folder"""
    files = os.listdir("json/")
    files.remove("sample.json")
    return [i[:-5] for i in files]

## Main Caller ##
if __name__ == "__main__":
    if len(sys.argv) > 4:
        print("ERROR: Too many parameters.\n")
        PrintUsage()
    else:
        exec_mode, providers_to_track = GetArguments(sys.argv)
        main(exec_mode, providers_to_track)