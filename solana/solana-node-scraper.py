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
from datetime import date, datetime
from ipwhois.net import Net #type: ignore
from ipwhois.asn import IPASN #type: ignore

## Load Settings ##
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
with open(BASE_DIR + "/config/SettingsConfig.json", "r") as f:
    loaded = json.load(f)
    SOL_CLI_PATH = loaded["sol_cli"]
    OUTPUT_FOLDER = loaded["output_folder"]
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
        
        #Run Gossip and Validators
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

    def SaveNodes(self, nodes):
        time = str(datetime.today().strftime("%m-%d-%Y"))
        path = f"{OUTPUT_FOLDER}/solana.json"
        to_write = {
            'timestamp': time,
            'collection_method': "api",
            'chain_data': {"epoch": self.epoch},
            'nodes': nodes
        }

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(to_write, f, indent=4, default=str)
            f.close()

    @classmethod
    def GetNodeBalance(cls, pubkey: str):
        #Implemented as a subprocess to avoid API rates
        result = subprocess.run([SOL_CLI_PATH, "balance", pubkey], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        #Return the result as a float -> convert from lamport to SOL
        return float(result.stdout.strip(' SOL\n'))

## Main ##
def main():
    print("\n-----RUNTIME-----")
    
    #Make SOL Object (global) and provider objects if providers_to_track not empty
    MakeSolanaObject()
    nodes = GetIPs()

    #Save the node JSON
    print("\n\nOutputting information to JSON files...")
    SOL_OBJ.SaveNodes(nodes)
    print("Done.", flush=True)

    #Output results if called from CLI
    PrintCompletion()

## Helper Functions ##
def MakeSolanaObject():
    global SOL_OBJ

    print("Building Solana CLI object for the first time.", flush=True)
    SOL_OBJ = SolanaCLI()
    print("Done.", flush=True)
    
    return

def GetIPs():
    print(f"\n\nAnalyzing {len(SOL_OBJ.gossipLookup)} Nodes. This may take a few minutes...", flush=True)
    nodes = {}
    i = 0

    #Iterate over all gossipNodes
    for ip, node in SOL_OBJ.gossipLookup.items():
        print(f"\tAnalyzing {ip} \t\t ({i}/{len(SOL_OBJ.gossipLookup)})", flush=True)
        #Set node information
        pubkey = node['pubkey']
        isValidator = pubkey in SOL_OBJ.validatorsLookup #if not validator, then RPC.
        extra_info = {}
        stake = 0
        if isValidator:
            extra_info = SOL_OBJ.GetValidatorInfo(pubkey=pubkey)
            stake = extra_info['stake']
        extra_info['Sol Balance'] = SOL_OBJ.GetNodeBalance(pubkey)

        nodes[ip] = {
            "is_validator": isValidator,
            "stake": stake,
            "address": pubkey,
            "extra_info": extra_info
        }
        i += 1

    print("Done.", flush=True)
    return nodes

def PrintCompletion():       
    print("\n\nThere is a total of %d gossip-discoverable solana nodes" % len(SOL_OBJ.gossipLookup))
    print("There is a total of %d validator nodes on solana" % len(SOL_OBJ.validatorsLookup))
    print("\nCheck output file to continue analysis. Farewell")

def PrintUsage():
    print("\n-----USAGE-----")
    print("Welcome to the Solana Node Scraper. This is a slimmed down version of https://github.com/theSamPadilla/solana-node-scraper.",
        " It is built to use in conjunction with the decentralization metrics tool")

    print("\n\n-----PARAMETERS-----")
    print("\n> --help -> Prints this message.")

    print("\nFor a full description, see the README.md")

    exit()

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
    if "--help" in sys.argv:
        PrintUsage()
    else:
        main()