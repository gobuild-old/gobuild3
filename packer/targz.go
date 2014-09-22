package main

import (
	"compress/gzip"
	"io"
	"os"
)

type Tgz struct {
	*Tar
	writer io.WriteCloser
}

func CreateTgz(filename string) (*Tgz, error) {
	file, err := os.Create(filename)
	if err != nil {
		return nil, err
	}
	writer := gzip.NewWriter(file)
	return &Tgz{Tar: NewTarWriter(writer), writer: writer}, nil
}

func (t *Tgz) Close() error {
	t.Tar.Close()
	return t.writer.Close()
}
