import json 

with open("validators.json") as f:
    validators = json.load(f)
    f.close()

addresses = set()
i = 0
for val in validators["result"]["validators"]:
    if val['address'] in addresses:
        print("There is a repeated address at counter %d -> Address: %s" % i, var['address'])
        exit(0)
    i += 1
    
print("No repeated addresses in %d validators" % i)