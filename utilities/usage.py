# Functions related to application usage
def PrintProviderCompletion(short_to_object_map, target):   
    print("\n\n\n-----RESULTS for %s-----" % target.upper())

    if not short_to_object_map.values():
        print("\nNo providers to track specified.")
    else:
        print("\nProvider Overview:")
        for obj in short_to_object_map.values():
            print("\n%s:" % obj.provider)
            print("\tMonitoring since %s" % (obj.objectCreationDate))
            print("\tThere are", obj.validatorCount, "VALIDATORS running on %s." % obj.provider)
            print("\tThere have been", len(obj.seenIPs), "different nodes (IPs) seen running on %s since the start of this monitoring." % obj.provider)

def PrintCountryCompletion(short_to_object_map, target, blockchain_obj):   
    if not short_to_object_map.values():
        print("\n\nNo providers to track specified.")
    else:
        print("\n\nCountries Overview:")
        for obj in short_to_object_map.values():
            print("\n%s:" % obj.country_name)
            print("\tMonitoring since %s" % (obj.objectCreationDate))
            print("\tThere are", obj.validatorCount, "VALIDATORS running out of %s." % obj.country_name)
            print("\tThere have been", len(obj.nodeDict), "different nodes (IPs) seen running on %s since the start of this monitoring." % obj.country_name)
    
    print("\n\nThere is a total of %d IPs seen on %s" % (blockchain_obj.totalNodes, target))
    print("There is a total of %d validator nodes on %s" % (blockchain_obj.totalValidators, target))
    print("%d ASNs could not be identified on %s" % (len(blockchain_obj.unidentifiedASNs), target))
    print("%d Locations could not be identified on %s" % (len(blockchain_obj.unidentifiedLocations), target))
    print("\nCheck output files in output dir, farewell")

def PrintUsage():
    print("\n-----USAGE-----")
    print("Welcome to the Blockchain Infra Analytics Tool. This tool analyzes the number",
        "of nodes of each provider specified in the PorviderLookup.json file, for a specified chain in the command line")

    print("\n\n-----PARAMETERS-----")
    print("The tool takes 1 mandatory parameter and 3 optional parameters in the following format:")
    print("\n>[MANDATORY] --blockchain=<value> -> Defines the target blockchain to analyze. Value must exist in the `json/` directory without the \".json\" extension.")
    print("\n> --providers=<val1>,<val2> -> Defines the providers for which to track nodes, based on the config/ProviderConfig.json and following",
        "the format defined on the README. Default is None.")
    print("\n> --countries=<val1>,<val2> -> Defines the countries for which to track nodes, based on the config/CountriesConfig.json and following",
        "ISO Alpha-2 country code convention. Default is None.")
    print("\n> --output -> Prints an overview of the results upon completion.")
    print("\n> --help -> Prints this message.")

    print("\n\n-----OUTPUT-----")
    print("The tool will build one file: \"output/<target_chain>/network/ProviderDistribution-<date>.json\" containing the infrasturcure analysis of the chain.")
    print("If \"--providers\" is specified, the tool will build a provider-<date>.json for every provider specified under \"output/<target_chain>/providers/\", containing a list of all nodes running on that provider.")

    print("\nFor a full description, see the README.md\n")

    exit(0)
