package cmd

import (
	"fmt"
	"net/http"
	"os"
	"time"

	"github.com/gorilla/mux"
	"github.com/rs/cors"
	"github.com/rs/zerolog"
	"github.com/rs/zerolog/log"
	"github.com/spf13/cobra"
	"github.com/theSamPadilla/tmcrawl/config"
	"github.com/theSamPadilla/tmcrawl/crawl"
	"github.com/theSamPadilla/tmcrawl/db"
	"github.com/theSamPadilla/tmcrawl/server"
)

const (
	logLevelJSON = "json"
	logLevelText = "text"
)

var (
	logLevel  string
	logFormat string
)

var rootCmd = &cobra.Command{
	Use:   "tmcrawl [config-file]",
	Args:  cobra.ExactArgs(1),
	Short: "tmcrawl implements a Tendermint p2p network crawler utility and API.",
	Long: `tmcrawl implements a Tendermint p2p network crawler utility and API.

The utility will capture geolocation information and node metadata such as network
name, node version, RPC information, and node ID for each crawled node. The utility
will first start with a set of seeds and attempt to crawl as many nodes as possible
from those seeds. When there are no nodes left to crawl, tmcrawl will pick a random
node from the known list of nodes to reseed the crawl every 'crawl_interval' seconds
from the last attempted crawl finish.

Nodes will also be periodically checked every 'recheck_interval'. If any node cannot
be reached, it'll be removed from the known set of nodes.`,
	RunE: tmcrawlCmdHandler,
}

func init() {
	rootCmd.PersistentFlags().StringVar(&logLevel, "log-level", zerolog.InfoLevel.String(), "logging level")
	rootCmd.PersistentFlags().StringVar(&logFormat, "log-format", logLevelJSON, "logging format; must be either json or text")

	rootCmd.AddCommand(getVersionCmd())
}

// Execute adds all child commands to the root command and sets flags appropriately.
// This is called by main.main(). It only needs to happen once to the rootCmd.
func Execute() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
		os.Exit(1)
	}
}

// This is the main handler
func tmcrawlCmdHandler(cmd *cobra.Command, args []string) error {
	logLvl, err := zerolog.ParseLevel(logLevel)
	if err != nil {
		return err
	}

	zerolog.SetGlobalLevel(logLvl)

	switch logFormat {
	case logLevelJSON:
		// JSON is the default logging format

	case logLevelText:
		log.Logger = log.Output(zerolog.ConsoleWriter{Out: os.Stderr})

	default:
		return fmt.Errorf("invalid logging format: %s", logFormat)
	}

	cfg, err := config.ParseConfig(args[0])
	if err != nil {
		return err
	}

	if _, err := os.Stat(cfg.DataDir); os.IsNotExist(err) {
		if err := os.Mkdir(cfg.DataDir, os.ModePerm); err != nil {
			return err
		}
	}

	// create and open key/value DB
	db, err := db.NewBadgerDB(cfg.DataDir, "tmcrawl.db")
	if err != nil {
		return err
	}
	defer db.Close()

	crawler := crawl.NewCrawler(cfg, db)
	go func() { crawler.Crawl() }()

	// create HTTP router and mount routes
	router := mux.NewRouter()
	c := cors.New(cors.Options{
		AllowedOrigins: []string{"*"},
	})
	server.RegisterRoutes(db, router)

	srv := &http.Server{
		Handler:      c.Handler(router),
		Addr:         cfg.ListenAddr,
		WriteTimeout: 15 * time.Second,
		ReadTimeout:  15 * time.Second,
	}

	log.Info().Str("address", cfg.ListenAddr).Msg("starting API server...")
	return srv.ListenAndServe()
}
