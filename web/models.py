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
    shasum = Optional(unicode)
    down_count = Optional(int, default=0)

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
