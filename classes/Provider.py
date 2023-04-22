import json, os
from datetime import date, datetime

import config.globals
from classes.Blockchain import Blockchain
from classes.dict_initial_values import flow_total_stake

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
        self.cumulativeStake = flow_total_stake if self.target_chain.target == "flow" else 0
        self.seenIPs = set()
        self.datacenters = []

        #Historic Data
        self.objectCreationDate = date.today().strftime("%m-%d-%Y")
    
    def UpdateTotals(self, ip: str, node_info: dict, role=None):   
        #Save only new ndoes
        if ip not in self.seenIPs:
            #Check if the IP is a validator
            if node_info["is_validator"]:
                self.validatorCount += 1
                if not node_info['stake']:
                    stake = 0
                else:
                    stake = int(float(node_info['stake']))

                #Catch Flow stake
                if not role:       
                    self.cumulativeStake += stake
                else:
                    if node_info["extra_info"]["is_active"]:
                        self.cumulativeStake[role]["active"] += stake
                    else:
                        self.cumulativeStake[role]["total"] += stake
            
            #Non validator node
            else:
                self.nonValidatorNodeCount += 1
                stake = None

            #Save ip to set
            self.seenIPs.add(ip)

    def OutputJSONInfo(self, blockchain_obj):
        path = "{base}/{output}/{target}/providers/{provider}_Nodes_{time}.json".format(base=config.globals.BASE_DIR, output=config.globals.OUTPUT_FOLDER, target=self.target_chain.target, provider=self.provider, time=str(datetime.today().strftime("%m-%d-%Y")))
        #Catch for flow
        if blockchain_obj.target == "flow":
            execution = 0 if blockchain_obj.totalStake["execution"]["total"] == 0 else (self.cumulativeStake["execution"]["total"] * 100) / blockchain_obj.totalStake["execution"]["total"]
            consensus = 0 if blockchain_obj.totalStake["consensus"]["total"] == 0 else (self.cumulativeStake["consensus"]["total"] * 100) / blockchain_obj.totalStake["consensus"]["total"]
            collection = 0 if blockchain_obj.totalStake["collection"]["total"] == 0 else (self.cumulativeStake["collection"]["total"] * 100) / blockchain_obj.totalStake["collection"]["total"]
            verification = 0 if blockchain_obj.totalStake["verification"]["total"] == 0 else (self.cumulativeStake["verification"]["total"] * 100) / blockchain_obj.totalStake["verification"]["total"]
            access = 0 if blockchain_obj.totalStake["access"]["total"] == 0 else (self.cumulativeStake["access"]["total"] * 100) / blockchain_obj.totalStake["access"]["total"]

            stake_percentage = {
                "execution": execution,
                "consensus": consensus,
                "collection": collection, 
                "verification": verification,
                "access": access
                }
         
        else:
            stake_percentage = 0 if blockchain_obj.totalStake == 0 else (self.cumulativeStake * 100) / blockchain_obj.totalStake
    
        to_write = {
            'Analysis Date': blockchain_obj.analysisDate,
            'Total Nodes': self.GetTotalNodes(),
            'Validator Nodes': self.validatorCount,
            'Non-Validator Nodes': self.nonValidatorNodeCount,
            'Monitoring since date': self.objectCreationDate,
            'Analysis Date': date.today().strftime("%m-%d-%Y"),
            'Cumulative stake': self.cumulativeStake,
            'Percentage of total stake': stake_percentage, 
            'Number of datacenters': len(self.datacenters),
            'Datacenters': self.GetDataCenterNodes(self.cumulativeStake)
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
        if self.target_chain.target == "flow":
            for datacenter in self.datacenters:
                results.append(datacenter.GetFlowDatacenterData(provider_total_stake))
        else:
            for datacenter in self.datacenters:
                results.append(datacenter.GetDatacenterData(provider_total_stake))
        return results

