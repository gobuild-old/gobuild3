# coding: utf-8
import datetime
import time
import json
import flask
import requests
from flask import request, flash, redirect, url_for, render_template

import models
import taskqueue

bp = flask.Blueprint('home', __name__)

@bp.route('/ruok', methods=['GET', 'POST'])
def ruok():
    return 'imok'

def cleanname(name):
    name = name.strip()
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
        raise Exception('Error load package in \
                <a href="https://gowalker.org/{name}">https://gowalker.org/{name}</a>'.format(
                    name=name))

    if not d['cmd']:
        raise Exception('Repo: [%s] is a go-lib, this platform only support main package' % name)
    return d['synopsis']

@bp.route('/')
@models.db_session
def home():
    address = flask.request.args.get('address')
    nocheck = (flask.request.args.get('force') == 'true')
    if address:
        reponame = cleanname(address)
        if not models.Repo.get(name=reponame):
            try:
                if nocheck:
                    if flask.request.args.get('reponame') != address:
                        return flask.render_template('index.html', error='reponame not match')

                    desc = 'unknown desc - forceadd'
                else:
                    desc = checkrepo(reponame)
            except Exception as e:
                force_add = '''
                If you confirm this is a go main package. 
                <form class="pull-right">
                    <input type="hidden" name="address" value="{reponame}">
                    <input type="hidden" name="force" value="true">
                    <input type="text" name="reponame" placeholder="Type repo name again">
                    <button class="btn btn-warning btn-xs">force add</button>
                </form>'''.format(reponame=reponame)
                error = str(e) + ' <br>- ' + force_add
                return flask.render_template('index.html', error=flask.Markup(error))
            repo = models.Repo(name=reponame)
            repo.created = datetime.datetime.today()
            repo.description = desc
            repo.author = 'unknown .. unfinished'

            # add new job
            build = models.Build(repo=repo, tag='branch:master', status='initing')
            job = models.Job(build=build, status='initing', created=datetime.datetime.today())
            models.commit()
            taskqueue.que.put(job.id)

        return flask.redirect('/'+reponame, 302)

    new = models.select(r for r in models.Repo).\
            order_by(models.desc(models.Repo.created))[:10]
    top = models.select(r for r in models.Repo).\
            order_by(models.desc(models.Repo.down_count))[:10]

    #error = 'Beta version, only for test for the time now.'
    error=None
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

    categorys = []
    for cg in models.select(c for c in models.Category)[:]:
        categorys.append(cg.name)
    kwargs = dict(repo=repo, builds=builds, 
            categorys=categorys,
            active_tag=active_tag, 
            build=build, osarchs=osarchs)
    return render_template('repo.html', **kwargs)

#
# compatible with v1.gobuild
#
@bp.route('/download/<path:reponame>')
def download(reponame):
    return redirect('/'+reponame)

@bp.route('/<path:reponame>/<tag>/linux/<arch>')
@bp.route('/<path:reponame>/<tag>/windows/<arch>')
@bp.route('/<path:reponame>/<tag>/darwin/<arch>')
def v1_link(reponame, tag, arch):
    return redirect('http://v1.gobuild.io/'+flask.request.path)
