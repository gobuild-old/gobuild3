# coding: utf-8
import os
import json
import time
import datetime
import uuid

import humanize
import flask
from flask import request, flash, redirect, url_for, render_template

import models
import gcfg

bp = flask.Blueprint('api', __name__)

@bp.route('/')
def home():
    return flask.render_template('api.html')

@bp.route('/v1/category.json')
@models.db_session
def list_category():
    cs = []
    for cg in models.select(c for c in models.Category)[:]:
        cs.append(cg.name)
    return json.dumps(cs)

@bp.route('/v1/recommend', methods=['POST'])
@models.db_session
def recommend():
    reponame = request.form.get('reponame')
    repo = models.Repo.get(name=reponame)
    if not repo:
        return flask.jsonify(dict(status=2, message='repo %s not found'%reponame))

    author = request.form.get('email')
    reason = request.form.get('reason')
    category = request.form.get('category')
    rc = models.Recommend.get(repo=repo)
    if rc:
        return flask.jsonify(dict(status=1, message='already recommend by %s' %(
            rc.author)))
    rc = models.Recommend(repo=repo, author=author, reason=reason)
    rc.name = repo.name
    rc.created = datetime.datetime.today()
    rc.updated = datetime.datetime.today()
    rc.checked = False
    rc.uuid = '%s-%s' %(uuid.uuid4(), uuid.uuid1())
    cg = models.Category.get(name=category) or \
            models.Category(name=category)
    rc.category = cg

    print author, reason
    return flask.jsonify(dict(status=0, message='success'))

@bp.route('/v1/repolist')
@models.db_session
def repolist():
    goos=request.args.get('os', 'windows')
    goarch=request.args.get('arch', 'amd64')
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

    dict(
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
        )
    return flask.jsonify({'status': 0, 'message': 'success', 'osarch': goos+'-'+goarch, 'data': data})
