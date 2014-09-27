# coding: utf-8
import time
import json
import datetime
import Queue

import flask
from flask import request, flash, redirect, url_for, render_template

import taskqueue
import models
import gcfg

bp = flask.Blueprint('task', __name__)

@bp.route('/<int:tid>')
@models.db_session
def home(tid):
    job = models.Job.get(id=tid)
    repo = job.build.repo
    return render_template('task.html', repo=repo, job=job)

@bp.route('/list/<int:bid>')
@models.db_session
def tasklist(bid):
    build = models.Build.get(id=bid)
    repo = build.repo

    jobs = models.select(b for b in models.Job \
            if b.build == build).order_by(models.desc(models.Job.created))

    kwargs = dict(repo=repo, build=build, jobs=jobs)
    return render_template('tasklist.html', **kwargs)

@bp.route('/update', methods=['POST'])
@models.db_session
def update():
    if request.form.get('safe_token') != gcfg.safe.token:
        return flask.jsonify(dict(content=None))

    def fv(name, default=None):
        return request.form.get(name, default)
    bid = int(fv('id'))
    job = models.Job[bid]
    job.status = fv('status')
    job.updated = datetime.datetime.today()
    job.build.status = job.status
    output = fv('output')
    if output:
        if fv('append'):
            job.output += output
        else:
            job.output = output

    return flask.jsonify(dict(status=0, message='success'))

@bp.route('/commit', methods=['POST'])
@models.db_session
def commit():
    req = json.loads(request.data)
    if req.get('safe_token') != gcfg.safe.token:
        return flask.jsonify(dict(content=None))

    job_id = int(req.get('id'))
    job = models.Job[job_id]
    job.updated = datetime.datetime.today()
    #job.output = req.get('output')
    job.version = req.get('version')
    job.gobuildrc = req.get('gobuildrc')

    success = req.get('success', False)
    job.status = 'finished' if success else 'error'
    print 'job-status:', job.id, job.status

    build = job.build
    build.lastest_job = job.id
    build.status = job.status
    if req.get('success', False):
        build.downloadable = True
        build.time_used = req.get('time_used')
        build.version = req.get('version')
        build.repo.updated = build.updated = job.updated
        build.repo.downloadable = True

        osarch_map = {}
        for osarch, ds in req.get('files').items():
            goos, arch = osarch.strip().split('_')

            archs = osarch_map.get(goos, [])
            archs.append(arch)
            osarch_map[goos] = archs


            file = models.File.get(build=build, os=goos, arch=arch) or \
                    models.File(build=build, os=goos, arch=arch, reponame=build.repo.name)
            file.loglink = ds.get('loglink', '')
            file.outlink = ds.get('outlink')
            file.size = ds.get('size')
            file.md5 = ds.get('md5')
            file.sha = ds.get('sha')
            #print osarch, ds

        # store in format: [{"windows": ["386", "amd64"]},..]
        store_list = []
        for goos in 'windows', 'linux', 'darwin':
            archs = osarch_map.get(goos)
            if archs:
                archs.sort()
                store_list.append([goos, archs])
        build.osarchs = json.dumps(store_list)

    return flask.jsonify(dict(status=0, message='success'))

@bp.route('/apply', methods=['POST'])
@models.db_session
def apply():
    if request.form.get('safe_token') != gcfg.safe.token:
        return flask.jsonify(dict(content=None))

    try:
        job_id = taskqueue.que.get_nowait()
    except Queue.Empty:
        return flask.jsonify(dict(job_id=0))
    job = models.Job[job_id]
    reponame = job.build.repo.name
    tag = job.build.tag
    return flask.jsonify(dict(job_id=job_id, reponame=reponame, tag=tag))

@bp.route('/new')
@models.db_session
def newtask():
    build = models.Build[1]
    b = models.Job(build=build, status='initing')
    b.created = datetime.datetime.today()
    models.commit()
    taskqueue.que.put(b.id)
    return str(b.id)

@bp.route('/build')
@models.db_session
def build():
    reponame = request.args.get('reponame')
    tag = request.args.get('tag')

    repo = models.Repo.get(name=reponame)
    build = models.Build.get(repo=repo, tag=tag) or \
            models.Build(repo=repo, tag=tag)
    job = models.Job(build=build, status='initing')
    job.created = datetime.datetime.today()
    models.commit()
    taskqueue.que.put(job.id)
    return redirect('/task/%d' % job.id)

