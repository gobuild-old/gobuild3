package main

import (
	"archive/zip"
	"io"
	"os"
)

type Zip struct {
	*zip.Writer
}

func CreateZip(filename string) (*Zip, error) {
	fd, err := os.Create(filename)
	if err != nil {
		return nil, err
	}
	zipper := zip.NewWriter(fd)
	return &Zip{Writer: zipper}, nil
}

func (z *Zip) Add(filename string) error {
	info, rdc, err := statFile(filename)
	if err != nil {
		return err
	}
	defer rdc.Close()

	hdr, err := zip.FileInfoHeader(info)
	if err != nil {
		return err
	}
	hdr.Name = sanitizedName(filename)
	if info.IsDir() {
		hdr.Name += "/"
	}
	hdr.Method = zip.Deflate // compress method
	writer, err := z.CreateHeader(hdr)
	if err != nil {
		return err
	}
	_, err = io.Copy(writer, rdc)
	return err
}
