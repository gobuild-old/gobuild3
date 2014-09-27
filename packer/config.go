package main

import (
	"io/ioutil"

	"github.com/codeskyblue/go-sh"
	"github.com/gobuild/goyaml"
)

type PackageConfig struct {
	Author      string `yaml:"author"`
	Description string `yaml:"description"`
	Filesets    struct {
		Includes []string `yaml:"includes"`
		Excludes []string `yaml:"excludes"`
	} `yaml:"filesets"`
	Settings struct {
		TargetDir string   `yaml:"targetdir"` // target dir
		Outfiles  []string `yaml:"outfiles"`
		Build     string   `yaml:"build"`
	} `yaml:"settings"`
}

const RCFILE = ".gobuild.yml"

var DefaultPcfg *PackageConfig

func init() {
	pcfg := &PackageConfig{}
	pcfg.Author = ""
	pcfg.Filesets.Includes = []string{"README.md", "LICENSE"}
	pcfg.Filesets.Excludes = []string{"\\.git"}
	pcfg.Settings.TargetDir = ""
	pcfg.Settings.Build = "go install -v"
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
