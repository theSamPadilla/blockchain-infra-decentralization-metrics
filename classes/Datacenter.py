from classes.Provider import Provider
from classes.dict_initial_values import flow_total_stake

class Datacenter:
    def __init__(self, country_name:str, country_code:str, city:str, region:str, latitude:float, longitude:float, provider:Provider):
        #Info
        self.country_name = country_name
        self.country_code = country_code
        self.city = city
        self.region = region
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.provider = provider
        
        #Counts
        self.validatorCount = 0
        self.nonValidatorNodeCount = 0
        self.cumulativeStake = flow_total_stake if provider.target_chain.target == "flow" else 0
        self.nodeDict = {} #*{IP:{key, extra data}}
        
    def __eq__(self, other):
            if not isinstance(other, Datacenter):
                print("ERROR: Tried comparing an insance of type %s with Datacenter." % type(other))
                exit(1)
            
            #It is the same datacenter if all properties are the same and there is less than 0.2 distance from each other in latitude and longitude
            if self.city == other.city and self.provider.provider == other.provider.provider and self.country_name == other.country_name and abs(self.latitude - other.latitude) < 0.2 and abs(self.longitude - other.longitude) < 0.2:
                return True
            return False
    
    def SaveDatacenterNode(self, ip: str, node_info: dict, role=None):   
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

    def GetDatacenterData(self, provider_total_stake):
        stake_percentage = 0 if provider_total_stake == 0 else (self.cumulativeStake * 100) / provider_total_stake
        return {
            "Country": self.country_name,
            "City": self.city,
            "Region": self.region,
            "Coordinates": f"{self.latitude}, {self.longitude}",
            'Total Nodes': len(self.nodeDict),
            'Validator Nodes': self.validatorCount,
            'Non-Validator Nodes': self.nonValidatorNodeCount,
            'Cumulative stake': self.cumulativeStake,
            'Percentage of provider stake': stake_percentage,
            "Nodes": self.nodeDict
        }

    def GetFlowDatacenterData(self, provider_total_stake_dict:dict):
        execution = 0 if provider_total_stake_dict["execution"]["total"] == 0 else (self.cumulativeStake["execution"]["total"] * 100) / provider_total_stake_dict["execution"]["total"]
        consensus = 0 if provider_total_stake_dict["consensus"]["total"] == 0 else (self.cumulativeStake["consensus"]["total"] * 100) / provider_total_stake_dict["consensus"]["total"]
        collection = 0 if provider_total_stake_dict["collection"]["total"] == 0 else (self.cumulativeStake["collection"]["total"] * 100) / provider_total_stake_dict["collection"]["total"]
        verification = 0 if provider_total_stake_dict["verification"]["total"] == 0 else (self.cumulativeStake["verification"]["total"] * 100) / provider_total_stake_dict["verification"]["total"]
        access = 0 if provider_total_stake_dict["access"]["total"] == 0 else (self.cumulativeStake["access"]["total"] * 100) / provider_total_stake_dict["access"]["total"]

        stake_percentages = {
            "execution": execution,
            "consensus": consensus,
            "collection": collection, 
            "verification": verification,
            "access": access
            }
        
        return {
            "Country": self.country_name,
            "City": self.city,
            "Region": self.region,
            "Coordinates": f"{self.latitude}, {self.longitude}",
            'Total Nodes': len(self.nodeDict),
            'Validator Nodes': self.validatorCount,
            'Non-Validator Nodes': self.nonValidatorNodeCount,
            'Cumulative stake': self.cumulativeStake,
            'Percentage of provider Total stake': stake_percentages,
            "Nodes": self.nodeDict
        }