package main

import (
	"os"
	"path/filepath"
	"runtime"

	"github.com/codegangsta/cli"
)

const VERSION = "0.3.0922"

var app = cli.NewApp()

func init() {
	cwd, _ := os.Getwd()
	program := filepath.Base(cwd)

	app.Name = "gobuild"
	app.Usage = "build and pack file into tgz or zip"
	app.Action = Action
	app.Version = VERSION
	app.Flags = []cli.Flag{
		cli.StringFlag{Name: "os", EnvVar: "GOOS", Value: runtime.GOOS, Usage: "operation system"},
		cli.StringFlag{Name: "arch", EnvVar: "GOARCH", Value: runtime.GOARCH, Usage: "arch eg amd64|386|arm"},
		cli.StringFlag{Name: "depth", Value: "3", Usage: "depth of file to walk"},
		cli.StringFlag{Name: "output,o", Value: program + ".zip", Usage: "target file"},
		cli.StringFlag{Name: "gom", Value: "go", Usage: "go package manage program"},
		cli.BoolFlag{Name: "nobuild", Usage: "donot call go build when pack"},
		cli.BoolFlag{Name: "rm", Usage: "remove build files when done"},
		cli.BoolFlag{Name: "debug", Usage: "show debug information"},
		cli.BoolFlag{Name: "init", Usage: "generate sample .gobuild.yml"},
		cli.StringSliceFlag{Name: "add,a", Value: &cli.StringSlice{}, Usage: "add file"},
	}
}

func main() {
	app.Run(os.Args)
}
