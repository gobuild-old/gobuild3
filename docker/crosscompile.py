#!/usr/bin/env python
# coding: utf-8

import os
import sys
import argparse

import sh

pathjoin = os.path.join

packer_path = pathjoin(os.path.dirname(os.path.abspath(__file__)), 'packer')
packer = sh.Command(packer_path)
reponame = ''

def binname(reponame):
    basename = os.path.basename(reponame)

def build(goos, goarch):
    env = os.environ.copy()
    env.update({'GOOS': goos, 'GOARCH': goarch})
    sh.go.build(_env=env)
    binname = os.path.basename(reponame)
    outzipname = '%s-%s-%s.zip' %(binname, goos, goarch)
    if goos == 'windows':
        binname += '.exe'

    outfd = open('build-%s-%s.log' %(goos, goarch), 'w')
    packer('--nobuild', '-a', binname, '-o', outzipname, _err_to_out=True, _out=outfd)

def main():
    parser = argparse.ArgumentParser(description='cross compile build for golang')
    parser.add_argument('--repo', dest='repo', required=True)
    args = parser.parse_args()

    global reponame
    reponame = args.repo

    sh.go.get('-v', reponame, _out=sys.stdout)
    rdir = pathjoin(os.getenv('GOPATH'), 'src', args.repo)
    os.chdir(rdir) # change directory

    os_archs = [('linux', 'amd64'), ('linux', '386'),
            ('windows', 'amd64'), ('windows', '386')]

    for goos, arch in os_archs:
        print 'Building for %s,%s' %(goos, arch)
        build(goos, arch)

    print 'Moving files ...'
    for goos, arch in os_archs:
        logfile = 'build-%s-%s.log' %(goos, arch)
        print 'move', goos, arch

if __name__ == '__main__':
    main()
