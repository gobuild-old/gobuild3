# coding: utf-8
import flask

bp = flask.Blueprint('donate', __name__)

@bp.route('/')
def home():
    return flask.render_template('donate.html')
