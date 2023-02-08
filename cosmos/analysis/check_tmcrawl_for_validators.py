import json

###################################
# CLEAN #
###################################
#Open JSONs
with open("info/tmcrawl_result.json") as tm, open("info/tendermint_validators.json") as va, open("info/query_validators.json") as op:
    tmcrawl = json.load(tm)
    validators = json.load(va)
    operators = json.load(op)
    tm.close()
    va.close()
    op.close()

#Iterate through tmcrawl results and clean them
tmcrawl_seen_IP_to_info = {}
clean_nodes = []
nodes_with_id = []
nodes_with_address = []
nodes_with_pubkey = []
nodes_with_voting_power = []

for node in tmcrawl['nodes']:
    #Disregard empty IP Addresses
    if node["ip"] == "":
        continue

    #Get node info
    ip = node["ip"]
    address = node["validator_address"]
    node_id = node["id"]
    voting_power = node ["validator_voting_power"]
    pubkey = node["validator_pubkey_byte"]

    #Set seen object
    tmcrawl_seen_IP_to_info[ip] = {
        "ip": ip,
        "id": node_id,
        "address": address,
        "latest_block": node["sync_info"]["latest_block_height"],
        "pub_key_bytes": pubkey,
        "pub_key_address": node["validator_pubkey_address"],
        "voting_power": voting_power
    }

    #Add validator to each respective clean list
    if address != "":
        nodes_with_address.append(node)
    if node_id != "":
        nodes_with_id.append(node)
    if pubkey != None:
        nodes_with_pubkey.append(node)
    if voting_power > 0:
        nodes_with_voting_power.append(node)

    clean_nodes.append(node)

#Write clean tmcrawl result variations
json_object1 = json.dumps(clean_nodes, indent=4)
json_object2 = json.dumps(nodes_with_id, indent=4)
json_object3 = json.dumps(nodes_with_address, indent=4)
json_object4 = json.dumps(nodes_with_pubkey, indent=4)
json_object5 = json.dumps(nodes_with_voting_power, indent=4)
 
# Writing json
with open("clean/clean_tmcrawl_results.json", "w") as out1, open("clean/id_tmcrawl.json", "w") as out2, open("clean/address_tmcrawl.json", "w") as out3, open("clean/pubkey_tmcrawl.json", "w") as out4, open("clean/voting_power_tmcrawl.json", "w") as out5:
    out1.write(json_object1)
    out2.write(json_object2)
    out3.write(json_object3)
    out4.write(json_object4)
    out5.write(json_object5)
    out1.close()
    out2.close()
    out3.close()
    out4.close()
    out5.close()

###################################
# ANALYZE #
###################################
#Get map of pubkey to operator addresses info
val_oper_key_to_info = {v["consensus_pubkey"]["key"]: v for v in operators["validators"]}

#Make set of top 175 validators for lookup
top_175_validators_pubkey_to_address = {v["pub_key"]["value"] for v in validators["result"]["validators"]}

#Reformat tmcrawl seen lookup dictionary to have pubkeys as keys
seen_pub_keys_to_info = {v["pub_key_bytes"]: v for k, v in tmcrawl_seen_IP_to_info.items() if v["pub_key_bytes"] is not None}

#Iterate through ALL validators
identified_total_validators = {}
identified_top175_validators = {}

for val in operators["validators"]:
    operator_address = val["operator_address"]
    consensus_pubkey = val["consensus_pubkey"]["key"]
    
    #Look for seen pub keys in tmcrawl, grab additional information
    if consensus_pubkey in seen_pub_keys_to_info:
        ip = seen_pub_keys_to_info[consensus_pubkey]["ip"]
        tmcrawl_seen_IP_to_info[ip]["validator_operator_address"] = operator_address
        tmcrawl_seen_IP_to_info[ip]["validator_tokens"] = val["tokens"]
        tmcrawl_seen_IP_to_info[ip]["validator_delegator_shares"] = val["delegator_shares"]
        tmcrawl_seen_IP_to_info[ip]["validator_description"] = val["description"]

        #Write final results
        if consensus_pubkey in top_175_validators_pubkey_to_address:
            identified_top175_validators[ip] = tmcrawl_seen_IP_to_info[ip]
        
        identified_total_validators[ip] = tmcrawl_seen_IP_to_info[ip]

###################################
# WRITE #
###################################
#Save and Print results
json_result_175 = json.dumps(identified_top175_validators, indent=4)
json_result_total = json.dumps(identified_total_validators, indent=4)
 
# Writing json
with open("results/top175_identified_validators.json", "w") as out1, open("results/all_identified_validators.json", "w") as out2:
    out1.write(json_result_175)
    out2.write(json_result_total)
    out1.close()
    out2.close()

print("\nCleaned tmcrawl results from %d to only %d nodes/IPs (-%d)." % (len(tmcrawl['nodes']), len(clean_nodes), len(tmcrawl['nodes'])-len(clean_nodes)))

print("\nFound %d nodes with IP and ID" % len(nodes_with_id))
print("Found %d nodes with IP and Address" % len(nodes_with_address))
print("Found %d nodes with IP and Pubkey" % len(nodes_with_pubkey))
print("Found %d nodes with IP and voting power" % len(nodes_with_voting_power))

print("\nFound %d top 175 validators in tmcrawl." % len(identified_top175_validators))
print("Found %d total validators in tmcrawl." % len(identified_total_validators))


print("\nTop 175:")
for k, v in identified_top175_validators.items():
    print("%s:\n%s" % (k, v))
    print()

print("\n\nTotal:")
for k, v in identified_total_validators.items():
    print("%s:\n%s" % (k, v))
    print()