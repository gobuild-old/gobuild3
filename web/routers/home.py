# coding: utf-8
import datetime
import time
import flask
import requests

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
                desc = checkrepo(reponame)
            except Exception as e:
                return flask.render_template('index.html', error=str(e))
            repo = models.Repo(name=reponame)
            repo.created = datetime.datetime.today()
            repo.description = desc
            repo.author = 'unknown .. unfinished'
            models.commit()

        return flask.redirect('/repo/'+reponame, 302)

    new = models.select(r for r in models.Repo).\
            order_by(models.desc(models.Repo.created))[:10]
    top = models.select(r for r in models.Repo).\
            order_by(models.desc(models.Repo.down_count))[:10]

    error = 'Beta version, only for test for the time now.'
    return flask.render_template('index.html', top_repos=top, new_repos=new, error=error)

