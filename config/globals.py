import os, json, IP2Location
import __main__

def LoadProviderAndCountry ():
    #Set the provider ASN lookup from the provider config file
    with open(f"{CONFIG_PATH}/ProviderConfig.json", "r") as f:
        provider = json.load(f)
        f.close()
    
    #Set the provider ASN lookup from the provider config file
    with open(f"{CONFIG_PATH}/CountryConfig.json", "r") as f:
        country = json.load(f)
        f.close()
    return provider, country

# Sets global variables used by all other files
BASE_DIR = os.path.dirname(os.path.realpath(__main__.__file__))
GEO_DB = IP2Location.IP2Location(os.path.join(f"{BASE_DIR}/lib/IP2Location-Python-master/data", "IP-COUNTRY-REGION-CITY-LATITUDE-LONGITUDE-ZIPCODE-TIMEZONE-ISP-DOMAIN-NETSPEED-AREACODE-WEATHER-MOBILE-ELEVATION-USAGETYPE-ADDRESSTYPE-CATEGORY-SAMPLE.BIN"))
CONFIG_PATH = BASE_DIR + "/config/"
OUTPUT_FOLDER = "results/"
PROVIDER_ASN_LOOKUP, COUNTRY_NAME_LOOKUP = LoadProviderAndCountry()