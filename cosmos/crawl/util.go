package crawl

import (
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net"
	"net/url"
	"os"
	"strings"
	"time"

	"github.com/harwoeck/ipstack"
	"github.com/rs/zerolog/log"
	"github.com/tendermint/tendermint/crypto"
	"github.com/tendermint/tendermint/crypto/tmhash"
	"github.com/tendermint/tendermint/p2p"

	httpclient "github.com/tendermint/tendermint/rpc/client/http"
)

func newRPCClient(remote string) *httpclient.HTTP {
	//Add "tcp" to remote
	var remoteAddr = fmt.Sprintf("tcp://%s", remote)
	httpClient, err := httpclient.NewWithTimeout(remoteAddr, "/websocket", 2)
	if err != nil {
		log.Err(err).Str("Failed to create json RPC client with address", remoteAddr)
	}

	return httpClient
}

func parseValidatorsJSON(path string) {
	type validatorObject struct {
		Address string `json:"address"`
		ID      p2p.ID
		PubKey  struct {
			Type  string `json:"type"`
			Value string `json:"value"`
		} `json:"pub_key"`
		VotingPower      string `json:"voting_power"`
		ProposerPriority string `json:"proposer_priority"`
	}

	file, err1 := os.Open(path)
	if err1 != nil {
		fmt.Printf("Error while reading file at %v\n", path)
		fmt.Println("error: ", err1)
		os.Exit(1)
	}
	defer file.Close()

	byteVal, _ := ioutil.ReadAll(file)
	var m map[string]interface{}

	err2 := json.Unmarshal([]byte(byteVal), &m)
	if err2 != nil {
		fmt.Println("error:", err2)
		os.Exit(1)
	}

	for _, v := range m {

		//Inside the "result" of the JSON
		if result, ok := v.(map[string]interface{}); ok {
			for _, result_value := range result {
				//Inside the validators
				if validators, ok := result_value.([]interface{}); ok {

					for _, val := range validators {
						//var pub_key_data = val["pub_key"]
						marsh, err3 := json.Marshal(val)
						if err3 != nil {
							fmt.Printf("Woops fuck %v", err3)
							os.Exit(1)
						}

						var validator validatorObject
						json.Unmarshal(marsh, &validator)

						validator.ID = p2p.ID(hex.EncodeToString(tmhash.SumTruncated([]byte(validator.Address))))

						fmt.Printf("\nValidator address is = %v\n", validator.Address)
						fmt.Printf("Validator ID is = %v\n", validator.ID)

						// var ID_from_PubKey = p2p.PubKeyToID(validator.PubKey)
						// fmt.Printf("ID from pubkey is = %v", ID_from_PubKey)
					}
				}
			}
		}
	}
}

func isPubKeySame(ID p2p.ID, pubkey crypto.PubKey) bool {
	//Call p2p method
	var ID_from_PubKey = p2p.PubKeyToID(pubkey)

	fmt.Printf("\n\n\nProvided ID = %v | Transformed ID = %v\n", ID, ID_from_PubKey)
	fmt.Printf("\tReturned ID is of type %T\n", ID_from_PubKey)

	//Verify method
	if ID_from_PubKey == ID {
		return true
	}
	return false
}

func parsePort(nodeAddr string) string {
	u, err := url.Parse(nodeAddr)
	if err != nil {
		return ""
	}

	return u.Port()
}

func parseURL(nodeAddr string) string {
	u, err := url.Parse(nodeAddr)
	if err != nil {
		return ""
	}

	fmt.Println(u.Host)
	var split1 = strings.Split(nodeAddr, "@")
	var ip1 = split1[len(split1)-1]
	var split2 = strings.Split(ip1, "//")
	var ip2 = split2[len(split2)-1]
	var finalSplit = strings.Split(ip2, ":")
	var ip = finalSplit[0]

	//fmt.Printf("\n\nParsed address %v and returned %v", nodeAddr, ip)

	return ip
	//return u.Hostname()
}

func locationFromIPResp(r *ipstack.Response) Location {
	return Location{
		Country:   r.CountryName,
		Region:    r.RegionName,
		City:      r.City,
		Latitude:  fmt.Sprintf("%f", r.Latitude),
		Longitude: fmt.Sprintf("%f", r.Longitude),
	}
}

// PingAddress attempts to ping a P2P Tendermint address returning true if the
// node is reachable and false otherwise.
func PingAddress(address string, t int64) bool {
	conn, err := net.DialTimeout("tcp", address, time.Duration(t)*time.Second)
	if err != nil {
		return false
	}

	defer conn.Close()
	return true
}
