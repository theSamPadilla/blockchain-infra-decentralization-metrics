import json, toml

with open("addressbook.json") as f:
    addr = json.load(f)
    f.close()

config = toml.load("../test/config.toml")

final_list = []
seen = set()
for i in addr['addrs']:
    addy = i['addr']
    if len(addy['ip'].split(':')) == 1:
        if addy['ip'] not in seen and i['last_success'] != "0001-01-01T00:00:00Z":
            addy_str = "{}@{}".format(addy['id'], addy['ip'])
            final_list.append(addy_str)
            seen.add(addy['ip'])

config['seeds'] = final_list
f = open("../test/config.toml", "w+")
toml.dump(config, f)
f.close()