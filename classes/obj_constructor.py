from classes.Blockchain import Blockchain
from classes.Country import Country
from classes.Provider import Provider

## Object Creation Functions ##
def MakeTargetBlockchainObject(target_blockchain):
    #First time creating the object.
    print("Building %s object for the first time." % target_blockchain, flush=True)
    blockchain_obj = Blockchain(target_blockchain)
    print("Done.", flush=True)
    
    return blockchain_obj

def MakeProviderObjects(providers_to_track: dict, blockchain_obj) -> dict:
    short_to_object_map = {} #* short -> provider object

    print("\n\nBuilding provider objects...", flush=True)

    for short in providers_to_track:
        name = providers_to_track[short]

        #First time creating the object.
        print("\tBuilding provider object for %s provider the first time." % name, flush=True)
        obj = Provider(short, name, blockchain_obj)
        print("\tDone.", flush=True)

        #Append object to list
        short_to_object_map[short] = obj

    return short_to_object_map

def MakeCountryObjects(countries_to_track: dict, blockchain_obj) -> dict:
    short_to_object_map = {} #* country_code -> country object

    print("\n\nBuilding provider objects...", flush=True)

    for country_code in countries_to_track:
        country_name = countries_to_track[country_code]

        #First time creating the object.
        print("\tBuilding country object for %s provider the first time." % country_name, flush=True)
        obj = Country(country_name=country_name, code=country_code, target_chain=blockchain_obj)
        print("\tDone.", flush=True)

        #Append object to list
        short_to_object_map[country_code] = obj

    return short_to_object_map
