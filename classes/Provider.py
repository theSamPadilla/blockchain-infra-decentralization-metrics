import json, os
import pickle
from datetime import date, datetime

import config.globals
from classes.Blockchain import Blockchain

class Provider:
    def __init__(self, short:str, provider:str, target_chain:Blockchain):
        #Info
        self.short = short
        self.provider = provider
        self.target_chain = target_chain
        self.analysisDate = date.today().strftime("%m-%d-%Y") #This will get overwritten by the timestamp in the JSON file
        self.objectPath = "{base}/memory/{target_chain}/providers/{short}_object.pickle".format(base=config.globals.BASE_DIR, target_chain=target_chain.target, short=short)

        #Counts
        self.validatorCount = 0
        self.nonValidatorNodeCount = 0
        self.cumulativeStake = 0
        self.seenIPs = set()
        self.datacenters = []

        #Historic Data
        self.objectCreationDate = date.today().strftime("%m-%d-%Y")
    
    def UpdateAnalysisDate(self, analysisDate: str):
        self.analysisDate = analysisDate

    def UpdateTotals(self, ip: str, node_info: dict):   
        #Save only new ndoes
        if ip not in self.seenIPs:
            #Check if the IP is a validator
            if node_info["is_validator"]:
                self.validatorCount += 1
                if not node_info['stake']:
                    stake = 0
                else:
                    stake = int(float(node_info['stake']))              
                self.cumulativeStake += stake
            
            #Non validator node
            else:
                self.nonValidatorNodeCount += 1
                stake = None

            #Save ip to set
            self.seenIPs.add(ip)

    def SaveObject(self, blockchain_obj):
        # Update analysis date before saving the object
        self.analysisDate = blockchain_obj.analysisDate
        
        print("\tSaving %s object" % self.provider, flush=True)      
        os.makedirs(os.path.dirname(self.objectPath), exist_ok=True)
        with open(self.objectPath, "wb") as f:
            pickle.dump(self, f)
            f.close()
        print("\tDone.", flush=True)

    def OutputJSONInfo(self, blockchain_obj):
        path = "{base}/{output}/{target}/providers/{provider}_Nodes_{time}.json".format(base=config.globals.BASE_DIR, output=config.globals.OUTPUT_FOLDER, target=self.target_chain.target, provider=self.provider, time=str(datetime.today().strftime("%m-%d-%Y")))
        #Catch for flow
        stake = blockchain_obj.totalStake if blockchain_obj.target != "flow" else blockchain_obj.totalStake["total"]
        to_write = {
            'Analysis Date': self.analysisDate,
            'Total Nodes': self.GetTotalNodes(),
            'Validator Nodes': self.validatorCount,
            'Non-Validator Nodes': self.nonValidatorNodeCount,
            'Monitoring since date': self.objectCreationDate,
            'Analysis Date': date.today().strftime("%m-%d-%Y"),
            'Cumulative stake': self.cumulativeStake,
            'Percentage of total stake': (self.cumulativeStake * 100) / stake, 
            'Number of datacenters': len(self.datacenters),
            'Datacenters': self.GetDataCenterNodes((self.cumulativeStake * 100) / stake)
        }

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(to_write, f, indent=4, default=str)
            f.close()

    def GetTotalNodes(self):
        total = 0
        for datacenter in self.datacenters:
            total += len(datacenter.nodeDict)
        return total

    def GetDataCenterNodes(self, provider_total_stake):
        results = []
        for datacenter in self.datacenters:
            results.append(datacenter.GetDatacenterData(provider_total_stake))
        return results
