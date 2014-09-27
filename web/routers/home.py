# coding: utf-8
import datetime
import time
import json
import flask
import requests
from flask import request, flash, redirect, url_for, render_template

import models

bp = flask.Blueprint('home', __name__)

@bp.route('/ruok', methods=['GET', 'POST'])
def ruok():
    return 'imok'

def cleanname(name):
    for prefix in 'http://', 'https://', '/':
        if name.startswith(prefix):
            name = name[len(prefix):]
    for suffix in '/', '.git':
        if name.endswith(suffix):
            name = name[:-len(suffix)]
    name = name.replace(':', '/')
    return name

def checkrepo(name):
    ''' return desc '''
    payload = {'pkgname': name}
    requests.get('https://gowalker.org/'+name) # call gowalker to load data
    r = requests.get('https://gowalker.org/api/v1/pkginfo', params=payload)
    d = r.json()
    if not d['id']:
        raise Exception('error load package in https://gowalker.org: %s' % r.text)

    if not d['cmd']:
        raise Exception('Repo: [%s] is a go-lib, this platform only support main package' % name)
    return d['synopsis']

@bp.route('/')
@models.db_session
def home():
    address = flask.request.args.get('address')
    if address:
        reponame = cleanname(address)
        if not models.Repo.get(name=reponame):
            try:
                nocheck = 'nocheck-'
                if reponame.startswith(nocheck):
                    reponame = reponame[len(nocheck):]
                    desc = 'unknown desc'
                else:
                    desc = checkrepo(reponame)
            except Exception as e:
                force_add = '''If you confirm this is a go main package. Click <a class="btn btn-warning btn-xs" href="/?address=nocheck-%s">force add</a>''' %(reponame)
                error = str(e) + ' <br>- ' + force_add
                return flask.render_template('index.html', error=flask.Markup(error))
            repo = models.Repo(name=reponame)
            repo.created = datetime.datetime.today()
            repo.description = desc
            repo.author = 'unknown .. unfinished'
            models.commit()

        return flask.redirect('/'+reponame, 302)

    new = models.select(r for r in models.Repo).\
            order_by(models.desc(models.Repo.created))[:10]
    top = models.select(r for r in models.Repo).\
            order_by(models.desc(models.Repo.down_count))[:10]

    error = 'Beta version, only for test for the time now.'
    return flask.render_template('index.html', top_repos=top, new_repos=new, error=error)

@bp.route('/<path:reponame>')
@models.db_session
def repo(reponame):
    repo = models.Repo.get(name=reponame)
    if not repo:
        return flask.redirect('/?address='+reponame)

    builds = models.select(b for b in models.Build \
            if b.repo == repo).order_by(models.Build.updated)

    active_tag = request.args.get('tag', 'branch:master')
    build = models.Build.get(repo=repo, tag=active_tag)
    osarchs = [] 
    if build and build.osarchs:
        osarchs = json.loads(build.osarchs)

    kwargs = dict(repo=repo, builds=builds,
            active_tag=active_tag, build=build, osarchs=osarchs)
    return render_template('repo.html', **kwargs)

@bp.route('/badge/<path:whatever>')
def badge(whatever):
    return flask.send_from_directory('static/images', 'badge.svg')
