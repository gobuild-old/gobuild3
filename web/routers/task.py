# coding: utf-8
import time
import flask
from flask import request, flash, redirect, url_for, render_template

import taskqueue

bp = flask.Blueprint('task', __name__)

@bp.route('/apply')
def apply():
    task = taskqueue.que.get()
    return flask.jsonify(dict(task=task))

import models

@bp.route('/new')
@models.db_session
def newtask():
    b = models.Build(status='initing', tag='branch:dev')
    models.commit()
    taskqueue.notify.put('12345')
    return str(b.id)
