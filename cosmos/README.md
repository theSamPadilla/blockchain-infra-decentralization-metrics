# tmcrawl [WIP - Not Fully nctional]

[![Build Status](https://travis-ci.org/theSamPadilla/tmcrawl.svg?branch=master)](https://travis-ci.org/theSamPadilla/tmcrawl)
[![Go Report Card](https://goreportcard.com/badge/github.com/theSamPadilla/tmcrawl)](https://goreportcard.com/report/github.com/theSamPadilla/tmcrawl)

> A Tendermint p2p crawling utility and API.
>> forked from [fissionlabsio/tmcrawl](https://github.com/fissionlabsio/tmcrawl)

The `tmcrawl` utility will capture node metadata such as network
name, node version, RPC information, and node ID for each tendermint crawled node. The utility
will first start with a set of seeds and attempt to crawl as many nodes as possible
from those seeds. When there are no nodes left to crawl, `tmcrawl` will pick a random
set of nodes from the known list of nodes to reseed the crawl every `crawl_interval`
seconds from the last attempted crawl finish.

Nodes are persisted in a key/value embedded database, by default BadgerDB. Saved
nodes will also be periodically rechecked every `recheck_interval`. If any node
cannot be reached, it'll be removed from the known set of nodes.

## Things to Note

1. `tmcrawl` is a Tendermint p2p network crawler, it does not operate as a seed
node or any other type of node.
2. Tendermint nodes can have peers across multiple networks, so there is no guarantee that all the nodes found by the tool run in the same network. For that, pay attention to the `network` attribute of the [`DefaultNodeInfo`](https://pkg.go.dev/github.com/tendermint/tendermint@v0.34.24/p2p#DefaultNodeInfo) tendermint type.
3. `tmcrawl` uses the Tendermint RPC port (`26657`) to get [`ResultStatus`](https://pkg.go.dev/github.com/tendermint/tendermint@v0.34.24/rpc/core/types#ResultStatus), from where it extracts network and peer information. Since having the Tendermint RPC port open is optional, **there is no guarantee that `tmcrawl` will crawl all the nodes in a cosmos network.** The number of nodes crawled for a network depends on how many nodes have the RPC port open and which peers they connect to.
4. Independent development of `tmcrawl` can be found (here)[https://github.com/theSamPadilla/tmcrawl]. Original repo where can be found (here)[https://github.com/fissionlabsio/tmcrawl].

## Install

`tmcrawl` takes a simple configuration. It needs to only know about a an
[ipstack](https://ipstack.com/) API access key and an initial set of seed nodes.
See `config.toml` for reference.

To install the binary:

```shell
$ make install
```

**Note**: Requires [Go 1.13+](https://golang.org/dl/)

## Usage

`tmcrawl` runs as a daemon process and exposes a RESTful JSON API.

To start the binary:

```shell
$ tmcrawl </path/to/config.toml> [flags]
```

The RESTful JSON API is served over `listen_addr` as provided in the configuration.
See `--help` for further documentation.

## API

All API documentation is hosted via Swagger UI under path `/swagger/`.

## Future Improvements

- Crawl integration tests
- Front-end visualization

## Contributing

Contributions are welcome! Please open an Issues or Pull Request for any changes.

## License

[CCC0 1.0 Universal](https://creativecommons.org/share-your-work/public-domain/cc0/)
