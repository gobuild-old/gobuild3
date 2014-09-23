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
    updated = Optional(datetime)
    view_count = Optional(int, default=0)
    down_count = Optional(int, default=0)
    builds = Set("Build")

class Build(db.Entity):
    repo = Optional(Repo)
    downloadable = Optional(bool, default=True)
    status = Optional(unicode)
    tag = Optional(unicode)
    sha = Optional(unicode)
    time_used = Optional(int)
    updated = Optional(datetime)
    down_count = Optional(int, default=0)
    details = Optional(LongStr)
    files = Set("File")
    version = Optional(unicode)

class File(db.Entity):
    build = Optional(Build)
    reponame = Optional(unicode)
    pkg_type = Optional(unicode, default='binary') # source or binary
    os = Optional(unicode, default='linux')
    arch = Optional(unicode, default='amd64')
    loglink = Optional(unicode)
    zipmd5 = Optional(unicode)
    zipsha = Optional(unicode)
    ziplink = Optional(unicode)
    zipsize = Optional(int, default=0)

class Timer(db.Entity):
    email = Required(unicode)
    mission = Required(unicode)
    created = Optional(date)
    count = Optional(int, default=1)

db.bind('sqlite', './test_db.sqlite', create_db=True)
'''
db.bind(gcfg.db.dbtype, 
        host=gcfg.db.host, 
        user=gcfg.db.username, 
        passwd=gcfg.db.password, 
        db=gcfg.db.dbname)
        '''
db.generate_mapping(create_tables=True)

if __name__ == '__main__':
    with db_session:
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
        build.down_count = 3
        build.details = 'lslxlsla build.....'
        build.version = 'go 1.3.1rc'

        file = File(build=build)
        file.reponame = repo.name
        file.pkg_type = 'binary'
        file.os='windows'
        file.arch = 'amd64'
        file.ziplink = 'http://www.baidu.com'
        file.loglink = 'http://www.baidu.com'
        file.zipmd5 = 'slkjfl213kj4124'
        file.zipsha = 'sssshhhhsej23423467890'
        file.zipsize = 1025

        build = Build(repo=repo)
        build.tag = 'tag:v1.0.2'
        build.sha = 'ssssslkjfaefr3134j2l3krj'
        build.time_used = 104
        build.updated = datetime.today()
        build.down_count = 2
        build.downloadable = False
        build.status = 'build error'
        build.details = 'wwww lslxlsla build.....'

@db_session
def add_record(phoneno, jsondata):
    ''' True or False '''
    phone = Phone.get(number=phoneno)
    if not phone:
        return False
    args = dict(phone=phone,
            created = datetime.fromtimestamp(time.time()),
            data = json.dumps(jsondata))
    JobRecord(**args)
    return True

@db_session
def get_latest_record(devno, strdatetime):
    ''' None or data '''
    stamp = time.mktime(time.strptime(strdatetime, '%Y-%m-%d'))
    start_time = datetime.fromtimestamp(stamp)
    to_time = start_time + timedelta(days=1)
    latest = select(p for p in JobRecord if p.created > start_time and 
            p.created < to_time and p.phone.number == devno).order_by(desc(JobRecord.created))[:1]
    if not latest:
        return None
    latest = latest[0]
    return dict(phoneno=latest.phone.number, created=latest.created, data=json.loads(latest.data))

@db_session
def get_timers(email):
    return select(t for t in Timer if t.email == email)[:]
