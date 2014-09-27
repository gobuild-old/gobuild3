## Still developing

## Beta version released

<http://beta.gobuild.io>

## Description
This repo is for website `gobuild.io`. Offer service that can easy build **golang** source code.

Commit your repo address to gobuild.io, it will do cross compile for you. 
After a while, download link will generated.

Now the web support the following features.

* platform support linux,amd64-386-arm/windows,amd64-386/darwin,amd64-386
* CGO support
* Support build specify branch, tag, or sha
* Rank the most download repos and latest repos.
* Support `.gobuild.yml` file to custom build actions

## .gobulid.yml format

```
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
            go install -v
        outfiles:
            - packer
```
This is a full version of `.gobuild.yml`, this file should commit the your repo with directory which contains go source code.

Only filesets.excludes use regex to filter file, the filesets.include not use regex, please do remember.
(If you got any idea to let includes support regex, pull requests are welcome.)

Use `packer` to check if `.gobuild.yml` is right.

	go get github.com/gobuild/gobuild3/packer

`packer --init` can also generate sample `.gobuild.yml`

settings.targetdir will set to env GOBIN, which will make sure `go install` install to the right dir.

Default values:

* settings.bulid.action --- gobuild
* settings.build.outfiles --- the basename of $REPONAME. files will add `.exe` auto when build for windows
* filesets.includes --- ["README.md", "LICENSE"]
* filesets.excludes --- ["\.git"]
other setting default empty.

## LINCENSE
This repo use MIT LINCENSE