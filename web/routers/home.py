# coding: utf-8
import datetime
import time
import flask

import models

bp = flask.Blueprint('home', __name__)

@bp.route('/ruok', methods=['GET', 'POST'])
def ruok():
    return 'imok'

def cleanname(name):
    for prefix in 'http://', 'https://':
        if name.startswith(prefix):
            name = name[len(prefix):]
    for suffix in '/', '.git':
        if name.endswith(suffix):
            name = name[:-len(suffix)]
    return name

@bp.route('/')
@models.db_session
def home():
    address = flask.request.args.get('address')
    if address:
        reponame = cleanname(address)
        if not models.Repo.get(name=reponame):
            repo = models.Repo(name=reponame)
            repo.created = datetime.datetime.today()
            repo.description = '.. unfinished'
            repo.author = '.. unfinished'
            models.commit()

        return flask.redirect('/repo/'+address, 302)

    new = models.select(r for r in models.Repo).\
            order_by(models.desc(models.Repo.created))[:10]
    top = models.select(r for r in models.Repo).\
            order_by(models.desc(models.Repo.down_count))[:10]

    error = 'Beta version, only for test for the time now. For data may deleted anytime!!!'
    return flask.render_template('index.html', top_repos=top, new_repos=new, error=error)
