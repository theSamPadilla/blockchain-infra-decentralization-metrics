package config

import (
	"errors"
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"

	"github.com/BurntSushi/toml"
	"github.com/go-playground/validator/v10"
)

var validate *validator.Validate = validator.New()

// ErrEmptyConfigPath defines a sentinel error for an empty config path.
var ErrEmptyConfigPath = errors.New("empty configuration file path")

var (
	defaultListenAddr           = "0.0.0.0:27758"
	defaultCrawlInterval   uint = 15
	defaultRecheckInterval uint = 3600
	defaultReseedSize      uint = 100
)

// Config defines all necessary tmcrawl configuration parameters.
type Config struct {
	Path       string   `toml:"path"`
	DataDir    string   `toml:"data_dir"`
	ListenAddr string   `toml:"listen_addr"`
	Seeds      []string `toml:"seeds" validate:"required,min=1"`
	ReseedSize uint     `toml:"reseed_size"`
	IPStackKey string   `toml:"ipstack_key" validate:"required,min=1"`

	CrawlInterval   uint `toml:"crawl_interval"`
	RecheckInterval uint `toml:"recheck_interval"`
}

// Validate returns an error if the Config object is invalid.
func (c Config) Validate() error {
	return validate.Struct(c)
}

// ParseConfig attempts to read and parse a tmcrawl config from the given file
// path. An error is returned if reading or parsing the config fails.
func ParseConfig(configPath string) (Config, error) {
	var cfg Config

	if configPath == "" {
		return cfg, ErrEmptyConfigPath
	}

	configData, err := ioutil.ReadFile(configPath)
	if err != nil {
		return cfg, fmt.Errorf("failed to read config: %w", err)
	}

	if _, err := toml.Decode(string(configData), &cfg); err != nil {
		return cfg, fmt.Errorf("failed to decode config: %w", err)
	}

	if cfg.ListenAddr == "" {
		cfg.ListenAddr = defaultListenAddr
	}
	if cfg.ReseedSize == 0 {
		cfg.ReseedSize = defaultReseedSize
	}
	if cfg.CrawlInterval == 0 {
		cfg.CrawlInterval = defaultCrawlInterval
	}
	if cfg.RecheckInterval == 0 {
		cfg.RecheckInterval = defaultRecheckInterval
	}
	if cfg.DataDir == "" {
		cfg.DataDir = filepath.Join(os.Getenv("HOME"), ".tmcrawl")
	}

	return cfg, cfg.Validate()
}
