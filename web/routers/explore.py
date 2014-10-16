# coding: utf-8
import flask
import models

from flask import request, render_template

bp = flask.Blueprint('explore', __name__)

@bp.route('/')
@models.db_session
def home():
    page_nr = int(request.args.get('p', '0'))
    page_size = 15
    recommends = models.select(rc for rc in models.Recommend \
            if rc.checked)[page_nr*page_size:page_size]
    return render_template('explore.html', recommends=recommends)

