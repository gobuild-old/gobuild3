#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# web
#

import os
import flask
import models

app = flask.Flask(__name__)
app.secret_key = 'some_secret'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # max 16M
#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def register_routers():
    from routers import home
    app.register_blueprint(home.bp, url_prefix='')

    for blueprint in 'home', 'repo', 'donate':
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
    app.run(debug=debug, host='0.0.0.0', port=int(port))
