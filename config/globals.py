import os, json, IP2Location
import __main__

def LoadFromConfig():
    #Set the provider ASN lookup from the provider config file
    with open(f"{CONFIG_PATH}/ProviderConfig.json", "r") as f:
        provider = json.load(f)
        f.close()
    
    #Set the country from the provider config file
    with open(f"{CONFIG_PATH}/CountryConfig.json", "r") as f:
        country = json.load(f)
        f.close()

    #Set the ipinfo API token
    with open(f"{CONFIG_PATH}/keys.json", "r") as f:
        token = json.load(f)["ipinfo"]
        f.close()

    return provider, country, token

# Sets global variables used by all other files
BASE_DIR = os.path.dirname(os.path.realpath(__main__.__file__))
CONFIG_PATH = BASE_DIR + "/config/"
OUTPUT_FOLDER = "results/"
PROVIDER_ASN_LOOKUP, COUNTRY_NAME_LOOKUP, IPINFO_TOKEN = LoadFromConfig()