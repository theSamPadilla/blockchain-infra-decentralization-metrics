import pickle, os, json

import config.globals
from classes.Blockchain import Blockchain
from classes.Country import Country
from classes.Provider import Provider

## Object Creation Functions ##
def MakeTargetBlockchainObject(target_blockchain):
    #Set paths
    p = "{base}/memory/{target}/blockchain_object.pickle".format(base=config.globals.BASE_DIR, target=target_blockchain)
    
    #First time creating the object.
    if not os.path.exists(p):
        print("Building %s object for the first time." % target_blockchain, flush=True)
        blockchain_obj = Blockchain(target_blockchain)
        print("Done.", flush=True)
    
    #Loading from memory
    else:
        print("Fetching %s object from memory..." % target_blockchain, flush=True)
        with open(p,'rb') as f:
            blockchain_obj = pickle.load(f)
            f.close()

        blockchain_obj.providersData = {"Other": {"Total RPC Nodes": 0, "Total Validators": 0, "Total Stake": 0}}

    return blockchain_obj

def MakeProviderObjects(providers_to_track: dict, blockchain_obj) -> dict:
    short_to_object_map = {} #* short -> provider object

    print("\n\nBuilding provider objects...", flush=True)

    for short in providers_to_track:
        #Set path and provider name
        path = "{base}/memory/{target}/providers/{short}_object.pickle".format(base=config.globals.BASE_DIR, target=blockchain_obj.target, short=short)
        name = providers_to_track[short]

        #First time creating the object.
        if not os.path.exists(path):
            print("\tBuilding provider object for %s provider the first time." % name, flush=True)
            obj = Provider(short, name, blockchain_obj)
            print("\tDone.", flush=True)

        #Loading from memory
        else:
            print("\tFetching provider object for %s from memory..." % name, flush=True)
            with open(path,'rb') as f:
                obj = pickle.load(f)
                f.close()
            print("\tDone.", flush=True)

        #Append object to list
        short_to_object_map[short] = obj

    return short_to_object_map

def MakeCountryObjects(countries_to_track: dict, blockchain_obj) -> dict:
    short_to_object_map = {} #* country_code -> country object

    print("\n\nBuilding provider objects...", flush=True)

    for country_code in countries_to_track:
        #Set path and provider name
        path = "{base}/memory/{target}/countries/{code}_object.pickle".format(base=config.globals.BASE_DIR, target=blockchain_obj.target, code=country_code)
        country_name = countries_to_track[country_code]

        #First time creating the object.
        if not os.path.exists(path):
            print("\tBuilding country object for %s provider the first time." % country_name, flush=True)
            obj = Country(country_name=country_name, code=country_code, target_chain=blockchain_obj)
            print("\tDone.", flush=True)

        #Loading from memory
        else:
            print("\tFetching country object for %s from memory..." % country_name, flush=True)
            with open(path,'rb') as f:
                obj = pickle.load(f)
                f.close()
            print("\tDone.", flush=True)

        #Append object to list
        short_to_object_map[country_code] = obj

    return short_to_object_map
