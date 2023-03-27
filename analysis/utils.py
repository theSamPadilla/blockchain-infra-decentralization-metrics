from ipwhois.net import Net
from ipwhois.asn import IPASN

import config.globals
from classes.Blockchain import Blockchain
from classes.Datacenter import Datacenter

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
    except Exception as e:
        #Capture unespecified IPs and set None asn
        blockchain_obj.unidentifiedASNs[ip] = target_ips[ip]
        print("\t[WARN] - Undefined IP: %s for %s" % (e, ip), flush=True)
        asn = None
        provider_name = "Unidentified"

    return asn, provider_name

def IpGeoLookup(ip: str, target_ips: dict, blockchain_obj: Blockchain) -> list:
    #Nest the IP geo lookup under a try/catch
    try:
        r = config.globals.GEO_DB.get_all(ip)
        country = config.globals.COUNTRY_NAME_LOOKUP[r.country_short]
        result = [country, r.country_short, r.city, r.region, r.latitude, r.longitude]
        print("\t[INFO] Succesful IP geo lookup.")
    except Exception as e:
        blockchain_obj.unidentifiedLocations[ip] = target_ips[ip]
        print("\t[WARN] - Error performing IP geo lookup: %s for %s" % (e, ip), flush=True)
        result = ["Unidentified", "Unidentified", "Unidentified", "Unidentified", 0, 0]

    return result

def ProviderAnalysis(providers_to_track: dict, asn:str, ip:str, node_info:dict, providers_short_to_object_map:dict, country:str, country_code:str, city:str, region:str, latitude:float, longitude:float, provider_name:str, blockchain_obj: Blockchain) -> str:
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

def CountryAnalysis(countries_to_track: dict, country: str, country_code:str, city:str, ip:str, node_info:dict, countries_short_to_object_map:dict, blockchain_obj: Blockchain):
    #Create entry for country if it hasn't yet been seen
    if country not in blockchain_obj.countriesData:
        blockchain_obj.countriesData[country] = {
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
