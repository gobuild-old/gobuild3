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
    v = json.load(open('out.json'))
    kwargs['prop'] = v
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

    file = models.File.get(reponame=reponame, os=goos, arch=goarch)
    if not file:
        return flask.jsonify(dict(status=1, message='file not found'))

    well = '{os} {arch}\nsize: {size}\nsha: {sha}\nmd5: {md5}'.format(
            os=goos, arch=goarch, 
            size=humanize.naturalsize(file.size),
            md5=file.md5sum, sha=file.shasum)
    file_link = 'http://www.baidu.com/index.php'
    return flask.jsonify(dict(status=0, message='success', 
        well=well, goos=goos, goarch=goarch, file_link=file.file_link))

@bp.route('/update')
def update():
    return flask.jsonify(dict(status=0, message='success'))

@bp.route('/commit')
def commit():
    return flask.jsonify(dict(status=0, message='success'))

