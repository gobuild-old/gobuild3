#!/usr/bin/env python
# coding: utf-8

import json
import os
import re
import sys
import signal
import StringIO
import time
import traceback
import threading

import qiniu.io
import qiniu.conf
import requests
import sh

import gcfg

qiniu.conf.UP_HOST = 'up.qiniug.com'

DOCKER_IMAGE = gcfg.slave.docker_image

server = gcfg.master.server.rstrip('/')
task_url = server+'/task'
safe_token = gcfg.safe.token

pathjoin = os.path.join

def handler(signum, frame):
    print 'Signal handler called with signal', signum
    sys.exit(1)

# Set the signal handler and a 5-second alarm
signal.signal(signal.SIGINT, handler)

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
        raise Exception(err)
    return r.get('outlink')

def docker_build(job_id, reponame, tag):
    print 'Handle', job_id, reponame, tag

    workspace = os.path.join(os.getcwd(), 'data', str(job_id))
    if not os.path.exists(workspace):
        os.makedirs(workspace)

    reply = rpost('/task/update', data=dict(id=job_id, status='building'))
    print 'reply:', reply
    bufio = StringIO.StringIO()
    lock = threading.Lock()
    running = True
    def _loop_report_stdout():
        pos = 0
        while True:
            lock.acquire()
            if not running: 
                lock.release()
                break
            if pos == bufio.tell():
                time.sleep(1)
                lock.release()
                continue
            bufio.read()
            reply = rpost('/task/update', data=dict(
                id=job_id, status='building', output=bufio.buf))
            print reply
            sys.stdout.write(bufio.buf[pos:])
            pos = bufio.tell()
            lock.release()
        print 'loop ended'
    t = threading.Thread(target=_loop_report_stdout)
    t.setDaemon(True)
    t.start()

    ret = sh.docker('run', '--rm',
            '-v', workspace+':/output',
            '-e', 'TIMEOUT=10m',
            '-e', 'HTTP_PROXY=%s'%gcfg.slave.http_proxy,
            DOCKER_IMAGE,
            '--repo', reponame,
            '--tag', tag, 
            _err_to_out=True, _out=bufio, _tee=True, _ok_code=range(255))

    running = False
    t.join()

    jsonpath = pathjoin(workspace, 'out.json')
    out = json.load(open(pathjoin(workspace, 'out.json'))) if \
            os.path.exists(jsonpath) else {}
    out['success'] = (ret.exit_code == 0)
    out['output'] = str(ret)
    out['id'] = job_id
    out['safe_token'] = safe_token
    if not out['success']:
        rpost('/task/update', data=dict(id=job_id, status='error', 
            output = str(ret)))
        return

    rpost('/task/update', data=dict(
        id=job_id, 
        status='uploading'))

    print 'Uploading files'
    for osarch, info in out['files'].items():
        outname = info.get('outname')
        safetag = ''.join(re.findall('[\w\d-_.]+', tag.replace(':', '-v-')))
        key = pathjoin(reponame, safetag, outname)
        print 'File:', outname, key
        info['outlink'] = upload_file(key, pathjoin(workspace, outname))

        logname = info.get('logname')
        key = pathjoin(str(job_id), osarch, logname)
        #print 'Log: ', logname
        info['loglink'] = upload_file(key, pathjoin(workspace, logname))

    json.dump(out, open('sample.json', 'w'))
    reply = rpost('/task/commit', data=json.dumps(out))
    print 'commit reply:', reply

def main():
    while True:
        try:
            r = rpost('/task/apply')
            job_id = r.get('job_id')
            if not isinstance(job_id, int):
                print 'error: got an invalid job_id: %s' % job_id
                time.sleep(2)

            if job_id:
                reponame = r.get('reponame')
                tag = r.get('tag')
                
                docker_build(job_id, reponame, tag)
            else:
                sys.stdout.write('%s idle\n' % time.strftime("[%Y-%m-%d %H:%M:%S]"))
        except Exception as e:
            traceback.print_exc()
            print 'exception:', e
            sleep = 5
            print 'retry after %d seconds' %(sleep)
            time.sleep(sleep)

if __name__ == '__main__':
    main()
