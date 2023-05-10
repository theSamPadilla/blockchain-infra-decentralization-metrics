import json
import ipinfo #type: ignore


import config.globals
from analysis.utils import IpAsnLookup, IpGeoLookup, ProviderAnalysis, CountryAnalysis, FlowProviderAnalysis, FlowCountryAnalysis, IsValidIp
from classes.Blockchain import Blockchain, Flow


## Holds analysis functions ##
def GetNetworkProviderDistribution(providers_to_track: dict, countries_to_track: dict, providers_short_to_object_map: dict, countries_short_to_object_map: dict, blockchain_obj) -> Blockchain:
    #Get IP address JSON file
    path = f"{config.globals.BASE_DIR}/json/{blockchain_obj.target}.json"
    with open(path, "r") as f:
        json_analysis = json.load(f)
        f.close()

    # Update blockchain object analysisDate and info
    analysisDate = json_analysis["timestamp"] #This is purely for human-readability, no need to be date type.
    blockchain_obj.analysisDate = analysisDate
    target_ips = json_analysis["nodes"]
    blockchain_obj.info = {
        "Collection Method": json_analysis["collection_method"],
        "Context": json_analysis["chain_data"]
    }

    print("\n\nAnalyzing %d Nodes. This may take a few minutes..." % len(target_ips), flush=True)

    #Delegate the flow runs to appropriate object and overwrite the object
    if blockchain_obj.target == "flow":
        blockchain_obj = GetFlowNetworkProviderDistribution(providers_to_track, countries_to_track, providers_short_to_object_map, countries_short_to_object_map, target_ips, analysisDate)
    else:
        GetGeneralNetworkProviderDistribution(providers_to_track, countries_to_track, providers_short_to_object_map, countries_short_to_object_map, target_ips, analysisDate, blockchain_obj)

    print("Done.", flush=True)
    return blockchain_obj

def GetFlowNetworkProviderDistribution(providers_to_track: dict, countries_to_track: dict, providers_short_to_object_map: dict, countries_short_to_object_map: dict, target_ips: dict, analysisDate: str) -> Blockchain:
    #Overwrite blockchain_obj variable to Flow() class and set IP handler.
    blockchain_obj = Flow("flow", analysisDate)
    ip_handler = ipinfo.getHandler(config.globals.IPINFO_TOKEN)
    
    #Iterate over all IP addresses
    for ip, node_info in target_ips.items():
        #Mark invalid IPs
        if not IsValidIp(ip):
            asn, provider_name = None, "Invalid"
            country, country_code, city, region, latitude, longitude, continent = ["Invalid", "Invalid", "Invalid", "Invalid", 0, 0, "Invalid"]
        else:
            #IP ASN Lookup
            asn, provider_name = IpAsnLookup(ip, target_ips, blockchain_obj)
            #IP Geolookup
            country, country_code, city, region, latitude, longitude, continent = [i for i in IpGeoLookup(ip, target_ips, blockchain_obj, ip_handler)]

        #Identify role parameter, stake, and key name
        role = node_info["extra_info"]["role"]
        role_param = blockchain_obj.ReturnNodeTypeQuantities(role)
        stake = 0 if not node_info["stake"] else int(float(node_info["stake"]))
        key_name = f"{role.capitalize()} Nodes"

        #Perform Analysis
        provider_name = FlowProviderAnalysis(providers_to_track, asn, ip, node_info, providers_short_to_object_map, country, country_code, city, region, latitude, longitude, provider_name, analysisDate, blockchain_obj, role)
        FlowCountryAnalysis(countries_to_track, continent, country, country_code, city, ip, node_info, countries_short_to_object_map, analysisDate, blockchain_obj, role)

        #Check if it meets requirements and add to general and provider stake
        if node_info["extra_info"]["is_active"]:
            role_param["active"] += 1

            #Total stake
            blockchain_obj.totalStake[role]["active"] += stake
            blockchain_obj.providersData[provider_name]["Total Stake"][role]["active"] += stake
            blockchain_obj.continentData[continent]['Total Stake'][role]["active"] += stake
            blockchain_obj.continentData[continent]["Countries"][country]['Total Stake'][role]["active"] += stake

            #Provider and country data
            blockchain_obj.providersData[provider_name][key_name]["active"] += 1
            blockchain_obj.continentData[continent][key_name]["active"] += 1
            blockchain_obj.continentData[continent]["Countries"][country][key_name]["active"] += 1


        #Else sum inactive nodes to provider dict and blockchain object
        else:
            blockchain_obj.providersData[provider_name]['Total Inactive Nodes'] += 1
            blockchain_obj.continentData[continent]['Total Inactive Nodes'] += 1
            blockchain_obj.continentData[continent]["Countries"][country]['Total Inactive Nodes'] += 1
            blockchain_obj.totalInactiveNodes += 1

        #Add to general and provider/country totals
        role_param["total"] += 1
        blockchain_obj.totalStake[role]["total"] += stake
        blockchain_obj.continentData[continent]['Total Nodes'] += 1
        blockchain_obj.continentData[continent]["Countries"][country]['Total Nodes'] += 1
        blockchain_obj.totalNodes += 1

        #Provider data
        blockchain_obj.providersData[provider_name][key_name]["total"] += 1
        blockchain_obj.providersData[provider_name]["Total Stake"][role]["total"] += stake
        blockchain_obj.providersData[provider_name]["Total Nodes"] += 1

        #Country data
        blockchain_obj.continentData[continent]['Total Nodes'] += 1
        blockchain_obj.continentData[continent]["Countries"][country]['Total Nodes'] += 1
        blockchain_obj.continentData[continent]["Total Stake"][role]["total"] += stake
        blockchain_obj.continentData[continent]["Countries"][country]["Total Stake"][role]["total"] += stake
        blockchain_obj.continentData[continent][key_name]["total"] += 1
        blockchain_obj.continentData[continent]["Countries"][country][key_name]["total"] += 1

    #Calculate the percentages after a full analysis
    blockchain_obj.CalculatePercentages()
    return blockchain_obj

def GetGeneralNetworkProviderDistribution(providers_to_track: dict, countries_to_track: dict, providers_short_to_object_map: dict, countries_short_to_object_map: dict, target_ips: dict, analysisDate: str, blockchain_obj: Blockchain):
    #Set Ipinfo handler
    ip_handler = ipinfo.getHandler(config.globals.IPINFO_TOKEN)
    
    #Iterate over all IP addresses
    for ip, node_info in target_ips.items():
        #Set invalid if IP is private, loopback, or invalid
        if not IsValidIp(ip):
            asn, provider_name = None, "Invalid"
            country, country_code, city, region, latitude, longitude, continent = ["Invalid", "Invalid", "Invalid", "Invalid", 0, 0, "Invalid"]
        else:
            #IP ASN Lookup
            asn, provider_name = IpAsnLookup(ip, target_ips, blockchain_obj)
            #IP Geolookup
            country, country_code, city, region, latitude, longitude, continent = [i for i in IpGeoLookup(ip, target_ips, blockchain_obj, ip_handler)]

        #Perform Analysis
        provider_name = ProviderAnalysis(providers_to_track, asn, ip, node_info, providers_short_to_object_map, country, country_code, city, region, latitude, longitude, provider_name, analysisDate, blockchain_obj)
        CountryAnalysis(countries_to_track, continent, country, country_code, city, ip, node_info, countries_short_to_object_map, analysisDate, blockchain_obj)

        #If it is validator (even if unidentified), sum validator and stake to provider dict and blockchain object.
        if node_info["is_validator"]:
            stake = 0 if not node_info["stake"] else int(node_info["stake"])
            blockchain_obj.providersData[provider_name]['Total Validators'] += 1
            blockchain_obj.providersData[provider_name]['Total Stake'] += stake
            blockchain_obj.continentData[continent]['Total Validators'] += 1
            blockchain_obj.continentData[continent]['Total Stake'] += stake
            blockchain_obj.continentData[continent]["Countries"][country]['Total Validators'] += 1
            blockchain_obj.continentData[continent]["Countries"][country]['Total Stake'] += stake

            blockchain_obj.totalStake += stake
            blockchain_obj.totalValidators += 1
        
        #Else just sum RPC to provider dict and blockchain object
        else:
            blockchain_obj.providersData[provider_name]['Total Non-Validator Nodes'] += 1
            blockchain_obj.continentData[continent]['Total Non-Validator Nodes'] += 1
            blockchain_obj.continentData[continent]["Countries"][country]['Total Non-Validator Nodes'] += 1
            blockchain_obj.totalNonValidatorNodes += 1

        #Add another node to the network and to the provider
        blockchain_obj.totalNodes += 1
        blockchain_obj.providersData[provider_name]['Total Nodes'] += 1
        blockchain_obj.continentData[continent]['Total Nodes'] += 1
        blockchain_obj.continentData[continent]["Countries"][country]['Total Nodes'] += 1

    #Calculate the percentages after a full analysis
    blockchain_obj.CalculatePercentages()
