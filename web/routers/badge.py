# coding: utf-8
import datetime
import models
import flask
from flask import render_template, make_response, request

bp = flask.Blueprint('badge', __name__)

@bp.route('/<path:reponame>/downloads.svg')
@models.db_session
def downloads(reponame):
    repo = models.Repo.get(name=reponame)
    total = repo.down_count if repo else '?'
    etag = str(total)
    if etag == request.headers.get('If-None-Match'):
        return flask.Response(status=304)

    status = '%s downloads' %(total)
    response = make_response(render_template('downloads.svg', status=status))
    response.headers['Content-Type'] = 'image/svg+xml'
    response.headers['Last-Modified'] = datetime.datetime.today() # no much use
    response.headers['ETag'] = etag # chrome not support ETag
    return response

@bp.route('/<path:whatever>/download.png')
def gobuildv1_badge(whatever):
    return flask.send_from_directory('static/images', 'badge.svg')

