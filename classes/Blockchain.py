import json, os
import pickle
from datetime import date, datetime

import config.globals

class Blockchain:
    def __init__(self, target):
        self.target = target
        self.objectPath = "{base_dir}/memory/{target}/{target}_object.pickle".format(base_dir=config.globals.BASE_DIR, target=target)
        self.totalStake = 0
        self.totalNodes = 0
        self.totalNonValidatorNodes = 0
        self.totalValidators = 0
        self.unidentifiedASNs = {}
        self.unidentifiedLocations = {}

        #Main Data Strucutres
        self.providersData = {"Other": {"Total Non-Validator Nodes": 0, "Total Validators": 0, "Total Nodes": 0, "Total Stake": 0}, "Unidentified": {"Total Non-Validator Nodes": 0, "Total Validators": 0, "Total Nodes": 0, "Total Stake": 0}} #*Data on rpc, validators, and stake per main provider.
        self.countriesData = {"Unidentified": {"Total Non-Validator Nodes": 0, "Total Validators": 0, "Total Nodes": 0, "Total Stake": 0}} #Note: There is no other, tracking all countries

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
        print("\n\tCalculating Provider and Country Percentages.", flush=True)
        for dic in [self.providersData, self.countriesData]:
            for i in dic:
                stake = dic[i]["Total Stake"]
                rpc = dic[i]["Total Non-Validator Nodes"]
                validators = dic[i]["Total Validators"]
                total = dic[i]["Total Nodes"]

                dic[i]["Percentage of Total Stake"] = stake * 100 / self.totalStake
                if self.totalNonValidatorNodes: dic[i]["Percentage of Non-Validator Nodes"] = rpc * 100 / self.totalNonValidatorNodes
                dic[i]["Percentage of Validators"] = validators * 100 / self.totalValidators
                dic[i]["Percentage of Total Nodes"] = total * 100 / self.totalNodes
        print("\tDone.", flush=True)

    def SaveProviderDistribution(self):
        path = "{base}/{output}/{target}/network/NetworkDistribution_{time}.json".format(base=config.globals.BASE_DIR, output=config.globals.OUTPUT_FOLDER, target=self.target, time=str(datetime.today().strftime("%m-%d-%Y")))
        to_write = {
            'Analysis Date': self.analysisDate,
            'Total Nodes': self.totalNodes,
            'Total Non-Validator Nodes': self.totalNonValidatorNodes,
            'Total Validator Nodes': self.totalValidators,
            'Total stake': self.totalStake,
            'Provider Distribution': self.providersData,
            'Countries Distribution': self.countriesData
        }

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(to_write, f, indent=4, default=str)
            f.close()

class Flow(Blockchain):
    def __init__(self, target, analysis_date):
        super().__init__(target)
        self.analysisDate = analysis_date

        #Flow specific variables
        self.totalStake = {"active": 0, "total": 0}
        self.executionNodes = {"active": 0, "total": 0}
        self.consensusNodes = {"active": 0, "total": 0}
        self.collectionNodes = {"active": 0, "total": 0}
        self.verificationNodes = {"active": 0, "total": 0}
        self.accessNodes = {"active": 0, "total": 0}
        self.totalInactiveNodes = 0
    
        #Main Data Strucutre
        self.providersData = {
            "Other": {"Execution Nodes": {"active": 0, "total": 0}, "Consensus Nodes": {"active": 0, "total": 0}, "Collection Nodes": {"active": 0, "total": 0}, "Verification Nodes": {"active": 0, "total": 0}, "Access Nodes": {"active": 0, "total": 0}, "Total Stake": {"active": 0, "total": 0}, "Total Nodes": 0, "Total Inactive Nodes": 0},
            "Unidentified": {"Execution Nodes": {"active": 0, "total": 0}, "Consensus Nodes": {"active": 0, "total": 0}, "Collection Nodes": {"active": 0, "total": 0}, "Verification Nodes": {"active": 0, "total": 0}, "Access Nodes": {"active": 0, "total": 0}, "Total Stake": {"active": 0, "total": 0}, "Total Nodes": 0, "Total Inactive Nodes": 0}
        }

    def ReturnNodeTypeQuantities(self, role):
        buff = {"execution": self.executionNodes,
        "consensus": self.consensusNodes,
        "collection": self.collectionNodes, 
        "verification": self.verificationNodes, 
        "access": self.accessNodes}
        return buff[role]


    #Overwrite percentages
    def CalculatePercentages(self, target_ips):
        print("\tCalculating Provider Percentages.", flush=True)
        for provider in self.providersData:
            stake = self.providersData[provider]["Total Stake"]["total"]
            execution = self.providersData[provider]["Execution Nodes"]
            collection = self.providersData[provider]["Collection Nodes"]
            consensus = self.providersData[provider]["Consensus Nodes"]
            verification = self.providersData[provider]["Verification Nodes"]
            access = self.providersData[provider]["Access Nodes"]
            total = self.providersData[provider]["Total Nodes"]
            active = total - self.providersData[provider]["Total Inactive Nodes"]

            #Active
            self.providersData[provider]["Percentage of Active Execution Nodes"] = execution["active"] * 100 / self.executionNodes["active"]
            self.providersData[provider]["Percentage of Active Collection Nodes"] = collection["active"] * 100 / self.collectionNodes["active"]
            self.providersData[provider]["Percentage of Active Consensus Nodes"] = consensus["active"] * 100 / self.consensusNodes["active"]
            self.providersData[provider]["Percentage of Active Verification Nodes"] = verification["active"] * 100 / self.verificationNodes["active"]
            self.providersData[provider]["Percentage of Active Access Nodes"] = access["active"] * 100 / self.accessNodes["active"]
            
            #Total
            self.providersData[provider]["Percentage of Total Execution Nodes"] = execution["total"] * 100 / self.executionNodes["total"]
            self.providersData[provider]["Percentage of Total Collection Nodes"] = collection["total"] * 100 / self.collectionNodes["total"]
            self.providersData[provider]["Percentage of Total Consensus Nodes"] = consensus["total"] * 100 / self.consensusNodes["total"]
            self.providersData[provider]["Percentage of Total Verification Nodes"] = verification["total"] * 100 / self.verificationNodes["total"]
            self.providersData[provider]["Percentage of Total Access Nodes"] = access["total"] * 100 / self.accessNodes["total"]

            #General
            self.providersData[provider]["Percentage of Total Stake"] = stake * 100 / self.totalStake["active"]
            self.providersData[provider]["Percentage of Active Nodes"] = active * 100 / (self.totalNodes - self.totalInactiveNodes)
            self.providersData[provider]["Percentage of Total Nodes"] = total * 100 / self.totalNodes


        print("\tDone.", flush=True)

    def SaveProviderDistribution(self):
        path = "{base}/{output}/{target}/network/ProviderDistribution_{time}.json".format(base=config.globals.BASE_DIR, output=config.globals.OUTPUT_FOLDER, target=self.target, time=str(datetime.today().strftime("%m-%d-%Y")))
        to_write = {
            'Analysis Date': self.analysisDate,
            'Total Nodes': self.totalNodes,
            'Inactive Nodes': self.totalInactiveNodes,
            'Total Active Nodes': (self.totalNodes - self.totalInactiveNodes),
            'Total Stake': self.totalStake["total"],
            'Inactive Stake': self.totalStake["total"] - self.totalStake["total"],
            'Provider Distribution': self.providersData
        }

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(to_write, f, indent=4, default=str)
            f.close()