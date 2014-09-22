package main

import (
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"runtime"
	"strings"

	"github.com/gobuild/log"

	"github.com/codegangsta/cli"
	sh "github.com/codeskyblue/go-sh"
	"github.com/gobuild/gobuild2/pkg/config"
)

func findFiles(path string, depth int, skips []*regexp.Regexp) ([]string, error) {
	baseNumSeps := strings.Count(path, string(os.PathSeparator))
	var files []string
	err := filepath.Walk(path, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			log.Warnf("filewalk: %s", err)
			return nil
		}
		if info.IsDir() {
			pathDepth := strings.Count(path, string(os.PathSeparator)) - baseNumSeps
			if pathDepth > depth {
				return filepath.SkipDir
			}
		}
		name := info.Name()
		isSkip := false
		for _, skip := range skips {
			if skip.MatchString(name) {
				isSkip = true
				break
			}
		}
		// log.Println(isSkip, name)
		if !isSkip {
			files = append(files, path)
		}
		if isSkip && info.IsDir() {
			return filepath.SkipDir
		}
		return nil
	})
	return files, err
}

func Action(c *cli.Context) {
	var goos, goarch = c.String("os"), c.String("arch")
	var depth = c.Int("depth")
	var output = c.String("output")
	var gom = c.String("gom")
	var nobuild = c.Bool("nobuild")
	var adds = c.StringSlice("add")

	if goos == "" {
		goos = runtime.GOOS
	}
	if goarch == "" {
		goarch = runtime.GOARCH
	}
	var err error
	defer func() {
		if err != nil {
			log.Fatal(err)
		}
	}()
	sess := sh.NewSession()
	sess.SetEnv("GOOS", goos)
	sess.SetEnv("GOARCH", goarch)
	sess.ShowCMD = true

	gomarr := strings.Fields(gom)
	if len(gomarr) >= 1 {
		sess.Alias("go", gomarr[0], gomarr[1:]...)
	}

	// parse yaml
	pcfg, err := config.ReadPkgConfig(config.RCFILE)
	if err != nil {
		return
	}
	// var pcfg = new(config.PackageConfig)
	// if sh.Test("file", config.RCFILE) {
	// 	data, er := ioutil.ReadFile(config.RCFILE)
	// 	if er != nil {
	// 		err = er
	// 		return
	// 	}
	// 	if err = goyaml.Unmarshal(data, pcfg); err != nil {
	// 		return
	// 	}
	// } else {
	// 	pcfg = config.DefaultPcfg
	// }
	pwd, _ := os.Getwd()
	gobin := filepath.Join(pwd, sanitizedName(pcfg.Settings.TargetDir))
	sess.SetEnv("GOBIN", gobin)
	log.Debugf("set env GOBIN=%s", gobin)
	log.Debug("config:", pcfg)
	pcfg.Filesets.Includes = append(pcfg.Filesets.Includes, adds...)

	var skips []*regexp.Regexp
	for _, str := range pcfg.Filesets.Excludes {
		skips = append(skips, regexp.MustCompile("^"+str+"$"))
	}

	log.Infof("archive file to: %s", output)
	var z Archiver
	hasExt := func(ext string) bool { return strings.HasSuffix(output, ext) }
	switch {
	case hasExt(".zip"):
		fmt.Println("zip format")
		z, err = CreateZip(output)
	case hasExt(".tar"):
		fmt.Println("tar format")
		z, err = CreateTar(output)
	case hasExt(".tgz"):
		fallthrough
	case hasExt(".tar.gz"):
		fmt.Println("tar.gz format")
		z, err = CreateTgz(output)
	default:
		fmt.Println("unsupport file archive format")
		os.Exit(1)
	}
	if err != nil {
		return
	}

	var files []string
	// build source
	if !nobuild {
		targetDir := sanitizedName(pcfg.Settings.TargetDir)
		if !sh.Test("dir", targetDir) {
			os.MkdirAll(targetDir, 0755)
		}
		symdir := filepath.Join(targetDir, goos+"_"+goarch)
		if err = os.Symlink(gobin, symdir); err != nil {
			log.Fatalf("os symlink error: %s", err)
		}
		defer os.Remove(symdir)
		opts := []string{"install", "-v"}
		opts = append(opts, strings.Fields(pcfg.Settings.Addopts)...) // TODO: here need to use shell args parse lib
		if err = sess.Command("go", opts).Run(); err != nil {
			return
		}
		os.Remove(symdir) // I have to do it twice
		cwd, _ := os.Getwd()
		program := filepath.Base(cwd)
		if goos == "windows" {
			program += ".exe"
		}
		if sh.Test("file", program) {
			files = append(files, program)
		}
	}

	log.Debug("archive files")
	for _, filename := range pcfg.Filesets.Includes {
		fs, err := findFiles(filename, depth, skips)
		if err != nil {
			return
		}
		files = append(files, fs...)
	}
	for _, file := range files {
		log.Infof("zip add file: %v", file)
		if err = z.Add(file); err != nil {
			return
		}
	}
	log.Info("finish archive file")
	err = z.Close()
}
