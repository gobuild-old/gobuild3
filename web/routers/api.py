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

bp = flask.Blueprint('api', __name__)

@bp.route('/')
def home():
    return flask.render_template('api.html')

@bp.route('/v1/repolist')
@models.db_session
def repolist():
    goos='windows'
    goarch='amd64'
    data = []
    for r in models.select(r for r in models.Recommend)[:]:
        item = dict(
            reponame=r.repo.name,
            alias=r.name,
            author=r.repo.author,
            description=r.repo.description,
            offical=r.repo.offcial,
            category=r.category.name if r.category else None,
            stars=r.repo.stars,
            osarch=goos+'-'+goarch,
            )
        files = []
        for b in r.repo.builds:
            if not b.downloadable:
                continue

            # actually only one loop
            file = {'label':b.tag, 'updated':b.updated}
            for f in models.select(f for f in models.File \
                    if f.build==b and f.os == goos and f.arch == goarch)[:1]:
                file.update({'binfiles': [os.path.basename(f.reponame)], # FIXME: need to parse from gobuildrc
                    'size': f.size, 'url': f.outlink, 'sha1': f.sha})
                files.append(file)
        if files:
            item['files'] = files
            data.append(item)

    data.append(dict(
        reponame = 'github.com/codeskyblue/cgotest',
        description='this is is just a test program',
        alias='cgotest', # this could be null
        author='unknown,lunny',
        offical=True,
        category='music',
        stars=18,
        files=[
            {'label': 'branch:master', 'url': 'http://gobuild3.qiniudn.com/github.com/gogits/gogs/branch-v-master/gogs-linux-386.tar.gz', 'binfiles': ['gogs'], 'sha1': '408eebced1c2cdbd363df2fe843831bf337d4273', 'size': 7000000},
            {'label': 'tag:v0.5.2', 'url': 'http://gobuild3.qiniudn.com/github.com/gogits/gogs/tag-v-v0.5.2/gogs-linux-386.tar.gz', 'binfiles': ['gogs'], 'sha1': '960e329d46ec7a79745cf3438eaf3c3151d38d97', 'size': 7100000}],
        ))
    return flask.jsonify({'status': 0, 'message': 'success', 'osarch': 'linux-386', 'data': data})
