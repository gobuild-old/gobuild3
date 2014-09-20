# coding: utf-8
#from flask import Blueprint
#from flask import request, flash, redirect, url_for, render_template
import flask
import models
import jenkins
import time
import requests
import re

bp = flask.Blueprint('link', __name__)

@bp.route('/')
def home():
    return flask.render_template('link.html', links=models.get_links())

@bp.route('/add', methods=['POST'])
def add_link():
    uri = flask.request.form['uri']
    if not re.match('^\w+://', uri):
        uri = 'http://'+uri.rstrip('/')
    title = flask.request.form['title']
    favicon = uri+'/favicon.ico'
    try:
        r = requests.get(uri, timeout=10.0)
        if r.status_code != 200:
            raise Exception('url request got status code: %d' % r.status_code)
        if not title:
            m = re.search(r'<title>(.*?)</title>', r.text, re.M|re.I)
            if m:
                title = m.group(1).strip()
            else:
                title = 'unknown'
        #m = re.search(r'<link\s+rel=[\'"]+[\w\s]*?icon[\w\s]*?[\'"\s]+href=[\'"](.*?)[\'"]', r.text, re.M|re.I)
        m = re.search(r'<link.*?href=[\'"]([\w\d/]*/favicon.\w+)[\'"]', r.text, re.M|re.I)
        if m:
            favicon = m.group(1)
            if not re.match('^\w+://', favicon):
                import urlparse
                p = urlparse.urlparse(uri)
                favicon = p.scheme + '://'+p.netloc + favicon
    except Exception, e:
        flask.flash(str(e), 'error')
    else:
        models.add_link(title, uri, favicon)
        uri=''
        return flask.redirect(flask.url_for('link.home'))
    return flask.render_template('link.html', uri=uri, links = models.get_links())

@bp.route('/redirect', methods=['GET'])
def redirect():
    #return flask.render_template('link.html')
    uri = flask.request.args.get('uri')
    models.touch_link(uri)
    return flask.redirect(uri)

