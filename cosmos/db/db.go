package db

import (
	"path/filepath"

	badger "github.com/dgraph-io/badger/v2"
)

type (
	// DB defines the persistence interface for tmcrawl.
	DB interface {
		Get(key []byte) ([]byte, error)
		Has(key []byte) bool
		Set(key, value []byte) error
		Delete(key []byte) error
		IteratePrefix(prefix []byte, cb func(k, v []byte) bool)
		Close() error
	}

	// BadgerDB defines a wrapper type around a Badger DB that implements the DB
	// interface. It mainly provides transaction abstractions.
	BadgerDB struct {
		db *badger.DB
	}
)

// NewBadgerDB returns a wrapper around a Badger DB that implements the DB interface.
// It will create all the necessary Badger DB buckets if they don't already exist.
func NewBadgerDB(dataDir, dbName string) (DB, error) {
	dbPath := filepath.Join(dataDir, dbName)
	db, err := badger.Open(badger.DefaultOptions(dbPath))
	if err != nil {
		return nil, err
	}

	return &BadgerDB{db: db}, err
}

// NewBadgerMemDB return a pure in-memory Badger DB instance that implements the
// DB interface. Data is stored only in-memory and should be used for testing
// purposes only.
func NewBadgerMemDB() (DB, error) {
	db, err := badger.Open(badger.DefaultOptions("").WithInMemory(true))
	if err != nil {
		return nil, err
	}

	return &BadgerDB{db: db}, err
}

// Get returns a value for a given key. It returns badger.ErrKeyNotFound if the
// value is not found.
func (bdb *BadgerDB) Get(key []byte) (value []byte, err error) {
	err = bdb.db.View(func(tx *badger.Txn) error {
		item, err := tx.Get(key)
		if err != nil {
			return err
		}

		value, err = item.ValueCopy(nil)
		return err
	})

	return value, err
}

// Has returns a boolean determining if the underlying Badger DB has a given key
// or not.
func (bdb *BadgerDB) Has(key []byte) bool {
	v, err := bdb.Get(key)
	return v != nil && err == nil
}

// Set attempts to set a key/value pair into Badger DB returning an error upon
// failure.
func (bdb *BadgerDB) Set(key, value []byte) error {
	return bdb.db.Update(func(tx *badger.Txn) error {
		return tx.SetEntry(badger.NewEntry(key, value))
	})
}

// Delete attempts to remove a value by key from Badger DB returning an error
// upon failure.
func (bdb *BadgerDB) Delete(key []byte) error {
	return bdb.db.Update(func(tx *badger.Txn) error {
		return tx.Delete(key)
	})
}

// IteratePrefix iterates over a series of key/value pairs where each key contains
// the provided prefix. For each key/value pair, a cb function is invoked. If
// cb returns true, iteration is halted.
func (bdb *BadgerDB) IteratePrefix(prefix []byte, cb func(k, v []byte) bool) {
	_ = bdb.db.Update(func(tx *badger.Txn) error {
		it := tx.NewIterator(badger.DefaultIteratorOptions)
		defer it.Close()

		for it.Seek(prefix); it.ValidForPrefix(prefix); it.Next() {
			item := it.Item()
			k := item.Key()
			v, _ := item.ValueCopy(nil)

			if cb(k, v) {
				return nil
			}
		}

		return nil
	})
}

// Close closes the Badger DB instance and returns an error upon failure.
func (bdb *BadgerDB) Close() error {
	return bdb.db.Close()
}
