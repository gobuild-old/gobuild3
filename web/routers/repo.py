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

@bp.route('/<path:reponame>')
@models.db_session
def home(reponame):
    repo = models.Repo.get(name=reponame)
    naturaltime = humanize.naturaltime(repo.updated)
    default_tag = request.args.get('tag', 'branch:master')
    builds = models.select(b for b in models.Build \
            if b.repo == repo).order_by(models.Build.updated)
    kwargs = dict(reponame=reponame, repo=repo, naturaltime=naturaltime, builds=builds,
            default_tag=default_tag)
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
def retrive():
    reponame = request.args.get('reponame')
    goos = request.args.get('goos')
    goarch = request.args.get('goarch')

    well = 'windows amd64\nsize: 1M\nsha: slalfjj\nmd5: lxlsle'
    file_link = 'http://www.baidu.com/index.php'
    return flask.jsonify(dict(status=0, message='success', 
        well=well, goos=goos, goarch=goarch, file_link=file_link))

@bp.route('/update')
def update():
    return flask.jsonify(dict(status=0, message='success'))

@bp.route('/commit')
def commit():
    return flask.jsonify(dict(status=0, message='success'))

