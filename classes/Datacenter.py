from classes.Provider import Provider

class Datacenter:
    def __init__(self, country_name:str, country_code:str, city:str, region:str, latitude:float, longitude:float, provider:Provider):
        #Info
        self.country_name = country_name
        self.country_code = country_code
        self.city = city
        self.region = region
        self.latitude = latitude
        self.longitude = longitude
        self.provider = provider
        
        #Counts
        self.validatorCount = 0
        self.nonValidatorNodeCount = 0
        self.cumulativeStake = 0
        self.nodeDict = {} #*{IP:{key, extra data}}
        
    def __eq__(self, other):
            if not isinstance(other, Datacenter):
                print("ERROR: Tried comparing an insance of type %s with Datacenter." % type(other))
                exit(1)
            
            #It is the same datacenter if all properties are the same and there is less than 0.2 distance from each other in latitude and longitude
            if self.city == other.city and self.provider.provider == other.provider.provider and self.country_name == other.country_name and abs(self.latitude - other.latitude) < 0.2 and abs(self.longitude - other.longitude) < 0.2:
                return True
            return False
    
    def SaveDatacenterNode(self, ip: str, node_info: dict):   
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

    def GetDatacenterData(self, parent_total_stake):
        return {
            "Country": self.country_name,
            "City": self.city,
            "Region": self.region,
            "Coordinates": f"{self.latitude}, {self.longitude}",
            'Total Nodes': len(self.nodeDict),
            'Validator Nodes': self.validatorCount,
            'Non-Validator Nodes': self.nonValidatorNodeCount,
            'Cumulative stake': self.cumulativeStake,
            'Percentage provider total stake': (self.cumulativeStake * 100) / parent_total_stake,
            "Nodes": self.nodeDict
        }