package crawl_test

import (
	"testing"
	"time"

	"github.com/stretchr/testify/require"
	"github.com/theSamPadilla/tmcrawl/crawl"
)

func TestNode_Key(t *testing.T) {
	n := crawl.Node{}
	require.Equal(t, "node/", string(n.Key()))

	n = crawl.Node{
		Address: "127.0.0.1",
		RPCPort: "26657",
		P2PPort: "26656",
	}
	require.Equal(t, "node/127.0.0.1", string(n.Key()))
}

func TestNode_Serialize(t *testing.T) {
	n := crawl.Node{
		Address:  "127.0.0.1",
		RPCPort:  "26657",
		P2PPort:  "26656",
		Moniker:  "test-node-0",
		ID:       "5a8a6061c8a2e2e02d497060d5325b6588051cc6",
		Network:  "chain-0",
		Version:  "0.0.1",
		TxIndex:  "off",
		LastSync: time.Now().UTC().Format(time.RFC3339),
		Location: crawl.Location{
			Country:   "United States",
			Region:    "Virginia",
			City:      "Ashburn",
			Latitude:  "39.043701",
			Longitude: "-77.474197",
		},
	}

	bz, err := n.Marshal()
	require.NoError(t, err)

	other := new(crawl.Node)
	require.NoError(t, other.Unmarshal(bz))
	require.Equal(t, n, *other)
}

func TestLocation_Serialize(t *testing.T) {
	l := crawl.Location{
		Country:   "United States",
		Region:    "Virginia",
		City:      "Ashburn",
		Latitude:  "39.043701",
		Longitude: "-77.474197",
	}

	bz, err := l.Marshal()
	require.NoError(t, err)

	other := new(crawl.Location)
	require.NoError(t, other.Unmarshal(bz))
	require.Equal(t, l, *other)
}
