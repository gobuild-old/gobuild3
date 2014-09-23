#!/usr/bin/env python
# coding: utf-8

import requests
import time

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
            reply = rpost('commit', data=open('out.json'))
            print 'commit reply:', reply

        print r

if __name__ == '__main__':
    main()
