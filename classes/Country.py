import json, os
import pickle
from datetime import date, datetime

from classes.Blockchain import Blockchain
from classes.dict_initial_values import flow_total_stake

import config.globals

class Country:
    def __init__(self, country_name:str, code:str, target_chain:Blockchain):
        #Info
        self.country = country_name
        self.code = code
        self.cities = set()
        self.target_chain = target_chain
        self.analysisDate = date.today().strftime("%m-%d-%Y") #This will get overwritten by the timestamp in the JSON file
        self.objectPath = "{base}/memory/{target_chain}/countries/{code}_object.pickle".format(base=config.globals.BASE_DIR, target_chain=target_chain.target, code=code)

        #Counts
        self.validatorCount = 0
        self.nonValidatorNodeCount = 0
        self.cumulativeStake = flow_total_stake if self.target_chain.target == "flow" else 0
        self.nodeDict = {} #*{IP:{key, extra data}}

        #Historic Data
        self.objectCreationDate = date.today().strftime("%m-%d-%Y")

    def SaveCountryNode(self, ip: str, node_info: dict, role=None):   
        #Save only new ndoes
        if ip not in self.nodeDict:

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

            #Save data to object
            self.nodeDict[ip] = {
                "Address": node_info["address"],
                "Is Validator": node_info["is_validator"],
                "Stake": stake,
                "Validator Info": node_info["extra_info"]
            }

    def OutputJSONInfo(self, blockchain_obj):
        path = "{base}/{output}/{target}/countries/{country}_Nodes_{time}.json".format(base=config.globals.BASE_DIR, output=config.globals.OUTPUT_FOLDER, target=self.target_chain.target, country=self.country, time=str(datetime.today().strftime("%m-%d-%Y")))
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
            'Total Nodes': len(self.nodeDict),
            'Validator Nodes': self.validatorCount,
            'Non-Validator Nodes': self.nonValidatorNodeCount,
            'Monitoring since date': self.objectCreationDate,
            'Analysis Date': date.today().strftime("%m-%d-%Y"),
            'Cumulative stake': self.cumulativeStake,
            'Percentage of total stake': stake_percentage, 
            'Nodes': self.nodeDict
        }

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(to_write, f, indent=4, default=str)
            f.close()