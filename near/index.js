
import fetch from 'node-fetch';
import process from 'node:process';
import fs from 'fs';

// holds network status
var networkStatusJson;
// global list of nodes and IP addresses
var nodeListAddrArr = [];
// global list of known producer accounts
var knownProducersAccountsArr = [];
var validatorsArr = [];
var validatorsStakeArr = [];

var promisesArr = [];

// Get network status, contains producer list
const getNetworkStatus = async function() {
    const responseStatus = await fetch('https://rpc.mainnet.near.org/status');
    const dataStatus = await responseStatus.json();
    //console.log(JSON.stringify(dataStatus));
    for (const validator of dataStatus.validators) {
        validatorsArr.push(validator.account_id);
    }
}

const getValidatorStake = async function() {

    var rpcBody = {
        "jsonrpc": "2.0",
        "id": "dontcare",
        "method": "validators",
        "params": [null]
      };
    const rpcResponse = await fetch('https://rpc.mainnet.near.org', {
        method: 'post',
        body: JSON.stringify(rpcBody),
        headers: {'Content-Type': 'application/json'}
    });
    const validatorsJson = await rpcResponse.json();
    console.log("Current validators: " + validatorsJson.result.current_validators.length);
    for (const validator of validatorsJson.result.current_validators) {
        validatorsStakeArr[validator.account_id] = validator;
    }
}

const traverseNodes = async function() {
    //return await getNetworkInfo();
    const data = await getNetworkInfo();
    return data;
}

// Retrieve node information - Starts off with the Near.org Mainnet RPC endpoint
const getNetworkInfo = async function() { 

    var networkInfo; 
    var networkInfoJson;
    var networkUrl = "https://rpc.mainnet.near.org/network_info";

    try {
        networkInfo = await fetch(networkUrl);
        networkInfoJson = await networkInfo.json();
        //console.log(JSON.stringify(networkInfoJson));
    } catch(e) {
        console.log(e);
    } 

    for (const peer of networkInfoJson.active_peers) {
        nodeListAddrArr[peer.id] = peer.addr;
        console.log(peer.id + ": " + peer.addr);
        promisesArr.push(getNodeInfo(peer.addr, 1));
    }

    for (const producer of networkInfoJson.known_producers) {
        //knownProducersAccountsArr[producer.peer_id] = producer.account_id;
        knownProducersAccountsArr[producer.account_id] = producer.peer_id;
        console.log(producer.peer_id + ": " + producer.account_id);
        if(nodeListAddrArr[producer.peer_id] !== undefined) {
            //console.log("Producer found! " + producer.account_id + ": " + nodeListAddrArr[producer.peer_id]);
        }
    }
    return true;
}


const getNodeInfo = async function(nodeAddr, level) { 

    // get the IP of the node, without port
    var nodeUrl = nodeAddr.substring(0, nodeAddr.indexOf(":"));
    nodeUrl = nodeUrl + ":3030"; // 3030 is the default RPC port, it is our best guess 
    console.log(nodeUrl);
    var nodeNetworkInfo;
    var nodeNetworkInfoJson;

    try { 
        nodeNetworkInfo = await fetch("http://" + nodeUrl + "/network_info");
        nodeNetworkInfoJson = await nodeNetworkInfo.json();
        //console.log(JSON.stringify(nodeNetworkInfoJson));
    } catch(e) {
        //console.log(e);
        //console.log("Unable to connect to: " + nodeUrl);
        return;
    } 

    
    for (const peer of nodeNetworkInfoJson.active_peers) {
        if(nodeListAddrArr[peer.id] !== undefined) {
            //console.log("Node has been already identified: " + peer.id);
        } else {
            nodeListAddrArr[peer.id] = peer.addr;
            console.log(peer.id + ": " + peer.addr);
            if(level < 3) {
                promisesArr.push(getNodeInfo(peer.addr, level+1));
            }            
        }
        
    }

    for (const producer of nodeNetworkInfoJson.known_producers) {
        if(knownProducersAccountsArr[producer.account_id] !== undefined) {
            //console.log("Producer has been already identified: " + producer.peer_id);
            //if(nodeListAddrArr[producer.peer_id] !== undefined) {
                //console.log("Producer found! " + producer.account_id + ": " + nodeListAddrArr[producer.peer_id]);
            //}
        } else {
            //knownProducersAccountsArr[producer.peer_id] = producer.account_id;
            knownProducersAccountsArr[producer.account_id] = producer.peer_id;
            console.log(producer.peer_id + ": " + producer.account_id);
            if(nodeListAddrArr[producer.peer_id] !== undefined) {
                //console.log("Producer found! " + producer.account_id + ": " + nodeListAddrArr[producer.peer_id]);
            }
        }
        
    }
}

async function runProcess() {

    promisesArr.push(await getNetworkStatus());
    promisesArr.push(await getValidatorStake());    
    promisesArr.push(await traverseNodes());

    //Promise.allSettled(promisesArr).
    //    then((results) => results.forEach((result) => console.log(result.status))).
    //    then(console.log("Completed"));

    const allPromise = Promise.all(promisesArr);
    allPromise.then(values => {
        // console.log(values); // [valueOfPromise1, valueOfPromise2, ...]

        // console.log("\n\n********\n\n");
        // console.log("\n\nnodeListAddrArr: " + Object.keys(nodeListAddrArr).length);
        // console.log(nodeListAddrArr);
        // console.log("\n\nknownProducersAccountsArr: " + Object.keys(knownProducersAccountsArr).length);
        // console.log(knownProducersAccountsArr);
        // console.log("\n\nvalidatorsArr: " + validatorsArr.length);
        // console.log(validatorsArr);
        // console.log("\n\nvalidatorsStakeArr: " + Object.keys(validatorsStakeArr).length);
        // console.log(validatorsStakeArr);
        

        console.log("\n\n********\n\n");

        
        var i=1;
        const yocto = 1000000000000000000000000
        var jsonOutput = {};
        jsonOutput.timestamp = new Date().toISOString().replace(/T/, ' ').replace(/\..+/, '');
        jsonOutput.collection_method = "api_and_crawl";
        jsonOutput.chain_data = "NEAR staking validators";
        jsonOutput.nodes = {};

        console.log("\n\Number of validators: " + Object.keys(validatorsStakeArr).length);
        var validatorsStakeArrKeys = Object.keys(validatorsStakeArr);
        var totalStaked = 0;
        for (const validatorAccountId of validatorsStakeArrKeys) {

            //console.log(validatorAccountId);
            var validatorStakeObj = validatorsStakeArr[validatorAccountId];
            //console.log(validatorStakeObj);
            var validator = validatorStakeObj.account_id;
            var validatorStake = null;
            if(validatorStakeObj !== undefined) {
                validatorStake = Number(validatorStakeObj.stake) / yocto; //yocto division 10^24
            }
            var validatorPeerId = knownProducersAccountsArr[validator];
            var validatorIP = null;
            if(validatorPeerId !== undefined) {
                validatorIP = nodeListAddrArr[validatorPeerId];
                if(validatorIP !== undefined) {
                    validatorIP = validatorIP.substring(0, validatorIP.indexOf(":"));
                }
            }
            totalStaked += validatorStake;
            console.log(i + "," + validator + "," + validatorPeerId + "," + validatorIP + "," + validatorStake);
            i++;

            // formatted json object
            var jsonObj = {};
            jsonObj.is_validator = true;
            jsonObj.stake = validatorStake;
            jsonObj.address = validatorPeerId;
            jsonObj.extra_info = {};

            // add stake to prveious IP if already seen
            if (jsonOutput.nodes.hasOwnProperty(validatorIP)) {
                jsonOutput.nodes[validatorIP].stake += validatorStake;
                if (Object.keys(jsonOutput.nodes[validatorIP].extra_info).length === 0) {
                    jsonOutput.nodes[validatorIP].extra_info["other_addresses"] = [];
                }
                jsonOutput.nodes[validatorIP].extra_info["other_addresses"].push(validatorPeerId);
            } else { // else add object for the first time
                jsonOutput.nodes[validatorIP] = jsonObj;
            }
        }
        console.log("Total staked: " + totalStaked);

        // Get ouput path and save result to the file
        fs.readFile('./config/SettingsConfig.json', (err, data) => {
            if (err) throw err;
          
            const config = JSON.parse(data);
            fs.writeFileSync(`${config.output_folder}/near.json`, JSON.stringify(jsonOutput, null, 4));
          });

      }).catch(error => {
        console.log(error);  // rejectReason of any first rejected promise
      });

}

runProcess();
 