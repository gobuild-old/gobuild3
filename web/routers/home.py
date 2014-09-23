# coding: utf-8
import time

import flask

bp = flask.Blueprint('home', __name__)

@bp.route('/ruok', methods=['GET', 'POST'])
def ruok():
    return 'imok'

@bp.route('/')
def home():
    address = flask.request.args.get('address')
    if address:
        return flask.redirect('/repo/'+address, 302)
    return flask.render_template('index.html')
