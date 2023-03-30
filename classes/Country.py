import json, os
import pickle
from datetime import date, datetime

from classes.Blockchain import Blockchain

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
        self.cumulativeStake = 0
        self.nodeDict = {} #*{IP:{key, extra data}}

        #Historic Data
        self.objectCreationDate = date.today().strftime("%m-%d-%Y")

    def SaveCountryNode(self, ip: str, node_info: dict):   
        #Save only new ndoes
        if ip not in self.nodeDict:

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

            #Save data to object
            self.nodeDict[ip] = {
                "Address": node_info["address"],
                "Is Validator": node_info["is_validator"],
                "Stake": stake,
                "Validator Info": node_info["extra_info"]
            }

    def SaveObject(self, blockchain_obj):
        # Update analysis date before saving the object
        self.analysisDate = blockchain_obj.analysisDate
        
        print("\tSaving %s object" % self.country, flush=True)      
        os.makedirs(os.path.dirname(self.objectPath), exist_ok=True)
        with open(self.objectPath, "wb") as f:
            pickle.dump(self, f)
            f.close()
        print("\tDone.", flush=True)

    def OutputJSONInfo(self, blockchain_obj):
        path = "{base}/{output}/{target}/countries/{country}_Nodes_{time}.json".format(base=config.globals.BASE_DIR, output=config.globals.OUTPUT_FOLDER, target=self.target_chain.target, country=self.country, time=str(datetime.today().strftime("%m-%d-%Y")))
        #Catch for flow
        stake = blockchain_obj.totalStake if blockchain_obj.target != "flow" else blockchain_obj.totalStake["total"]
        to_write = {
            'Analysis Date': blockchain_obj.analysisDate,
            'Total Nodes': len(self.nodeDict),
            'Validator Nodes': self.validatorCount,
            'Non-Validator Nodes': self.nonValidatorNodeCount,
            'Monitoring since date': self.objectCreationDate,
            'Analysis Date': date.today().strftime("%m-%d-%Y"),
            'Cumulative stake': self.cumulativeStake,
            'Percentage of total stake': (self.cumulativeStake * 100) / stake, 
            'Nodes': self.nodeDict
        }

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(to_write, f, indent=4, default=str)
            f.close()