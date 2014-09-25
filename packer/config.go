package main

import (
	"io/ioutil"

	"github.com/codeskyblue/go-sh"
	"github.com/gobuild/goyaml"
)

type PackageConfig struct {
	Filesets struct {
		Includes []string `yaml:"includes"`
		Excludes []string `yaml:"excludes"`
	} `yaml:"filesets"`
	Settings struct {
		TargetDir string `yaml:"targetdir"` // target dir
		Addopts   string `yaml:"addopts"`   // extra command line options
	} `yaml:"settings"`
}

const RCFILE = ".gobuild.yml"

var DefaultPcfg *PackageConfig

func init() {
	pcfg := &PackageConfig{}
	pcfg.Filesets.Includes = []string{"README.md", "LICENSE"}
	pcfg.Filesets.Excludes = []string{".*.go"}
	// pcfg.Settings.CGOEnable = true // the default CGOEnable should be nil
	pcfg.Settings.TargetDir = ""
	pcfg.Settings.Addopts = ""
	DefaultPcfg = pcfg
}

// parse yaml
func ReadPkgConfig(filepath string) (pcfg PackageConfig, err error) {
	pcfg = PackageConfig{}
	if sh.Test("file", filepath) {
		data, er := ioutil.ReadFile(filepath)
		if er != nil {
			err = er
			return
		}
		if err = goyaml.Unmarshal(data, &pcfg); err != nil {
			return
		}
	} else {
		pcfg = *DefaultPcfg
	}
	return pcfg, nil
}
