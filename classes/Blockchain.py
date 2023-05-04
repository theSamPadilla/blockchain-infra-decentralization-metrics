import json, os
from datetime import date, datetime

import config.globals
from copy import deepcopy

from classes.dict_initial_values import providers_init, location_init, providers_init_flow, location_init_flow, flow_total_stake

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
        self.info = {}

        #Main Data Strucutre initializers
        self.providersData = providers_init
        self.continentData = location_init

        #Set object creation date and analysis date
        self.objectCreationDate = date.today().strftime("%m-%d-%Y")
        self.analysisDate = date.today().strftime("%m-%d-%Y") # will get overwritten by the timestamp in the JSON

    def CalculatePercentages(self):
        print("\n\tCalculating Provider, Continent, and Country Percentages.", flush=True)
        for dic in [self.providersData, self.continentData]:
            for i in dic:
                stake = dic[i]["Total Stake"]
                rpc = dic[i]["Total Non-Validator Nodes"]
                validators = dic[i]["Total Validators"]
                total = dic[i]["Total Nodes"]

                dic[i]["Percentage of Total Stake"] = stake * 100 / self.totalStake
                if self.totalNonValidatorNodes: dic[i]["Percentage of Non-Validator Nodes"] = rpc * 100 / self.totalNonValidatorNodes
                dic[i]["Percentage of Validators"] = validators * 100 / self.totalValidators
                dic[i]["Percentage of Total Nodes"] = total * 100 / self.totalNodes
            
                #Get Country percentages
                if "Countries" in dic[i]:
                    for c in dic[i]["Countries"]:
                        c_stake = dic[i]["Countries"][c]["Total Stake"]
                        c_rpc = dic[i]["Countries"][c]["Total Non-Validator Nodes"]
                        c_validators = dic[i]["Countries"][c]["Total Validators"]
                        c_total = dic[i]["Countries"][c]["Total Nodes"]

                        dic[i]["Countries"][c]["Percentage of Total Stake"] = c_stake * 100 / self.totalStake
                        if self.totalNonValidatorNodes: dic[i]["Countries"][c]["Percentage of Non-Validator Nodes"] = c_rpc * 100 / self.totalNonValidatorNodes
                        dic[i]["Countries"][c]["Percentage of Validators"] = c_validators * 100 / self.totalValidators
                        dic[i]["Countries"][c]["Percentage of Total Nodes"] = c_total * 100 / self.totalNodes
        
        print("\tDone.", flush=True)

    def SaveProviderDistribution(self):
        path = "{base}/{output}/{target}/network/NetworkDistribution_{time}.json".format(base=config.globals.BASE_DIR, output=config.globals.OUTPUT_FOLDER, target=self.target, time=str(datetime.today().strftime("%m-%d-%Y")))
        to_write = {
            'Analysis Date': self.analysisDate,
            'Info': self.info,
            'Total Nodes': self.totalNodes,
            'Total Non-Validator Nodes': self.totalNonValidatorNodes,
            'Total Validator Nodes': self.totalValidators,
            'Total Stake': self.totalStake,
            'Provider Distribution': self.providersData,
            'Geographic Distribution': self.continentData
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
        self.totalStake = deepcopy(flow_total_stake)
        self.executionNodes = {"active": 0, "total": 0}
        self.consensusNodes = {"active": 0, "total": 0}
        self.collectionNodes = {"active": 0, "total": 0}
        self.verificationNodes = {"active": 0, "total": 0}
        self.accessNodes = {"active": 0, "total": 0}
        self.totalInactiveNodes = 0
    
        #Main Data Strucutres
        self.providersData = providers_init_flow
        self.continentData = location_init_flow

    def ReturnNodeTypeQuantities(self, role):
        buff = {"execution": self.executionNodes,
        "consensus": self.consensusNodes,
        "collection": self.collectionNodes, 
        "verification": self.verificationNodes, 
        "access": self.accessNodes}
        return buff[role]

    #Overwrite percentages function
    def CalculatePercentages(self):
        self.CalculateProviderPercentages()
        self.CalculateLocationPercentages()
        print("\tDone.", flush=True)

    def CalculateProviderPercentages(self):
        print("\tCalculating Provider Percentages.", flush=True)
        for provider in self.providersData:
            #Stake
            execution_stake = self.providersData[provider]["Total Stake"]["execution"]["total"]
            consensus_stake = self.providersData[provider]["Total Stake"]["consensus"]["total"]
            collection_stake = self.providersData[provider]["Total Stake"]["collection"]["total"]
            verification_stake = self.providersData[provider]["Total Stake"]["verification"]["total"]
            access_stake = self.providersData[provider]["Total Stake"]["access"]["total"]

            #Counts
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

            #Stake percentages
            self.providersData[provider]["Percentage of Total Execution Stake"] = execution_stake * 100 / self.totalStake["execution"]["active"]
            self.providersData[provider]["Percentage of Total Consensus Stake"] = consensus_stake * 100 / self.totalStake["consensus"]["active"]
            self.providersData[provider]["Percentage of Total Collection Stake"] = collection_stake * 100 / self.totalStake["collection"]["active"]
            self.providersData[provider]["Percentage of Total Verification Stake"] = verification_stake * 100 / self.totalStake["verification"]["active"]
            self.providersData[provider]["Percentage of Total Access Stake"] = access_stake * 100 / self.totalStake["access"]["active"]

            #Other percentages
            self.providersData[provider]["Percentage of Active Nodes"] = active * 100 / (self.totalNodes - self.totalInactiveNodes)
            self.providersData[provider]["Percentage of Total Nodes"] = total * 100 / self.totalNodes

    def CalculateLocationPercentages(self):
        print("\tCalculating Country Percentages.", flush=True)
        for continent in self.continentData:
            #Stake
            execution_stake_contintnet = self.continentData[continent]["Total Stake"]["execution"]["total"]
            consensus_stake_contintnet = self.continentData[continent]["Total Stake"]["consensus"]["total"]
            collection_stake_contintnet = self.continentData[continent]["Total Stake"]["collection"]["total"]
            verification_stake_contintnet = self.continentData[continent]["Total Stake"]["verification"]["total"]
            access_stake_contintnet = self.continentData[continent]["Total Stake"]["access"]["total"]
            
            #Counts
            execution_contintnet = self.continentData[continent]["Execution Nodes"]
            collection_contintnet = self.continentData[continent]["Collection Nodes"]
            consensus_contintnet = self.continentData[continent]["Consensus Nodes"]
            verification_contintnet = self.continentData[continent]["Verification Nodes"]
            access_contintnet = self.continentData[continent]["Access Nodes"]
            total_contintnet = self.continentData[continent]["Total Nodes"]
            active_contintnet = total_contintnet - self.continentData[continent]["Total Inactive Nodes"]

            #Active
            self.continentData[continent]["Percentage of Active Execution Nodes"] = execution_contintnet["active"] * 100 / self.executionNodes["active"]
            self.continentData[continent]["Percentage of Active Collection Nodes"] = collection_contintnet["active"] * 100 / self.collectionNodes["active"]
            self.continentData[continent]["Percentage of Active Consensus Nodes"] = consensus_contintnet["active"] * 100 / self.consensusNodes["active"]
            self.continentData[continent]["Percentage of Active Verification Nodes"] = verification_contintnet["active"] * 100 / self.verificationNodes["active"]
            self.continentData[continent]["Percentage of Active Access Nodes"] = access_contintnet["active"] * 100 / self.accessNodes["active"]
            
            #Total
            self.continentData[continent]["Percentage of Total Execution Nodes"] = execution_contintnet["total"] * 100 / self.executionNodes["total"]
            self.continentData[continent]["Percentage of Total Collection Nodes"] = collection_contintnet["total"] * 100 / self.collectionNodes["total"]
            self.continentData[continent]["Percentage of Total Consensus Nodes"] = consensus_contintnet["total"] * 100 / self.consensusNodes["total"]
            self.continentData[continent]["Percentage of Total Verification Nodes"] = verification_contintnet["total"] * 100 / self.verificationNodes["total"]
            self.continentData[continent]["Percentage of Total Access Nodes"] = access_contintnet["total"] * 100 / self.accessNodes["total"]

            #Stake Percentages
            self.continentData[continent]["Percentage of Total Execution Stake"] = execution_stake_contintnet * 100 / self.totalStake["execution"]["active"]
            self.continentData[continent]["Percentage of Total Consensus Stake"] = consensus_stake_contintnet * 100 / self.totalStake["consensus"]["active"]
            self.continentData[continent]["Percentage of Total Collection Stake"] = collection_stake_contintnet * 100 / self.totalStake["collection"]["active"]
            self.continentData[continent]["Percentage of Total Verification Stake"] = verification_stake_contintnet * 100 / self.totalStake["verification"]["active"]
            self.continentData[continent]["Percentage of Total Access Stake"] = access_stake_contintnet * 100 / self.totalStake["access"]["active"]

            #Other percentages
            self.continentData[continent]["Percentage of Active Nodes"] = active_contintnet * 100 / (self.totalNodes - self.totalInactiveNodes)
            self.continentData[continent]["Percentage of Total Nodes"] = total_contintnet * 100 / self.totalNodes

            #Countries
            for country in self.continentData[continent]["Countries"]:
                self.CalculateCountryPercentages(country, continent)

    def CalculateCountryPercentages(self, country, continent):
        #Stake
        execution_stake_country = self.continentData[continent]["Countries"][country]["Total Stake"]["execution"]["total"]
        consensus_stake_country = self.continentData[continent]["Countries"][country]["Total Stake"]["consensus"]["total"]
        collection_stake_country = self.continentData[continent]["Countries"][country]["Total Stake"]["collection"]["total"]
        verification_stake_country = self.continentData[continent]["Countries"][country]["Total Stake"]["verification"]["total"]
        access_stake_country = self.continentData[continent]["Countries"][country]["Total Stake"]["access"]["total"]
        
        #Counts
        execution_country = self.continentData[continent]["Countries"][country]["Execution Nodes"]
        collection_country = self.continentData[continent]["Countries"][country]["Collection Nodes"]
        consensus_country = self.continentData[continent]["Countries"][country]["Consensus Nodes"]
        verification_country = self.continentData[continent]["Countries"][country]["Verification Nodes"]
        access_country = self.continentData[continent]["Countries"][country]["Access Nodes"]
        total_country = self.continentData[continent]["Countries"][country]["Total Nodes"]
        active_country = total_country - self.continentData[continent]["Countries"][country]["Total Inactive Nodes"]

        #Active
        self.continentData[continent]["Countries"][country]["Percentage of Active Execution Nodes"] = execution_country["active"] * 100 / self.executionNodes["active"]
        self.continentData[continent]["Countries"][country]["Percentage of Active Collection Nodes"] = collection_country["active"] * 100 / self.collectionNodes["active"]
        self.continentData[continent]["Countries"][country]["Percentage of Active Consensus Nodes"] = consensus_country["active"] * 100 / self.consensusNodes["active"]
        self.continentData[continent]["Countries"][country]["Percentage of Active Verification Nodes"] = verification_country["active"] * 100 / self.verificationNodes["active"]
        self.continentData[continent]["Countries"][country]["Percentage of Active Access Nodes"] = access_country["active"] * 100 / self.accessNodes["active"]
        
        #Total
        self.continentData[continent]["Countries"][country]["Percentage of Total Execution Nodes"] = execution_country["total"] * 100 / self.executionNodes["total"]
        self.continentData[continent]["Countries"][country]["Percentage of Total Collection Nodes"] = collection_country["total"] * 100 / self.collectionNodes["total"]
        self.continentData[continent]["Countries"][country]["Percentage of Total Consensus Nodes"] = consensus_country["total"] * 100 / self.consensusNodes["total"]
        self.continentData[continent]["Countries"][country]["Percentage of Total Verification Nodes"] = verification_country["total"] * 100 / self.verificationNodes["total"]
        self.continentData[continent]["Countries"][country]["Percentage of Total Access Nodes"] = access_country["total"] * 100 / self.accessNodes["total"]

        #Stake percentages
        self.continentData[continent]["Countries"][country]["Percentage of Total Execution Stake"] = execution_stake_country * 100 / self.totalStake["execution"]["active"]
        self.continentData[continent]["Countries"][country]["Percentage of Total Consensus Stake"] = consensus_stake_country * 100 / self.totalStake["consensus"]["active"]
        self.continentData[continent]["Countries"][country]["Percentage of Total Collection Stake"] = collection_stake_country * 100 / self.totalStake["collection"]["active"]
        self.continentData[continent]["Countries"][country]["Percentage of Total Verification Stake"] = verification_stake_country * 100 / self.totalStake["verification"]["active"]
        self.continentData[continent]["Countries"][country]["Percentage of Total Access Stake"] = access_stake_country * 100 / self.totalStake["access"]["active"]
        
        #Other percentages
        self.continentData[continent]["Countries"][country]["Percentage of Active Nodes"] = active_country * 100 / (self.totalNodes - self.totalInactiveNodes)
        self.continentData[continent]["Countries"][country]["Percentage of Total Nodes"] = total_country * 100 / self.totalNodes

    def SaveProviderDistribution(self):
        path = "{base}/{output}/{target}/network/ProviderDistribution_{time}.json".format(base=config.globals.BASE_DIR, output=config.globals.OUTPUT_FOLDER, target=self.target, time=str(datetime.today().strftime("%m-%d-%Y")))
        to_write = {
            'Analysis Date': self.analysisDate,
            'Total Nodes': self.totalNodes,
            'Inactive Nodes': self.totalInactiveNodes,
            'Total Active Nodes': (self.totalNodes - self.totalInactiveNodes),
            'Total Stake': self.totalStake,
            'Provider Distribution': self.providersData,
            'Geographic Distribution': self.continentData
        }

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(to_write, f, indent=4, default=str)
            f.close()