# coding: utf-8
import time
import json
import datetime
import flask
from flask import request, flash, redirect, url_for, render_template

import taskqueue
import models

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
            if b.build == build).order_by(models.Job.created)

    kwargs = dict(repo=repo, build=build, jobs=jobs)
    return render_template('tasklist.html', **kwargs)

@bp.route('/update', methods=['POST'])
@models.db_session
def update():
    def fv(name, default=None):
        return request.form.get(name, default)
    bid = int(fv('id'))
    job = models.Job[bid]
    job.status = fv('status')
    job.updated = datetime.datetime.today()
    job.output = fv('output', '')

    return flask.jsonify(dict(status=0, message='success'))

@bp.route('/commit', methods=['POST'])
@models.db_session
def commit():
    req = json.loads(request.data)
    job_id = int(req.get('id'))
    job = models.Job[job_id]
    job.updated = datetime.datetime.today()
    job.output = req.get('output')

    build = job.build
    if req.get('success', False):
        build.downloadable = True
        #build.details = req.get('output')
        build.time_used = req.get('time_used')
        build.version = req.get('version')

        for osarch, ds in req.get('files').items():
            goos, arch = osarch.strip().split('_')
            file = models.File.get(build=build, os=goos, arch=arch) or \
                    models.File(build=build, os=goos, arch=arch, reponame=build.repo.name)
            file.loglink = ds.get('loglink')
            file.outlink = ds.get('outlink')
            file.size = ds.get('size')
            file.md5 = ds.get('md5')
            file.sha = ds.get('sha')
            #print osarch, ds
    return flask.jsonify(dict(status=0, message='success'))

@bp.route('/apply')
@models.db_session
def apply():
    job_id = taskqueue.que.get()
    print 'apply', job_id
    if not job_id:
        return flask.jsonify(dict(job_id=0))
    job = models.Job[job_id]
    reponame = job.build.repo.name
    tag = job.build.tag
    return flask.jsonify(dict(job_id=job_id, reponame=reponame, tag=tag))

@bp.route('/new')
@models.db_session
def newtask():
    build = models.Build[1]
    print build
    b = models.Job(build=build, status='initing')
    models.commit()
    taskqueue.notify.put(b.id)
    return str(b.id)
