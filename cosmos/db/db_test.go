package db_test

import (
	"fmt"
	"testing"

	"github.com/stretchr/testify/require"
	"github.com/theSamPadilla/tmcrawl/db"
)

func TestGetSet(t *testing.T) {
	bdb, err := db.NewBadgerMemDB()
	require.NoError(t, err)

	key, value := []byte("key"), []byte("value")
	bz, err := bdb.Get(key)
	require.Error(t, err)
	require.Nil(t, bz)

	require.NoError(t, bdb.Set(key, value))

	bz, err = bdb.Get(key)
	require.NoError(t, err)
	require.Equal(t, value, bz)
}

func TestHas(t *testing.T) {
	bdb, err := db.NewBadgerMemDB()
	require.NoError(t, err)

	key, value := []byte("key"), []byte("value")
	require.False(t, bdb.Has(key))

	require.NoError(t, bdb.Set(key, value))
	require.True(t, bdb.Has(key))
}

func TestDelete(t *testing.T) {
	bdb, err := db.NewBadgerMemDB()
	require.NoError(t, err)

	key, value := []byte("key"), []byte("value")
	err = bdb.Delete(key)
	require.NoError(t, err)

	require.NoError(t, bdb.Set(key, value))

	bz, err := bdb.Get(key)
	require.NoError(t, err)
	require.Equal(t, value, bz)

	err = bdb.Delete(key)
	require.NoError(t, err)

	bz, err = bdb.Get(key)
	require.Error(t, err)
	require.Nil(t, bz)
}

func TestIteratePrefix(t *testing.T) {
	bdb, err := db.NewBadgerMemDB()
	require.NoError(t, err)

	prefix1 := []byte("prefix1/")
	prefix2 := []byte("prefix2/")
	numEntries := 10

	for i := 0; i < numEntries; i++ {
		key := append(prefix1, []byte(fmt.Sprintf("%d", i))...)
		require.NoError(t, bdb.Set(key, []byte(fmt.Sprintf("%d", i))))

		key = append(prefix2, []byte(fmt.Sprintf("%d", i))...)
		require.NoError(t, bdb.Set(key, []byte(fmt.Sprintf("%d", i))))
	}

	values := [][]byte{}
	bdb.IteratePrefix(prefix1, func(_, v []byte) bool {
		values = append(values, v)
		return false
	})

	require.Len(t, values, numEntries)

	values = [][]byte{}
	half := numEntries / 2
	bdb.IteratePrefix(prefix2, func(_, v []byte) bool {
		values = append(values, v)
		return len(values) >= half
	})

	require.Len(t, values, half)
}

func TestClose(t *testing.T) {
	bdb, err := db.NewBadgerMemDB()
	require.NoError(t, err)
	require.NoError(t, bdb.Close())
}
