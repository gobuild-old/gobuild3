# coding: utf-8
import os
import json
import time
import datetime

import humanize
import flask
from flask import request, flash, redirect, url_for, render_template

import models
import gcfg

bp = flask.Blueprint('repo', __name__)

@bp.app_template_filter('strftime')
def strftime(value, format='%Y-%m-%d %H:%M:%S'):
    return value.strftime(format)

@bp.app_template_filter('human_duration')
def human_duration(value):
    return str(datetime.timedelta(seconds=value))

@bp.app_template_filter()
def basename(value): 
    return os.path.basename(value)

@bp.app_template_filter()
def str2html(value): 
    return flask.Markup(value.replace('\n', '<br>'))

@bp.route('/<path:reponame>')
@models.db_session
def home(reponame):
    repo = models.Repo.get(name=reponame)
    naturaltime = humanize.naturaltime(repo.updated)
    builds = models.select(b for b in models.Build \
            if b.repo == repo).order_by(models.Build.updated)

    active_tag = request.args.get('tag', 'branch:master')
    active_build = models.Build.get(repo=repo, tag=active_tag)

    kwargs = dict(reponame=reponame, repo=repo, naturaltime=naturaltime, builds=builds,
            active_tag=active_tag, active_build=active_build)
    return render_template('repo.html', **kwargs)

# FIXME: not finished build page
@bp.route('/build')
def build():
    reponame = request.args.get('reponame')
    tag = request.args.get('tag')
    return 'build - %s@%s' %(reponame, tag)

@bp.route('/retrive')
@models.db_session
def retrive():
    reponame = request.args.get('reponame')
    goos = request.args.get('goos')
    goarch = request.args.get('goarch')
    tag = request.args.get('tag')

    repo = models.Repo.get(name=reponame)

    build = models.Build.get(repo=repo, tag=tag)

    file = models.File.get(build=build, os=goos, arch=goarch)
    if not file:
        return flask.jsonify(dict(status=1, message='file not found'))

    repo.down_count += 1
    build.down_count += 1

    well = '{os} {arch}\n<b>File</b>\nsize: {size}\nsha: {sha}\nmd5: {md5}'.format(
            os=goos, arch=goarch, 
            size=humanize.naturalsize(file.size),
            md5=file.md5, sha=file.sha)
    return flask.jsonify(dict(status=0, message='success', 
        well=well, goos=goos, goarch=goarch, outlink=file.outlink, loglink=file.loglink))

@bp.route('/update', methods=['POST'])
@models.db_session
def update():
    def fv(name, default=None):
        return request.form.get(name, default)
    bid = int(fv('build_id'))
    build = models.Build[bid]
    build.status = fv('status')
    build.updated = datetime.datetime.today()
    build.details = fv('details')

    return flask.jsonify(dict(status=0, message='success'))

@bp.route('/commit', methods=['POST'])
@models.db_session
def commit():
    req = json.loads(request.data)
    build_id = int(req.get('build_id'))
    build = models.Build[build_id]
    build.downloadable = req.get('success', False)
    build.details = req.get('details')
    build.time_used = req.get('time_used')
    build.version = req.get('version')
    if build.downloadable:
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

