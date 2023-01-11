#!/usr/bin/python3
############################################
# Copyright 2022 Google LLC
#
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
import sys, json, subprocess, requests, os
import pickle
import ipwhois
from datetime import date, datetime
from ipwhois.net import Net #type: ignore
from ipwhois.asn import IPASN #type: ignore

## Load Settings ##
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
PROVIDER_CONFIG_PATH = BASE_DIR + "/config/ProviderConfig.json"
with open(BASE_DIR + "/config/SettingsConfig.json", "r") as f:
    SOL_CLI_PATH = json.load(f)["sol_cli"]
    f.close()

## Classes ##
class SolanaCLI:
    apiEndpoint = 'https://api.mainnet-beta.solana.com'
    requestHeader = {'Content-Type': 'application/json'}
    
    def __init__(self):
        self.objectPath = BASE_DIR + "/memory/SOL_object.pickle"
        self.totalStake = 0

        #Main Data Strucutres
        self.providersData = {"Other": {"Total RPC Nodes": 0, "Total Validators": 0, "Total Stake": 0}} #*Data on rpc, validators, and stake per main provider.
        
        #Placeholder Data Structures for commands/request outputs
        self.gossipLookup = {} #*Lookup optimized response of Gossip {IP->{info}}
        self.validatorInfoLookup = {} #*Lookup optimized output of Validator Info Get {pubkey->{info}}
        self.validatorsLookup = {} #*Lookup optimized output of Validators {pubkey->{info}}
        
        #Run Gossip and Validators and set epoch
        self.SetEpoch()
        self.GetGossip()
        self.RunValidators()
        self.RunValidatorInfo()

        #Set object creation
        self.objectCreationEpoch = self.epoch
        self.objectCreationDate = date.today().strftime("%m-%d-%Y")

    #API call
    def GetGossip(self):
        print("\tGetting Solana Gossip Nodes.", flush=True)
        
        #Get gossip from API call
        data = {"jsonrpc":"2.0", "id":1, "method":"getClusterNodes"}
        result = requests.post(self.apiEndpoint, headers=self.requestHeader, json=data)

        #Fail missed requests gracefully
        if result.status_code != 200:
            raise("\n\n[FATAL] Solana Gossip API Request Failed. Try again later")
        
        #Optimize the result for faster lookups
        buff = result.json()['result'] 
        for node in buff:
            ip = node.pop('gossip').split(":")[0] #*Pops element, gets only IP portion
            self.gossipLookup[ip] = node

        #Done
        print("\tDone.", flush=True)
    
    #Solana CLI
    def RunValidators(self):
        print("\tRunning Solana Validators.", flush=True)
        
        #Run the solana gossip subprocess
        result = subprocess.run([SOL_CLI_PATH, "validators", "--output", "json"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        #Get current stake (disregard delinquent stake) and optimize the result for faster lookups
        buff = json.loads(result.stdout)
        self.totalStake = buff['totalCurrentStake'] / 1000000000
        for val in buff['validators']:
            pubkey = val.pop('identityPubkey')
            self.validatorsLookup[pubkey] = val
        
        #Done
        print("\tDone.", flush=True)

    #Solana CLI
    def RunValidatorInfo(self):
        print("\tRunning Solana Validator Info.", flush=True)
        
        #Run the solana gossip subprocess
        result = subprocess.run([SOL_CLI_PATH, "validator-info", "get", "--output", "json"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        #Optimize the result for faster lookups
        buff = json.loads(result.stdout)
        for val in buff:
            self.validatorInfoLookup[val['identityPubkey']] = val['info']
        
        #Done
        print("\tDone.", flush=True)

    # Helper Methods #
    def GetValidatorInfo(self, pubkey: str):
        validatorInfo = {}

        #Get default info if it exists
        if pubkey in self.validatorInfoLookup:
            validatorInfo['details'] = self.validatorInfoLookup[pubkey]

        #Get extra data
        validatorInfo['stake'] = float(self.validatorsLookup[pubkey]['activatedStake']) / 1000000000 #*Transforming from lamports
        validatorInfo['voteAccountPubkey'] = self.validatorsLookup[pubkey]['voteAccountPubkey']
        validatorInfo['commission'] = self.validatorsLookup[pubkey]['commission']
        validatorInfo['version'] = self.validatorsLookup[pubkey]['version']
        validatorInfo['isDelinquent'] = self.validatorsLookup[pubkey]['delinquent']
        validatorInfo['skipRate'] = self.validatorsLookup[pubkey]['skipRate']

        return validatorInfo

    def SetEpoch(self):
        #Make call
        data = {"jsonrpc":"2.0","id":1, "method":"getEpochInfo"}
        result = requests.post(self.apiEndpoint, headers=self.requestHeader, json=data)

        #Fail missed requests gracefully
        if result.status_code != 200:
            raise("\n\n[FATAL] Solana getEpochInfo API Request Failed. Try again later")

        #Return epoch
        self.epoch = result.json()['result']['epoch']
    
    def Save(self):
        #Write object binary to the file
        print("\tSaving SOL object.", flush=True)
        with open(self.objectPath, "wb") as f:
            pickle.dump(self, f)
            f.close()
        print("\tDone.", flush=True)

    def CalculatePercentages(self):
        print("\tCalculating Provider Percentages.", flush=True)
        for provider in self.providersData:
            stake = self.providersData[provider]["Total Stake"]
            rpc = self.providersData[provider]["Total RPC Nodes"]
            validators = self.providersData[provider]["Total Validators"]

            self.providersData[provider]["Percentage of Total Stake"] = stake * 100 / self.totalStake
            self.providersData[provider]["Percentage of RPC Nodes"] = rpc * 100 / len(self.gossipLookup)
            self.providersData[provider]["Percentage of Validators"] = validators * 100 / len(self.validatorsLookup)
        print("\tDone.", flush=True)

    def SaveProviderDistribution(self):
        path = BASE_DIR + "/" + OUTPUT_FOLDER + "/network/SolanaProviderDistribution_" + str(datetime.now().strftime("%m-%d-%Y_%H:%M")) + ".json"
        to_write = {
            'Total Nodes': len(self.gossipLookup),
            'Validator Nodes': len(self.validatorsLookup),
            'Current Epoch': self.epoch,
            'Total stake': self.totalStake,
            'Provider Distribution': self.providersData
        }

        with open(path, "w") as f:
            json.dump(to_write, f, indent=4, default=str)
            f.close()

    @classmethod
    def GetNodeBalance(cls, pubkey: str):
        #Implemented as a subprocess to avoid API rates
        result = subprocess.run([SOL_CLI_PATH, "balance", pubkey], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        #Return the result as a float -> convert from lamport to SOL
        return float(result.stdout.strip(' SOL\n'))

class Provider:
    def __init__(self, short, provider):
        #Info
        self.short = short
        self.provider = provider
        self.objectPath = BASE_DIR + "/memory/" + short + "_object.pickle"
        
        #Counts
        self.validatorCount = 0
        self.liveNodeCount = 0
        self.cumulativeStake = 0
        self.nodeDict = {} #*{IP:{key, extra data}}
        self.ipRangesLookup = {} #Optimized for lookups -> {range -> info}

        #Historic Data
        self.objectCreationDate = date.today().strftime("%m-%d-%Y")
        self.objectCreationEpoch = SOL_OBJ.epoch
        self.ipListCreationDate = date.today().strftime("%m-%d-%Y")
        
    def UpdateNodeLiveliness(self):
        print("\tChecking liveliness of %s nodes..." % self.provider, flush=True)
        
        for ip in self.nodeDict:
            #Was live and not in gossip -> Deactivate
            if self.nodeDict[ip]['Is Live'] and ip not in SOL_OBJ.gossipLookup:
                self.nodeDict[ip]['Is Live'] = False
                self.nodeDict[ip]['Earliest Deactivation'] = SOL_OBJ.epoch
                self.liveNodeCount -= 1
                
                #Substract CURRENT stake & decrease validator count if validator
                if self.nodeDict[ip]['Is Validator']:
                    self.validatorCount -= 1
                    self.cumulativeStake -= self.nodeDict[ip]['Validator Info']['stake']

            #Was not live and is now in gossip -> Reactivate
            elif not self.nodeDict[ip]['Is Live'] and ip in SOL_OBJ.gossipLookup:
                del self.nodeDict[ip]['Earliest Deactivation']
                self.nodeDict[ip]['Is Live'] = True
                self.nodeDict[ip]['Earliest Reactivation'] = SOL_OBJ.epoch
                self.liveNodeCount += 1

                #Add LATEST stake & increment validator count if validator
                if self.nodeDict[ip]['Is Validator']:
                    pubkey = self.nodeDict[ip]['Pubkey']
                    self.validatorCount += 1
                    self.cumulativeStake += (float(SOL_OBJ.validatorsLookup[pubkey]['activatedStake']) / 1000000000)
        
        print("\tDone.", flush=True)

    def SaveProviderNode(self, ip: str, pubkey: str, isValidator: bool):   
        #Save only new ndoes
        if ip not in self.nodeDict:
            validatorInfo = {}

            #Check if the IP is a validator
            if isValidator:
                validatorInfo = SOL_OBJ.GetValidatorInfo(pubkey=pubkey)
                self.validatorCount += 1
                self.cumulativeStake += validatorInfo['stake']

            #Save data to object
            self.liveNodeCount += 1
            self.nodeDict[ip] = {
                "Pubkey": pubkey,
                "Sol Balance": SolanaCLI.GetNodeBalance(pubkey=pubkey),
                "Oldest epoch seen": SOL_OBJ.epoch,
                "Is Live": True,
                "Is Validator": isValidator,
                "Validator Info": validatorInfo
            }

    def Save(self):
        print("\tSaving %s object" % self.provider, flush=True)
        with open(self.objectPath, "wb") as f:
            pickle.dump(self, f)
            f.close()
        print("\tDone.", flush=True)

    def SaveNodeJSONInfo(self):
        path = BASE_DIR + "/" + OUTPUT_FOLDER + "/providers/" + self.provider + "_Nodes_" + str(datetime.now().strftime("%m-%d-%Y_%H:%M")) + ".json"
        to_write = {
            'Live Nodes': self.liveNodeCount,
            'Validator Nodes': self.validatorCount,
            'Total different nodes seen': len(self.nodeDict),
            'Monitoring since date': self.objectCreationDate,
            'Monitoring since epoch': self.objectCreationEpoch,
            'Current epoch': SOL_OBJ.epoch,
            'Cumulative stake': self.cumulativeStake,
            'Percentage of total stake': (self.cumulativeStake * 100) / SOL_OBJ.totalStake, 
            'Nodes': self.nodeDict
        }

        with open(path, "w") as f:
            json.dump(to_write, f, indent=4, default=str)
            f.close()

## Main ##
def main(exec_mode, providers_to_track):
    print("\n-----RUNTIME-----")
    
    #Make SOL Object (global) and provider objects if providers_to_track not empty
    MakeSolanaObject()
    short_to_object_map = {}
    if providers_to_track:
        short_to_object_map = MakeProviderObjects(providers_to_track, exec_mode)

    #Analyze all nodes if full execution mode
    if exec_mode == "full":
        GetNetworkProviderDistribution(providers_to_track, short_to_object_map)

    #Check Liveliness of specified stored nodes.
    print("\n\nChecking Liveliness of Saved Nodes...", flush=True)
    for obj in short_to_object_map.values():
        obj.UpdateNodeLiveliness()
    print("Done.", flush=True)

    #Save objects
    print("\n\nSaving Objects...", flush=True)
    SOL_OBJ.Save()
    for obj in short_to_object_map.values():
        obj.Save()
    print("Done.", flush=True)

    #Save the node JSON
    print("\n\nOutputting information to JSON files...")
    for obj in short_to_object_map.values():
        obj.SaveNodeJSONInfo()
    SOL_OBJ.SaveProviderDistribution()
    print("Done.", flush=True)

    #Output results if called from CLI
    if OUTPUT_FOLDER == "output/":
        PrintCompletion(short_to_object_map)

## Helper Functions ##
def MakeSolanaObject():
    global SOL_OBJ

    #Set paths
    psol = BASE_DIR + "/memory/SOL_object.pickle"
    
    #First time creating the object.
    if not os.path.exists(psol):
        print("Building Solana CLI object for the first time.", flush=True)
        SOL_OBJ = SolanaCLI()
        print("Done.", flush=True)
    
    #Loading from memory
    else:
        print("Fetching Solana CLI object from memory...", flush=True)
        with open(psol,'rb') as fsol:
            SOL_OBJ = pickle.load(fsol)

        #Update Gossip, Validators, Validator Info, Epoch, and clear provider object
        SOL_OBJ.SetEpoch()
        SOL_OBJ.GetGossip()
        SOL_OBJ.RunValidators()
        SOL_OBJ.RunValidatorInfo()
        SOL_OBJ.providersData = {"Other": {"Total RPC Nodes": 0, "Total Validators": 0, "Total Stake": 0}}

    return

def MakeProviderObjects(providers_to_track: dict, exec_mode: str):
    short_to_object_map = {} #* short -> provider object

    print("\n\nBuilding provider objects...", flush=True)

    for short in providers_to_track:
        #Set path and provider name
        path = BASE_DIR + "/memory/" + short + "_object.pickle"
        name = providers_to_track[short]

        #First time creating the object.
        if not os.path.exists(path):
            #Only make objects if execution mode is full. Else print warning and skip.
            if exec_mode != "full":
                print("Warning: \"%s\" does not exist. Can only create objects on \"full\" mode." % path, flsuh=True)
                print("\tWill attempt to load other provider objects (if any).", flush=True)
            else:
                print("\tBuilding provider object for %s provider the first time." % name, flush=True)
                obj = Provider(short, name)
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

def GetNetworkProviderDistribution(providers_to_track: dict, short_to_object_map: dict):
    print("\n\nAnalyzing Gossip Nodes. This may take a few minutes...", flush=True)
    
    #Iterate over all gossipNodes
    for ip, node in SOL_OBJ.gossipLookup.items():
        #Nest the Network object building in a try/except
        try:
            #Build Network objects and set variables
            net = Net(ip)
            obj = IPASN(net)
            results = obj.lookup()
            asn = results['asn']
        except ipwhois.exceptions.IPDefinedError:
            #Ignore this IP
            print("\t[WARN] - IPDefinedError found for %s" % ip, flush=True)
            continue

        #Set node information
        pubkey = node['pubkey']
        isValidator = pubkey in SOL_OBJ.validatorsLookup #if not validator, then RPC.

        #Set provider name as Other. Will get overwritten for relevant providers defined in the file
        provider_name = "Other"

        #If the ASN is in the ASN lookup, overwrite provider
        if asn in PROVIDER_ASN_LOOKUP:
            provider_name = PROVIDER_ASN_LOOKUP[results['asn']]['provider']
            
            #Create entry if provider hasn't yet been seen
            if provider_name not in SOL_OBJ.providersData:
                SOL_OBJ.providersData[provider_name] = {
                    "Total RPC Nodes": 0,
                    "Total Validators": 0,
                    "Total Stake": 0
                }

            #Catch the providers_to_track nodes and save them to the object
            if provider_name in providers_to_track.values():
                short = list(providers_to_track.keys())[list(providers_to_track.values()).index(provider_name)]
                short_to_object_map[short].SaveProviderNode(ip, pubkey, isValidator)

        #If validator, sum validator and stake. Else just sum RPC
        if isValidator:
            stake = SOL_OBJ.GetValidatorInfo(pubkey=pubkey)['stake']
            SOL_OBJ.providersData[provider_name]['Total Validators'] += 1
            SOL_OBJ.providersData[provider_name]['Total Stake'] += stake
        else:
            SOL_OBJ.providersData[provider_name]['Total RPC Nodes'] += 1

    #Calculate the percentages after a full analysis
    SOL_OBJ.CalculatePercentages()

    print("Done.", flush=True)

def PrintCompletion(short_to_object_map):   
    print("\n\n\n-----RESULTS-----")
    
    if not short_to_object_map.values():
        print("\nNo providers to track specified.")
    else:
        print("\nProvider Overview:")
        for obj in short_to_object_map.values():
            print("\n%s:" % obj.provider)
            print("\tMonitoring since epoch %d and date %s" % (obj.objectCreationEpoch, obj.objectCreationDate))
            print("\tThere are", obj.liveNodeCount, "LIVE nodes running on %s." % obj.provider)
            print("\tThere are", obj.validatorCount, "VALIDATORS running on %s." % obj.provider)
            print("\tThere have been", len(obj.nodeDict), "different solana nodes (IPs) seen running on %s since the start of this monitoring." % obj.provider)
    
    print("\n\nThere is a total of %d gossip-discoverable solana nodes" % len(SOL_OBJ.gossipLookup))
    print("There is a total of %d validator nodes on solana" % len(SOL_OBJ.validatorsLookup))
    print("\nCheck output files in output dir, farewell")

def PrintUsage():
    print("\n-----USAGE-----")
    print("Welcome to the Solana Node Scraper. This scraper analyzes the number",
        "of RPC nodes, validators, and stake of each provider specified in the PorviderLookup.json file.")

    print("\n\n-----PARAMETERS-----")
    print("The scraper takes 4 optional parameters in the following format:")
    print("\n> --exec.mode=<value> -> Defines the execution method. Options are (\"full\" or \"liveliness\") Default is \"full\".")
    print("\n> --providers=<val1>,<val2> -> Defines the providers for which to track nodes, based on the config/ProviderConfig.json and following",
        "the format defined on the README. Default is None.")
    print("\n> --from.script -> Sends the output files to upload/ for upload to GCS and silences runtime messages. Use recommended for bash scripts only.")
    print("\n> --help -> Prints this message.")

    print("\n\n-----OUTPUT-----")
    print("Except when running on \"liveliness\" mode, the scraper will build one file: SolanProviders-<date>.json containing the infrasturcure analysis of the chain.")
    print("If \"--providers\" is specified, the scraper will build a provider-<date>.json for every provider specified, containing a list of all nodes running on that provider.")

    print("\nFor a full description, see the README.md")

    exit()
        
def GetArguments(args: list):
    #Print usage and exit
    if "--help" in args:
        PrintUsage()
    
    #Set global output folder depending on call origin flag
    global OUTPUT_FOLDER
    OUTPUT_FOLDER = "output/"
    if "--from.script" in args:
        OUTPUT_FOLDER = "upload/"
        args.remove("--from.script")

    #Set arg constraints
    allowed_commands = {"--providers", "--exec.mode", "--from.cli", "--help"}
    allowed_exec_modes = {"full", "liveliness"}
    allowed_providers = LoadConfigFileAndGetAllowedProviders()

    #Vars and assign defaults
    exec_mode = "full"
    providers_to_track = {} #* short -> provider_name
    
    #Disregard the first arg (filename)
    args.pop(0)

    #Get commands and values
    for arg in args:
        buff = arg.split("=")

        #Check for good format
        if len(buff) != 2:
            print("ERROR: The argument %s has the wrong format." % arg)
            print("\tValid format is: \"--<argument>=<value>\"")
            exit()

        #Unpack command and value
        command, value = buff[0], buff[1]

        #Check that command is supported
        if command not in allowed_commands:
            print("ERROR: The argument %s is not supported." % command)
            print("\tValid arguments are:", allowed_commands)
            exit()

        #Exec mode
        if command == "--exec.mode":
            #Check for allowed exec modes
            if value not in allowed_exec_modes:
                print("ERROR: The value %s is not a valid execution method." % value)
                print("\tValid values are:", allowed_exec_modes)
                exit()
            
            #Assign exec mode
            else:
                exec_mode = value

        #Providers
        elif command == "--providers":
            providers = value.split(",")
        
            #Check for valid providers
            for short in providers:
                short = short.upper()
                if short not in allowed_providers:
                    print("ERROR: Wrong gormat or the provider %s is not a valid provider." % short)
                    print("\tThe expected format is --providers=<val1>,<val2>,... (no spaces between values)")
                    print("\tValid providers, based on the config file, are:", list(allowed_providers.keys()))
                    exit()

                #Add to list
                else:
                    providers_to_track[short] = allowed_providers[short]

    #Check that at least one provider was passed if liveliness check
    if exec_mode == "liveliness" and not providers_to_track:
        print("\nError: No providers to track were passed in the --providers flag. Can't track liveliness")
        exit()

    return exec_mode, providers_to_track

def LoadConfigFileAndGetAllowedProviders():
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

## Misc Functions ##
def GetTopAsnDescriptions():
    asns = {}

    for ip in SOL_OBJ.gossipLookup:        
        net = Net(ip)
        obj = IPASN(net)
        results = obj.lookup()
        
        #Write asn if not seen yet or count an addition
        if results['asn_description'] not in asns:
            asns[results['asn_description']] = 1
        
        else:
            asns[results['asn_description']] += 1

    mostUsedAsns = dict(sorted(asns.items(), key=lambda item: item[1]))
    with open('reference/RefAsns.json', 'w') as f:
        json.dump(mostUsedAsns, f, indent=4, default=str)
        f.close()

    return

def GetAsnDescriptionMap():
    asns = {}
    for ip in SOL_OBJ.gossipLookup:        
        net = Net(ip)
        obj = IPASN(net)
        results = obj.lookup()
        
        if results['asn'] not in asns:
            asns[results['asn']] = results['asn_description']

    with open('reference/RefAsnToDescription.json', 'w') as f:
        json.dump(asns, f, indent=4, default=str)
        f.close()

    return

## Main Caller ##
if __name__ == "__main__":
    if len(sys.argv) > 4:
        print("ERROR: Too many parameters.")
        PrintUsage()
    else:
        exec_mode, providers_to_track = GetArguments(sys.argv)
        main(exec_mode, providers_to_track)