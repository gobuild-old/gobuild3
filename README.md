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

## .gobulid.yml format (TODO: not finished and checked)

```
author: codeskyblue@gmail.com
description: >
        Hmm. this is a test.
        hahaha

filesets:
    includes:
        - conf
        - README[.].*
        - LICENSE
    excludes:
        - \.git
settings:
        build:
                setup: |
                        make prepare
                action: go install -v
                teardown: make clean
        outfiles:
                - cgotest

```
This is a full version of `.gobuild.yml`, this file should commit the your repo with directory which contains go source code.

filesets use regex to filter file, include will do before exclude. 
Use `packer` to check if `.gobuild.yml` is right.

	go get github.com/gobuild/gobuild3/packer

Default values:

* settings.bulid.action --- gobuild
* settings.build.outfiles --- the basename of $REPONAME. files will add `.exe` auto when build for windows
* filesets.includes --- ["README.md", "LICENSE"]

other setting default empty.

## LINCENSE
This repo use MIT LINCENSE