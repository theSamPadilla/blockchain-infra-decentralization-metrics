import os
import config.globals
from utilities.usage import PrintUsage

def LoadConfigFilesAndGetAllowedProviders() -> list:
    """Loads providers from ProvidersConfig.json file"""
    #Get allowed provider set
    allowed_providers = {} #*short.upper() -> provider_name
    for provider in config.globals.PROVIDER_ASN_LOOKUP.values():
        if "short" in provider:
            allowed_providers[provider['short'].upper()] = provider["provider"]

    return allowed_providers

def GetBlockchainNames() -> list:
    """Gets the possible parameters for the `--blockchain` argument from the `json/` folder"""
    files = os.listdir(f"{config.globals.BASE_DIR}/json/")
    files.remove("sample.json")
    return [i[:-5] for i in files]

def GetArguments(args: list) -> tuple:
    #Print usage and exit
    if "--help" in args:
        PrintUsage()
            
    #Disregard the first arg (filename)
    args.pop(0)

    #Set arg constraints
    allowed_blockchains = GetBlockchainNames()
    if "--blockchain" not in ''.join(args):
        print("ERROR: Missing mandatory \"--blockchain\" flag.")
        print("\tValid values are:", allowed_blockchains)
        exit(1)
    
    allowed_commands = {"--providers", "--blockchain", "--countries", "--output", "--help"}
    allowed_providers = LoadConfigFilesAndGetAllowedProviders()

    #Set output folder and flag
    output_message = False
    if "--output" in ''.join(args):
        output_message = True
        args.remove("--output")
    
    #Initialize list of providers and countries to track
    providers_to_track = {} #* short -> provider_name
    countries_to_track = {} #* two letter code -> country name

    #Get commands and values
    for arg in args:
        buff = arg.split("=")

        #Check for good format
        if len(buff) != 2:
            print("ERROR: The argument %s has the wrong format." % arg)
            print("\tValid format is: \"--<argument>=<value>\"")
            exit(1)

        #Unpack command and value
        command, value = buff[0], buff[1]

        #Check that command is supported
        if command not in allowed_commands:
            print("ERROR: The argument %s is not supported." % command)
            print("\tValid arguments are:", allowed_commands)
            exit(1)

        #Target blockchain
        if command == "--blockchain":
            #Check for allowed blockchain
            if value not in allowed_blockchains:
                print("ERROR: There is no file named %s.json in the `json/` folder. Can't perform analysis." % value)
                print("\tValid values are:", allowed_blockchains)
                exit(1)
            else:
                target_blockchain = value

        #Providers
        elif command == "--providers":
            providers = value.split(",")
        
            #Check for valid providers
            for short in providers:
                short = short.upper()
                if short not in allowed_providers:
                    print("ERROR: Wrong format or the provider %s is not a valid provider." % short)
                    print("\tThe expected format is --providers=<val1>,<val2>,... (no spaces between values)")
                    print("\tValid providers, based on the config file, are:", list(allowed_providers.keys()))
                    exit(1)

                #Add to list
                else:
                    providers_to_track[short] = allowed_providers[short]

                #Providers
        elif command == "--countries":
            countries = value.split(",")
        
            #Check for valid Countries 
            for short in countries:
                short = short.upper()
                if short not in config.globals.COUNTRY_NAME_LOOKUP.keys():
                    print("ERROR: Wrong format or the country %s is not a valid ISO Alpha-2 country code." % short)
                    print("\tThe expected format is --countries=<val1>,<val2>,... (no spaces between values)")
                    print("\tValid ISO Alpha-2 country codes and their respective countries are:", config.globals.COUNTRY_NAME_LOOKUP)
                    exit(1)

                #Add to list
                else:
                    countries_to_track[short] = config.globals.COUNTRY_NAME_LOOKUP[short]

    return target_blockchain, providers_to_track, countries_to_track, output_message
