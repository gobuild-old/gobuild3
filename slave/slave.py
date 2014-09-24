#!/usr/bin/env python
# coding: utf-8

import time
import json
import sys

import requests
import qiniu.io

import gcfg

server = gcfg.master.server.rstrip('/')
task_url = server+'/task'
safe_token = gcfg.safe.token

def safe_patch(fn):
    def _decorator(*args, **kwargs):
        data = kwargs.get('data')
        if not data:
            data = kwargs['data'] = {}
        if isinstance(data, dict):
            data.update({'safe_token': safe_token})
        return fn(*args, **kwargs)
    return _decorator

def rget(name, **kwargs):
    return requests.get(server+name, **kwargs).json()

@safe_patch
def rpost(name, **kwargs):
    return requests.post(server+name, **kwargs).json()

def upload_file(key, filename):
    extra = qiniu.io.PutExtra()
    r = rpost('/storage/apply', data={'key':key})
    ret, err = qiniu.io.put_file(r.get('uptoken'), key, filename, extra)
    if err is not None:
        sys.stderr.write('error: %s \n' % err)
        raise err
    return r.get('outlink')

def main():
    while True:
        try:
            r = rpost('/task/apply')
            job_id = r.get('job_id')
            if not isinstance(job_id, int):
                print 'error: got an invalid job_id: %s' % job_id
                time.sleep(2)

            if job_id:
                reply = rpost('/task/update', data=dict(id=job_id, status='building'))
                print 'reply:', reply
                time.sleep(2)
                out = json.load(open('out.json'))
                out['id'] = job_id
                reply = rpost('/task/commit', data=json.dumps(out))
                print 'commit reply:', reply
            else:
                sys.stdout.write('.')
                sys.stdout.flush()
        except Exception as e:
            print 'exception:', e
            sleep = 5
            print 'retry after %d seconds' %(sleep)
            time.sleep(sleep)

if __name__ == '__main__':
    main()
    #print upload_file('hello2.txt', 'out.json')
