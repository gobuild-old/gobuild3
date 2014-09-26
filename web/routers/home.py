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
    return name

def checkrepo(name):
    ''' return desc '''
    payload = {'action': 'package', 'id': name}
    r = requests.get('http://go-search.org/api', params=payload)
    if not r.text.startswith('{'):
        raise Exception('error find package in go-search: %s' % r.text)

    d = r.json()
    print d
    if d['Name'] and d['Name'] != 'main':
        raise Exception('Repo: [%s] is a go-lib, this platform only support main package' % name)
    return d['Synopsis']

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

