#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import flask
import pyoauth2
import datetime

import models

KEY = '27b016c9b59be5d05a61'
SECRET = 'ef8fa87d87f4ee56cf68245c86b4f080e3f122fb'
CALLBACK = 'http://mt.nie.netease.com/timer/login'
client = pyoauth2.Client(KEY, SECRET, 
                site='https://api.github.com', 
                authorize_url='https://github.com/login/oauth/authorize',
                token_url='https://github.com/login/oauth/access_token')

authorize_url = client.auth_code.authorize_url(redirect_uri=CALLBACK, scope='user,gist')

bp = flask.Blueprint('timer', __name__)

@bp.route('/')
def home():
    login_data = flask.session.get('login_data', None)
    return flask.render_template('timer.html', oauth_url=authorize_url, login_data=login_data)

@bp.route('/record/<email>', methods=['GET'])
def view_record(email):
    login_email = flask.session.get('login_data', {}).get('email')
    print 'allow timer:', login_email
    if email != login_email:
        if login_email != 'codeskyblue@gmail.com':
            return 'no authorized, login with you account'
    return flask.render_template('timer_record.html', records=models.get_timers(email), email=email)
        

@bp.route('/add_record', methods=['POST'])
@models.db_session
def add_record():
    mission = flask.request.form['mission']
    done = flask.request.form.get('done', False)
    #status = 'FINISH' if done else 'START'
    #print 'record mission(%s)=%s' %(status, mission)
    #with open('mission.txt', 'a') as file:
    #    timestamp = time.strftime('%Y/%M/%D %H:%M:%S')
    #    file.write('%s - %s: %s\n' %(timestamp, status, mission.encode('utf-8')))

    login_data = flask.session.get('login_data', None)
    email = login_data.get('email') if login_data else 'hzsunshx@corp.netease.com'
    if done:
        # access_token = pyoauth2.AccessToken(client, login_data.get('token'))
        today = datetime.date.today()
        t = models.Timer.get(email=email, mission=mission, created=today)
        if t:
            t.count += 1
        else:
            t = models.Timer(email=email, mission=mission)
            t.created = today
        #print email, mission, status
        #kjt = models.Timer(email=email, mission=mission)
        #t.created = today
        #t.status = status
        #print access_token.request('POST', '/gists', data=json.dumps({
    return flask.jsonify({'success': True})


@bp.route('/login')
def login():
    code = flask.request.args.get('code')
    access_token = client.auth_code.get_token(code, redirect_uri=CALLBACK, parse='query')
    ret = access_token.get('/user')
    avatar_url, email = ret.parsed.get('avatar_url'), ret.parsed.get('email')
    login_data = {'avatar': avatar_url, 'email': email, 'token': access_token.token}
    #print '-' * 80
    print 'login-data:', login_data
    flask.session['login_data'] = login_data
    return flask.redirect(flask.url_for('timer.home'))

@bp.route('/logout')
def logout():
    # remove the username from the session if it's there
    flask.session.pop('login_data', None)
    return flask.redirect(flask.url_for('timer.home'))
