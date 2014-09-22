# coding: utf-8
import os
import json
import time
import datetime

import flask
from flask import request, flash, redirect, url_for, render_template

import models
import gcfg

bp = flask.Blueprint('repo', __name__)

@bp.route('/<path:reponame>')
def home(reponame):
    kwargs = {'reponame': reponame}
    v = json.load(open('out.json'))
    print v
    kwargs['prop'] = v
    return render_template('repo.html', **kwargs)
