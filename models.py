#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from pony.orm import *
from datetime import datetime, timedelta, date
import json
import gcfg

#sql_debug(True)
db = Database()

class Repo(db.Entity):
    name = Required(unicode, unique=True)
    author = Optional(unicode)
    updated = Optional(datetime)
    view_count = Optional(int, default=0)
    down_count = Optional(int, default=0)

class Build(db.Entity):
    branch = Optional(unicode)
    time_used = Optional(int)
    created = Optional(datetime)
    file_link = Optional(unicode)
    pkg_type = Optional(unicode, default='binary') # source or binary
    compress_type = Optional(unicode, default='zip')
    os = Optional(unicode, default='linux')
    arch = Optional(unicode, default='amd64')
    md5sum = Optional(unicode)
    down_count = Optional(int, default=0)

class Jenkins(db.Entity):
    name = Required(unicode, unique=True)
    phones = Set("Phone", cascade_delete=True)

class Phone(db.Entity):
    number = Required(unicode, unique=True)
    brand = Optional(unicode)
    model = Optional(unicode)
    memory_size = Optional(int)
    jenkins = Optional(Jenkins)
    connected = Required(bool, default=True)
    job_name = Optional(str)
    width = Optional(int)
    height = Optional(int)
    screen_file = Optional(str)
    updated = Optional(datetime)
    records = Set("JobRecord")

class Job(db.Entity):
    name = Required(unicode, unique=True)
    author = Optional(unicode)
    code_url = Optional(unicode)
    username = Optional(unicode)
    password = Optional(unicode)
    jobrecords = Set("JobRecord")

class JobRecord(db.Entity):
    data = Required(LongStr)
    created = Optional(datetime)
    phone = Required(Phone)
    job = Optional(Job)


class Link(db.Entity):
    uri = Required(unicode, unique=True)
    name = Optional(unicode)
    favicon = Optional(unicode)
    visit_count = Optional(int, default=0)

class Timer(db.Entity):
    email = Required(unicode)
    mission = Required(unicode)
    created = Optional(date)
    count = Optional(int, default=1)

# for h15 only 2014-09-05
class Box(db.Entity):
    docker_id = Required(unicode, unique=True)
    author = Required(unicode)
    host = Optional(unicode)
    port = Optional(int)
    created = Optional(datetime)
    ports = Set("BoxPort")

class BoxPort(db.Entity):
    local = Required(int)
    container = Required(int)
    box = Optional(Box)

#db.bind('sqlite', 'c:/test_db.sqlite', create_db=True)
db.bind(gcfg.db.dbtype, 
        host=gcfg.db.host, 
        user=gcfg.db.username, 
        passwd=gcfg.db.password, 
        db=gcfg.db.dbname)
db.generate_mapping(create_tables=True)

@db_session
def get_boxes():
    return select(b for b in Box)[:]

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
def add_jenkins_slave(name):
    if not Jenkins.get(name=name):
        Jenkins(name=name)

@db_session
def get_phones(limit=None):
    return select(p for p in Phone)[:]

@db_session
def get_jobs(limit=None):
    return select(j for j in Job)[:]

@db_session
def get_links(limit=None):
    return select(l for l in Link).order_by(desc(Link.visit_count))[:]

@db_session
def add_link(name, uri, favicon):
    print name, uri
    link = Link.get(uri=uri)
    if link:
        link.name = name
        link.favicon = favicon
    else:
        Link(name=name, uri=uri, favicon=favicon)

@db_session
def touch_link(uri):
    link = Link.get(uri=uri)
    if not link:
        return
    link.visit_count += 1


@db_session
def get_timers(email):
    return select(t for t in Timer if t.email == email)[:]
