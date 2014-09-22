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
    from routers import home#, link, result
    #app.register_blueprint(doc.bp, url_prefix='/doc')
    #app.register_blueprint(link.bp, url_prefix='/link')
    #app.register_blueprint(timer.bp, url_prefix='/timer')
    #app.register_blueprint(result.bp, url_prefix='/result')
    app.register_blueprint(home.bp, url_prefix='')


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
if __name__ == '__main__':
    register_routers()
    app.run(debug=True, host='0.0.0.0', port=int(port))
