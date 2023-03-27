import json
from ipwhois.net import Net
from ipwhois.asn import IPASN

import config.globals
from analysis.utils import IpAsnLookup, IpGeoLookup, ProviderAnalysis, CountryAnalysis
from classes.Blockchain import Blockchain, Flow


## Holds analysis functions ##
def GetNetworkProviderDistribution(providers_to_track: dict, countries_to_track: dict, providers_short_to_object_map: dict, countries_short_to_object_map: dict, blockchain_obj) -> Blockchain:
    #Get IP address JSON file
    path = f"{config.globals.BASE_DIR}/json/{blockchain_obj.target}.json"
    with open(path, "r") as f:
        json_analysis = json.load(f)
        f.close()

    # Update blockchain object analysisDate
    analysisDate = json_analysis["timestamp"] #This is purely for human-readability, no need to be date type.
    blockchain_obj.analysisDate = analysisDate
    target_ips = json_analysis["nodes"]

    print("\n\nAnalyzing %d Nodes. This may take a few minutes..." % len(target_ips), flush=True)

    #Delegate the flow runs to appropriate object and overwrite the object
    if blockchain_obj.target == "flow":
        blockchain_obj = GetFlowNetworkProviderDistribution(providers_to_track, countries_to_track, providers_short_to_object_map, blockchain_obj.target, target_ips, analysisDate)
    else:
        GetGeneralNetworkProviderDistribution(providers_to_track, countries_to_track, providers_short_to_object_map, countries_short_to_object_map, target_ips, blockchain_obj)

    print("Done.", flush=True)
    return blockchain_obj

def GetFlowNetworkProviderDistribution(providers_to_track: dict, countries_to_track: dict, short_to_object_map: dict, target_blockchain: str, target_ips: dict, analysisDate: str) -> Blockchain:
    #Overwrite blockchain_obj variable to Flow() class and return it
    blockchain_obj = Flow(target_blockchain, analysisDate)
    
    #Iterate over all IP addresses
    for ip, node_info in target_ips.items():
        #Nest the Network object building in a try/except
        try:
            #Build Network objects and set variables
            net = Net(ip)
            obj = IPASN(net)
            results = obj.lookup()
            asn = results['asn']
            provider_name = "Other" #Set provider name as Other. Will get overwritten for relevant providers defined in the file
        except Exception as e:
            #Capture unespecified IPs and set None asn
            blockchain_obj.unidentifiedIPs[ip] = target_ips[ip]
            print("\t[WARN] - Undefined IP: %s for %s" % (e, ip), flush=True)
            asn = None
            provider_name = "Unidentified"
        
        #If the ASN is in the ASN lookup, overwrite provider
        if asn in config.globals.PROVIDER_ASN_LOOKUP:
            provider_name = config.globals.PROVIDER_ASN_LOOKUP[results['asn']]['provider']
            
            #Create entry if provider hasn't yet been seen
            if provider_name not in blockchain_obj.providersData:
                blockchain_obj.providersData[provider_name] = {
                    "Execution Nodes": {"active": 0, "total": 0},
                    "Consensus Nodes": {"active": 0, "total": 0},
                    "Collection Nodes": {"active": 0, "total": 0},
                    "Verification Nodes": {"active": 0, "total": 0},
                    "Access Nodes": {"active": 0, "total": 0},
                    "Total Stake": {"active": 0, "total": 0},
                    "Total Nodes": 0,
                    "Total Inactive Nodes": 0
                }

            #Catch the providers_to_track nodes and save them to the object
            if provider_name in providers_to_track.values():
                short = list(providers_to_track.keys())[list(providers_to_track.values()).index(provider_name)]
                short_to_object_map[short].SaveProviderNode(ip, node_info)

        #Identify role parameter, stake, and key name
        role = node_info["extra_info"]["role"]
        role_param = blockchain_obj.ReturnNodeTypeQuantities(role)
        stake = 0 if not node_info["stake"] else int(float(node_info["stake"]))
        key_name = f"{role.capitalize()} Nodes"

        #Check if it meets requirements and add to general and provider stake
        if node_info["extra_info"]["is_active"]:
            role_param["active"] += 1
            blockchain_obj.totalStake["active"] += stake

            #Provider data
            blockchain_obj.providersData[provider_name][key_name]["active"] += 1
            blockchain_obj.providersData[provider_name]["Total Stake"]["active"] += stake
        
        #Else sum inactive nodes to provider dict and blockchain object
        else:
            blockchain_obj.providersData[provider_name]['Total Inactive Nodes'] += 1
            blockchain_obj.totalInactiveNodes += 1

        #Add to general and provider totals
        role_param["total"] += 1
        blockchain_obj.totalStake["total"] += stake
        blockchain_obj.totalNodes += 1

        #Provider data
        blockchain_obj.providersData[provider_name][key_name]["total"] += 1
        blockchain_obj.providersData[provider_name]["Total Stake"]["total"] += stake
        blockchain_obj.providersData[provider_name]["Total Nodes"] += 1

    #Calculate the percentages after a full analysis
    blockchain_obj.CalculatePercentages(target_ips)

    return blockchain_obj

def GetGeneralNetworkProviderDistribution(providers_to_track: dict, countries_to_track: dict, providers_short_to_object_map: dict, countries_short_to_object_map: dict, target_ips: dict, blockchain_obj: Blockchain):
    #Iterate over all IP addresses
    for ip, node_info in target_ips.items():
        #IP ASN Lookup
        asn, provider_name = IpAsnLookup(ip, target_ips, blockchain_obj)
        #IP Geolookup
        country, country_code, city, region, latitude, longitude = [i for i in IpGeoLookup(ip, target_ips, blockchain_obj)]

        #Perform Analysis
        provider_name = ProviderAnalysis(providers_to_track, asn, ip, node_info, providers_short_to_object_map, country, country_code, city, region, latitude, longitude, provider_name, blockchain_obj)
        CountryAnalysis(countries_to_track, country, country_code, city, ip, node_info, countries_short_to_object_map, blockchain_obj)

        #If it is validator (even if unidentified), sum validator and stake to provider dict and blockchain object.
        if node_info["is_validator"]:
            stake = 0 if not node_info["stake"] else int(node_info["stake"])
            blockchain_obj.providersData[provider_name]['Total Validators'] += 1
            blockchain_obj.providersData[provider_name]['Total Stake'] += stake
            blockchain_obj.countriesData[country]['Total Validators'] += 1
            blockchain_obj.countriesData[country]['Total Stake'] += stake
            blockchain_obj.totalStake += stake
            blockchain_obj.totalValidators += 1
        
        #Else just sum RPC to provider dict and blockchain object
        else:
            blockchain_obj.providersData[provider_name]['Total Non-Validator Nodes'] += 1
            blockchain_obj.countriesData[country]['Total Non-Validator Nodes'] += 1
            blockchain_obj.totalNonValidatorNodes += 1

        #Add another node to the network and to the provider
        blockchain_obj.totalNodes += 1
        blockchain_obj.providersData[provider_name]['Total Nodes'] += 1
        blockchain_obj.countriesData[country]['Total Nodes'] += 1

    #Calculate the percentages after a full analysis
    blockchain_obj.CalculatePercentages(target_ips)
