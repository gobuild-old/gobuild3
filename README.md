## Beta version released

<http://gobuild.io>

## Description
This repo is for the website `gobuild.io`, which offers a service that can easy build **golang** source code.

Commit your repo address to gobuild.io and it will cross-compile for you and generate a download link.

Currently the site supports the following features:

* Platform support for linux, amd64-386-arm/windows, amd64-386/darwin and amd64-386
* CGO support
* Builds specified by branch, tag, or sha
* Rank the most downloaded and latest repos
* Custom build actions with `.gobuild.yml` files
* [godep](https://github.com/tools/godep) support

## .gobuild.yml format

```yaml
author: codeskyblue@gmail.com
description: >
        Hmm. this is a test.
        hahaha

filesets:
    includes:
        - conf
        - README.md
        - LICENSE
    excludes:
        - \.git
settings:
        targetdir: ""
        build: |
			test -d Godeps && go(){ godep go "$@";} ; go install -v
        outfiles:
            - packer
```
This is a full version of `.gobuild.yml`. This file should be committed to your repo with a directory containing go source code.

Only `filesets.excludes` uses regex to filter file. Note that `filesets.includes` does *not* use regex.
(If you have any idea how includes could support regex, pull requests are welcome.)

Use `packer` to check if `.gobuild.yml` is right.

	go get github.com/gobuild/gobuild3/packer

`packer --init` can also generate sample `.gobuild.yml`

`settings.targetdir` will set to env `GOBIN`, which will make sure `go install` installs to the right directory.

**Default values**:

* settings.build --- "test -d Godeps && go(){ godep go "$@";} ; go install -v"
* settings.build.outfiles --- the basename of $REPONAME. files will add `.exe` auto when build for windows
* filesets.includes --- ["README.md", "LICENSE", "conf", "static", "views"]
* filesets.excludes --- ["\.git", `".*\\.go"`]
other settings default to empty.

alias not supported in `bash -c`, I really don't know why.

## LICENSE
This repo is covered by the MIT LICENSE
