package main

import (
	"archive/tar"
	"fmt"
	"io"
	"os"
)

type Tar struct {
	*tar.Writer
}

func CreateTar(filename string) (*Tar, error) {
	file, err := os.Create(filename)
	if err != nil {
		return nil, err
	}
	return NewTarWriter(file), nil
}

func NewTarWriter(wr io.WriteCloser) *Tar {
	writer := tar.NewWriter(wr)
	return &Tar{Writer: writer}
}

func (t *Tar) Add(filename string) error {
	info, rdc, err := statFile(filename)
	if err != nil {
		return err
	}
	defer rdc.Close()

	link := ""
	if info.Mode()&os.ModeSymlink != 0 {
		link, _ = os.Readlink(filename)
	}
	// header
	hdr, err := tar.FileInfoHeader(info, link)
	if err != nil {
		return err
	}
	hdr.Name = sanitizedName(filename)
	if info.IsDir() {
		hdr.Name += "/"
	}
	if err = t.WriteHeader(hdr); err != nil {
		return fmt.Errorf("header: %v", err)
	}
	if info.Mode().IsRegular() {
		_, err = io.Copy(t, rdc)
	}
	return err
}
