#!/usr/bin/python3
############################################
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
############################################
import sys

from classes.obj_constructor import MakeCountryObjects, MakeProviderObjects, MakeTargetBlockchainObject
from utilities.usage import PrintCountryCompletion, PrintProviderCompletion, PrintUsage
from utilities.setup import GetArguments
from analysis.analysis import GetNetworkProviderDistribution

## Main ##
def main(target_blockchain, providers_to_track, countries_to_track, output):
    print("\n-----RUNTIME-----")
    
    #Make target blockchain and provider objects if providers_to_track not empty
    blockchain_obj = MakeTargetBlockchainObject(target_blockchain)
    providers_short_to_object_map = {}
    countries_short_to_object_map = {}
    if providers_to_track:
        providers_short_to_object_map = MakeProviderObjects(providers_to_track, blockchain_obj)
    if countries_to_track:
        countries_short_to_object_map = MakeCountryObjects(countries_to_track, blockchain_obj)

    #Analyze all nodes for provided blockchain (overwrites if flow)
    blockchain_obj = GetNetworkProviderDistribution(providers_to_track, countries_to_track, providers_short_to_object_map, countries_short_to_object_map, blockchain_obj)

    #Save objects
    print("\n\nSaving Objects...", flush=True)
    blockchain_obj.Save()
    for obj in providers_short_to_object_map.values():
        obj.SaveObject(blockchain_obj)
    for obj in countries_short_to_object_map.values():
        obj.SaveObject(blockchain_obj)
    print("Done.", flush=True)

    #Output JSON for trackable providers and countries
    print("\n\nOutputting information to JSON files...")
    for obj in providers_short_to_object_map.values():
        obj.OutputJSONInfo(blockchain_obj)
    for obj in countries_short_to_object_map.values():
        obj.OutputJSONInfo(blockchain_obj)
    blockchain_obj.SaveProviderDistribution()
    print("Done.", flush=True)

    #Output results flag passed
    if output:
        PrintProviderCompletion(providers_short_to_object_map, target_blockchain)
        PrintCountryCompletion(countries_short_to_object_map, target_blockchain, blockchain_obj)

## Main Caller ##
if __name__ == "__main__":
    if len(sys.argv) > 6:
        print("ERROR: Too many parameters.\n")
        PrintUsage()
    else:
        exec_mode, providers_to_track, countries_to_track, output = GetArguments(sys.argv)
        main(exec_mode, providers_to_track, countries_to_track, output)