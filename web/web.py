#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# web
#

import os
import flask
import humanize

import ansi2html
import models


app = flask.Flask(__name__)
app.secret_key = 'some_secret'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # max 16M
#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.template_filter()
def basename(value): 
    return os.path.basename(value)

@app.template_filter()
def human_duration(value):
    return str(datetime.timedelta(seconds=value))

@app.template_filter()
def naturaltime(value):
    return humanize.naturaltime(value)

@app.template_filter()
def strftime(value, format='%Y-%m-%d %H:%M:%S'):
    if value is None: return 'unknown'
    return value.strftime(format)

@app.template_filter('ansi2html')
def _ansi2html(text):
    return flask.Markup(ansi2html.convert(text))

def register_routers():
    from routers import home
    app.register_blueprint(home.bp, url_prefix='')

    for blueprint in 'home', 'repo', 'task', 'donate', 'storage', 'api', 'badge', 'explore':
        exec 'from routers import %s' %(blueprint) 
        bp = eval(blueprint+'.bp')
        app.register_blueprint(bp, url_prefix='/'+blueprint)


#@app.route('/login/', methods=['GET', 'POST'])
#def login():
#    app.logger.debug("login")
#    error = None
#    if request.method == 'POST':
#        if request.form['username'] != 'admin' or \
#                request.form['password'] != 'secret':
#            error = 'Invalid credentials'
#        else:
#            flash('You are successfully logged in')
#            return redirect(url_for('index'))
#    return render_template('login.html', error=error)

port = os.getenv('PORT') or '5000'
debug = os.getenv('DEBUG') in ('true', '1') or False
if __name__ == '__main__':
    register_routers()
    app.run(debug=debug, host='0.0.0.0', port=int(port), threaded=True)
