from ipwhois.net import Net
from ipwhois.asn import IPASN
import ipinfo #type: ignore

import config.globals
from classes.Blockchain import Blockchain, Flow
from classes.Datacenter import Datacenter

#NOTE: This is a compound object. Simple assignment will pass a reference to the object defined in dict_initial_values.py
#NOTE: To pass a net deepcopy use the .deepcopy() method.
from classes.dict_initial_values import flow_total_stake
from copy import deepcopy

## Helper Functions ##
def IpAsnLookup(ip: str, target_ips: dict, blockchain_obj: Blockchain) -> tuple:
    #Nest the Network object building in a try/except
    try:
        #Build Network objects and set variables
        net = Net(ip)
        obj = IPASN(net)
        results = obj.lookup()
        asn = results['asn']
        provider_name = "Other" #Set provider name as Other. Will get overwritten for relevant providers defined in the file
        print(f"\t[INFO - {blockchain_obj.target}] Succesful ASN lookup")
    except Exception as e:
        #Capture unespecified IPs and set None asn
        blockchain_obj.unidentifiedASNs[ip] = target_ips[ip]
        print("\t[WARN - %s] - Undefined IP: %s for %s" % (blockchain_obj.target, e, ip), flush=True)
        asn = None
        provider_name = "Unidentified"

    return asn, provider_name

def IpGeoLookup(ip: str, target_ips: dict, blockchain_obj: Blockchain, ip_handler: ipinfo.Handler) -> list:
    #Nest the IP geo lookup under a try/catch
    try:
        #Set Ipinfo handler
        ip_handler = ipinfo.getHandler(config.globals.IPINFO_TOKEN)
        r = ip_handler.getDetails(ip).all
        country = config.globals.COUNTRY_NAME_LOOKUP[r["country"]]
        result = [country, r["country"], r["city"], r["region"], r["latitude"], r["longitude"], r["continent"]["name"]]
        print(f"\t[INFO - {blockchain_obj.target}] Succesful GEO lookup")
    except Exception as e:
        blockchain_obj.unidentifiedLocations[ip] = target_ips[ip]
        print("\t[WARN - %s] Error performing IP geo lookup: %s for %s" % (blockchain_obj.target, e, ip), flush=True)
        result = ["Unidentified", "Unidentified", "Unidentified", "Unidentified", 0, 0, "Unidentified"]

    return result

def ProviderAnalysis(providers_to_track: dict, asn:str, ip:str, node_info:dict, providers_short_to_object_map:dict, country:str, country_code:str, city:str, region:str, latitude:float, longitude:float, provider_name:str, analysisDate: str, blockchain_obj: Blockchain) -> str:
    #If the ASN is in the ASN lookup, overwrite 'Other' provider
    if asn in config.globals.PROVIDER_ASN_LOOKUP:
        provider_name = config.globals.PROVIDER_ASN_LOOKUP[asn]['provider']
        
        #Create entry if provider hasn't yet been seen
        if provider_name not in blockchain_obj.providersData:
            blockchain_obj.providersData[provider_name] = {
                "Total Non-Validator Nodes": 0,
                "Total Validators": 0,
                "Total Nodes": 0,
                "Total Stake": 0
            }

        #Catch the providers_to_track nodes and save them to the object
        if provider_name in providers_to_track.values():
            short = list(providers_to_track.keys())[list(providers_to_track.values()).index(provider_name)]
            provider_obj = providers_short_to_object_map[short]
            
            #Create Datacenter object
            datacenter_obj = Datacenter(country, country_code, city, region, latitude, longitude, provider_obj)
            
            #If object exists, overwrite datacenter object. Else add to list and count node.
            if datacenter_obj in provider_obj.datacenters:
                datacenter_obj = provider_obj.datacenters[provider_obj.datacenters.index(datacenter_obj)]
            else:
                provider_obj.datacenters.append(datacenter_obj)

            #Save node to datacenter and update totals
            datacenter_obj.SaveDatacenterNode(ip, node_info)
            provider_obj.UpdateTotals(ip, node_info)
    
    #Returns overwritten result if found
    return provider_name

def CountryAnalysis(countries_to_track: dict, continent: str, country: str, country_code:str, city:str, ip:str, node_info:dict, countries_short_to_object_map:dict, analysisDate: str, blockchain_obj: Blockchain):
    #Create entry for country inside of the appropriave continent if it hasn't yet been seen
    if continent not in blockchain_obj.continentData:
        blockchain_obj.continentData[continent] = {
            "Total Non-Validator Nodes": 0,
            "Total Validators": 0,
            "Total Nodes": 0,
            "Total Stake": 0,
            "Countries": {
                country: {
                    "Total Non-Validator Nodes": 0,
                    "Total Validators": 0,
                    "Total Nodes": 0,
                    "Total Stake": 0
                }
            }
        }
    #Create entry for country inside continent if not yet seen
    elif country not in blockchain_obj.continentData[continent]["Countries"]:
            blockchain_obj.continentData[continent]["Countries"][country] = {
                    "Total Non-Validator Nodes": 0,
                    "Total Validators": 0,
                    "Total Nodes": 0,
                    "Total Stake": 0
            }

    #Catch the countries_to_track nodes, add city, and save them to country object
    if country_code in countries_to_track:
        country_obj = countries_short_to_object_map[country_code]
        country_obj.cities.add(city)
        country_obj.SaveCountryNode(ip, node_info)

def FlowProviderAnalysis(providers_to_track: dict, asn:str, ip:str, node_info:dict, providers_short_to_object_map:dict, country:str, country_code:str, city:str, region:str, latitude:float, longitude:float, provider_name:str, analysisDate: str, blockchain_obj: Flow, role: str) -> str:
    #If the ASN is in the ASN lookup, overwrite 'Other' provider
    if asn in config.globals.PROVIDER_ASN_LOOKUP:
        provider_name = config.globals.PROVIDER_ASN_LOOKUP[asn]['provider']
        
        #Create entry if provider hasn't yet been seen
        if provider_name not in blockchain_obj.providersData:
            blockchain_obj.providersData[provider_name] = {
                "Execution Nodes": {"active": 0, "total": 0},
                "Consensus Nodes": {"active": 0, "total": 0},
                "Collection Nodes": {"active": 0, "total": 0},
                "Verification Nodes": {"active": 0, "total": 0},
                "Access Nodes": {"active": 0, "total": 0},
                "Total Stake": deepcopy(flow_total_stake),
                "Total Nodes": 0,
                "Total Inactive Nodes": 0
            }

        #Catch the providers_to_track nodes, update analysis, and save them to the object
        if provider_name in providers_to_track.values():
            short = list(providers_to_track.keys())[list(providers_to_track.values()).index(provider_name)]
            provider_obj = providers_short_to_object_map[short]
            
            #Create Datacenter object
            datacenter_obj = Datacenter(country, country_code, city, region, latitude, longitude, provider_obj)
            
            #If object exists, overwrite datacenter object. Else add to list and count node.
            if datacenter_obj in provider_obj.datacenters:
                datacenter_obj = provider_obj.datacenters[provider_obj.datacenters.index(datacenter_obj)]
            else:
                provider_obj.datacenters.append(datacenter_obj)

            #Save node to datacenter and update totals
            datacenter_obj.SaveDatacenterNode(ip, node_info, role)
            provider_obj.UpdateTotals(ip, node_info, role)

    #Returns overwritten result if found
    return provider_name

def FlowCountryAnalysis(countries_to_track: dict, continent: str, country: str, country_code:str, city:str, ip:str, node_info:dict, countries_short_to_object_map:dict, analysisDate: str, blockchain_obj: Flow, role: str):
    #Create entry for country inside of the appropriave continent if it hasn't yet been seen
    if continent not in blockchain_obj.continentData:
        blockchain_obj.continentData[continent] = {
            "Execution Nodes": {"active": 0, "total": 0},
            "Consensus Nodes": {"active": 0, "total": 0},
            "Collection Nodes": {"active": 0, "total": 0},
            "Verification Nodes": {"active": 0, "total": 0},
            "Access Nodes": {"active": 0, "total": 0},
            "Total Stake": deepcopy(flow_total_stake),
            "Total Nodes": 0,
            "Total Inactive Nodes": 0,
            "Countries": {
                country: {
                    "Execution Nodes": {"active": 0, "total": 0},
                    "Consensus Nodes": {"active": 0, "total": 0},
                    "Collection Nodes": {"active": 0, "total": 0},
                    "Verification Nodes": {"active": 0, "total": 0},
                    "Access Nodes": {"active": 0, "total": 0},
                    "Total Stake": deepcopy(flow_total_stake),
                    "Total Nodes": 0,
                    "Total Inactive Nodes": 0
                }
            }
        }
    #Create entry for country inside continent if not yet seen
    elif country not in blockchain_obj.continentData[continent]["Countries"]:
            blockchain_obj.continentData[continent]["Countries"][country] = {
                "Execution Nodes": {"active": 0, "total": 0},
                "Consensus Nodes": {"active": 0, "total": 0},
                "Collection Nodes": {"active": 0, "total": 0},
                "Verification Nodes": {"active": 0, "total": 0},
                "Access Nodes": {"active": 0, "total": 0},
                "Total Stake": deepcopy(flow_total_stake),
                "Total Nodes": 0,
                "Total Inactive Nodes": 0
            }

    #Catch the countries_to_track nodes, add city, and save them to country object
    if country_code in countries_to_track:
        country_obj = countries_short_to_object_map[country_code]
        country_obj.cities.add(city)
        country_obj.SaveCountryNode(ip, node_info, role)

def IsValidIp(ip) -> bool:
    list_172 = ["172.16.", "172.17.", "172.18.", "172.19.", "172.20.", "172.21.", "172.22.", "172.23.", "172.24.", "172.25.", "172.26.", "172.27.", "172.28.", "172.29.", "172.30.", "172.31."]
    if (ip == "") or (ip == "0.0.0.0") or (ip == "1.1.1.1") or (ip[:3] == "10.") or (ip[:8] == "192.168.") or (ip[:7] in list_172) or ("." not in ip and ":" not in ip) or (ip[:4] == "127."):
        return False
    return True