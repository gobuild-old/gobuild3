#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import json
from datetime import datetime, timedelta, date

from pony.orm import *

import gcfg

#sql_debug(True)
db = Database()

class Repo(db.Entity):
    name = Required(unicode, unique=True)
    author = Optional(unicode)
    description = Optional(str)
    created = Optional(datetime)
    updated = Optional(datetime)
    view_count = Optional(int, default=0) # goint to replace by ammount soon.
    down_count = Optional(int, default=0) # so is it.
    ammount = Set("Ammount") # new add

    builds = Set("Build")

    # github-api: https://developer.github.com/v3/repos/#get
    readme = Optional(LongStr) # markdown format
    stars = Optional(int, default=0) # get from github
    offcial = Optional(bool, default=False)
    #alias = Optional(unicode) # same in Recommend.alias
    recommend = Optional("Recommend")

class Ammount(db.Entity):
    repo = Required(Repo)
    name = Required(unicode)
    count = Optional(int, default=0)
    composite_key(name, repo)

class Recommend(db.Entity):
    repo = Optional(Repo)
    name = Optional(unicode)
    created = Optional(datetime)
    updated = Optional(datetime)
    checked = Optional(bool, default=False)
    uuid = Optional(unicode)
    category = Optional("Category")

class Category(db.Entity):
    name = Required(unicode, unique=True)
    recommends = Set(Recommend)

class Build(db.Entity):
    repo = Optional(Repo)
    tag = Optional(unicode)
    
    sha = Optional(unicode)
    downloadable = Optional(bool, default=False)
    updated = Optional(datetime)
    down_count = Optional(int, default=0)
    files = Set("File")
    jobs = Set("Job")
    latest_job = Optional(int, default=0)
    osarchs = Optional(LongStr) # json data: [{"windows": ["amd64", "386"], ...]

    status = Optional(unicode) # ?
    time_used = Optional(int) # ?
    version = Optional(unicode) #?

    composite_key(repo, tag)

class Job(db.Entity):
    build = Required(Build)
    status = Optional(unicode, default='initing')
    created = Optional(datetime)
    updated = Optional(datetime)
    output = Optional(LongStr, default='')
    gobuildrc = Optional(LongStr)

class File(db.Entity):
    build = Optional(Build)
    reponame = Optional(unicode)
    pkg_type = Optional(unicode, default='binary') # source or binary
    os = Optional(unicode, default='linux')
    arch = Optional(unicode, default='amd64')
    loglink = Optional(unicode)
    outlink = Optional(unicode)
    size = Optional(int, default=0)
    md5 = Optional(unicode)
    sha = Optional(unicode)

class Timer(db.Entity):
    email = Required(unicode)
    mission = Required(unicode)
    created = Optional(date)
    count = Optional(int, default=1)

if gcfg.db.dbtype == 'sqlite':
    db.bind('sqlite', './test_db.sqlite', create_db=True)
else:
    db.bind(gcfg.db.dbtype, 
        host=gcfg.db.host, 
        user=gcfg.db.username, 
        passwd=gcfg.db.password, 
        db=gcfg.db.dbname)

db.generate_mapping(create_tables=True)

@db_session
def repocount(repo, _type, addcnt=0):
    ''' repo download count(got,down,or other) '''
    am = Ammount.get(repo=repo, name=_type) \
            or Ammount(repo=repo, name=_type)
    am.count += addcnt
    return am.count


if __name__ == '__main__':
    with db_session:
        print 'start add new repo'
        print repocount(1, 'got', 2)

        repo = Repo(name='github.com/gobuild/got')
        repo.author = 'lunny'
        repo.description = 'this is sample repo'
        repo.updated = datetime.today()
        repo.view_count = 10
        repo.down_count = 7

        build = Build(repo=repo)
        build.tag = 'branch:master'
        build.sha = 'slkjfaefr3jr2134j2l3krj'
        build.time_used = 1024
        build.updated = datetime.today()
        build.downloadable = False
        build.down_count = 3
        build.details = 'lslxlsla build.....'
        build.version = 'go 1.3.1rc'

        file = File(build=build)
        file.reponame = repo.name
        file.pkg_type = 'binary'
        file.os='windows'
        file.arch = 'amd64'
        file.outlink = 'http://www.baidu.com'
        file.loglink = 'http://www.baidu.com'
        file.md5 = 'slkjfl213kj4124'
        file.sha = 'sssshhhhsej23423467890'
        file.size = 1025

        print 'add new build'
        build = Build(repo=repo)
        build.tag = 'tag:v1.0.2'
        build.sha = 'ssssslkjfaefr3134j2l3krj'
        build.time_used = 104
        build.updated = datetime.today()
        build.down_count = 2
        build.downloadable = True
        build.status = 'build error'
        build.osarchs = '[["windows", ["amd64", "arm"]], ["linux", ["amd64"]]]'

