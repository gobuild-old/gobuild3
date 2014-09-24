#!/usr/bin/env python
# coding: utf-8

import requests
import time
import json

import gcfg

task_url = gcfg.master.task_url.rstrip('/')

def rget(name, **kwargs):
    return requests.get(task_url+'/'+name, **kwargs).json()

def rpost(name, **kwargs):
    return requests.post(task_url+'/'+name, **kwargs).json()

def main():
    while True:
        r = rget('apply')
        job_id = r.get('job_id')
        if job_id:
            reply = rpost('update', data=dict(id=job_id, status='building'))
            print 'reply:', reply
            time.sleep(2)
            out = json.load(open('out.json'))
            out['id'] = job_id
            reply = rpost('commit', data=json.dumps(out))
            print 'commit reply:', reply

        print r

if __name__ == '__main__':
    main()
