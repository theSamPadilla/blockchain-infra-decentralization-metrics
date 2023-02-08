package config

import (
	"io/ioutil"
	"os"
	"path/filepath"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestValidate(t *testing.T) {
	testCases := []struct {
		name      string
		cfg       Config
		expectErr bool
	}{
		{
			"valid config",
			Config{IPStackKey: "testkey", Seeds: []string{"http://seed1:26657", "http://seed2:26657"}},
			false,
		},
		{
			"missing seeds",
			Config{IPStackKey: "testkey", Seeds: []string{}},
			true,
		},
		{
			"missing ipstack API key",
			Config{IPStackKey: "", Seeds: []string{"http://seed1:26657", "http://seed2:26657"}},
			true,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			require.Equal(t, tc.cfg.Validate() != nil, tc.expectErr)
		})
	}
}

func TestParseConfig_Default(t *testing.T) {
	tmpFile, err := ioutil.TempFile("", "tmcrawl.toml")
	require.NoError(t, err)
	defer os.Remove(tmpFile.Name())

	content := []byte(`
ipstack_key = "testkey"
seeds = [
	"http://seed1:26657",
	"http://seed2:26657"
]`)
	_, err = tmpFile.Write(content)
	require.NoError(t, err)

	cfg, err := ParseConfig(tmpFile.Name())
	require.NoError(t, err)
	require.Equal(t, "testkey", cfg.IPStackKey)
	require.Equal(t, []string{"http://seed1:26657", "http://seed2:26657"}, cfg.Seeds)
	require.Equal(t, defaultListenAddr, cfg.ListenAddr)
	require.Equal(t, defaultReseedSize, cfg.ReseedSize)
	require.Equal(t, defaultCrawlInterval, cfg.CrawlInterval)
	require.Equal(t, defaultRecheckInterval, cfg.RecheckInterval)
	require.Equal(t, filepath.Join(os.Getenv("HOME"), ".tmcrawl"), cfg.DataDir)

	require.NoError(t, tmpFile.Close())
}

func TestParseConfig_Invalid(t *testing.T) {
	tmpFile, err := ioutil.TempFile("", "tmcrawl.toml")
	require.NoError(t, err)
	defer os.Remove(tmpFile.Name())

	_, err = ParseConfig("")
	require.Error(t, err)

	_, err = ParseConfig("/a/b/c")
	require.Error(t, err)

	content := []byte(`
ipstack_key: "testkey"
`)
	_, err = tmpFile.Write(content)
	require.NoError(t, err)

	_, err = ParseConfig(tmpFile.Name())
	require.Error(t, err)

	require.NoError(t, tmpFile.Close())
}
