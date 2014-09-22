package main

import (
	"os"
	"path/filepath"

	"github.com/codegangsta/cli"
)

const VERSION = "0.3.0922"

var app = cli.NewApp()

func init() {
	cwd, _ := os.Getwd()
	program := filepath.Base(cwd)

	app.Name = "gobuild"
	app.Usage = "[COMMANDS]"
	app.Version = VERSION
	app.Flags = []cli.Flag{
				cli.StringFlag{Name: "os", Value: os.Getenv("GOOS"), Usage: "operation system"},
				cli.StringFlag{Name: "arch", Value: os.Getenv("GOARCH")},
				cli.StringFlag{Name: "depth", Value: "3", Usage: "depth of file to walk"},
				cli.StringFlag{Name: "output,o", Value: program + ".zip", Usage: "target file"},
				cli.StringFlag{Name: "gom", Value: "go", Usage: "go package manage program"},
				cli.BoolFlag{Name: "nobuild", Usage: "donot call go build when pack"},
				cli.StringSliceFlag{Name: "add,a", Value: &cli.StringSlice{}, Usage: "add file"},
	}
}

func main() {
	app.Run(os.Args)
}
