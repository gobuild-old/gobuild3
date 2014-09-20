# coding: utf8
import time
import datetime
import json
import os
import threading
import random
import xmlrpclib

from flask import Blueprint
from flask import request, flash, redirect, url_for, render_template
import flask
import sh
import requests

import models
import gcfg

bp = Blueprint('box', __name__)

DATA_DIR = gcfg.cf.get('docker', 'data')
SVN_ADDR = 'https://svn-h15.gz.netease.com/svn/code/server'
DOCKER_IMAGE = 'hzsunshx:h15'


@bp.route('/')
def home():
    return render_template('box.html', boxes=models.get_boxes())

#pathjoin = os.path.join

TEAM_HOSTS = {
        'h15': ['10.246.13.180'],
        }
CLIENT_PORT = 7413

def newrpc(host):
    rpc = xmlrpclib.ServerProxy("http://%s:%d/"%(host, CLIENT_PORT), allow_none=True)
    return rpc

@bp.route('/create', methods=['POST'])
@models.db_session
def create():
    team = request.form['team']
    hosts = TEAM_HOSTS.get(team)
    if not hosts:
        flash("This group(%s) got no machines"%(team), "warn")
        return render_template('box.html', boxes=models.get_boxes())

    host = random.choice(hosts) # FIXME: for quick code
    name = request.form['name']
    if not name.startswith('hz') and not name.startswith('gz'):
        flash('What is your name? Are you kidding me!!!', 'warn')
        return render_template('box.html', boxes=models.get_boxes())
    PORT = '4000'

    # svn
    if models.Box.get(author=name):
        flash("One people only one server", "error")
        return render_template('box.html', boxes=models.get_boxes())

    try:
        docker_id = newrpc(host).create_container(name)
    except Exception as e:
        print 'ERROR docker run, detail:', str(e)
        flash('docker create error: '+str(e), 'error')
        return render_template('box.html', boxes=models.get_boxes())

    box = models.Box(author=name, docker_id=docker_id)
    box.host = host
    box.created = datetime.datetime.fromtimestamp(time.time())
    # FIXME: call use rpc
    ret = newrpc(host).docker('port', docker_id, PORT)
    port = int(ret.split(':', 1)[1])
    box.port = port # sudo docker port 4000

    for pcontainer, plocal in newrpc(host).ports(docker_id).items():
        pcontainer = int(pcontainer)
        bp = models.BoxPort(local=plocal, container=pcontainer)
        bp.box = box

    flash("create server success, system created", "success")
    return render_template('box.html', boxes=models.get_boxes())

@bp.route('/delete/<docker_id>')
def delete(docker_id):
    with models.db_session:
        box = models.Box.get(docker_id=docker_id)
        if not box:
            return flask.jsonify({'status':1, 'message': 'docker not exists'})
        else:
            name = box.author
            host = box.host
            #def _del_docker(docker_id):
            #    try:
            newrpc(host).delete_container(name, docker_id)
            #    except Exception as e:
            #        print 'DELETE Error:', str(e)
            #t = threading.Thread(target=_del_docker, args=(box.docker_id,))
            #t.daemon = True
            #t.start()
            for bp in box.ports:
                bp.delete()
            box.delete()
    return flask.jsonify({'status':0, 'message': 'delete success'})
    #return render_template('box.html', boxes=models.get_boxes())

@bp.route('/logs/<docker_id>')
@models.db_session
def logs(docker_id):
    box = models.Box.get(docker_id=docker_id)
    if not box:
        return 'docker id not exists anymore'
    ret = newrpc(box.host).docker('logs', docker_id)
    return ret

@bp.route('/api/port/<docker_id>')
@models.db_session
def ports(docker_id):
    box = models.Box.get(docker_id=docker_id)
    if not box:
        return flask.jsonify({'status':1, 'message': 'docker not exists'})
    msg = 'Port container -> public\n'
    for bp in box.ports:
        msg += '%d -> %d\n' %(bp.container, bp.local)
    return flask.jsonify({'status': 0, 'message': msg})

@bp.route('/api/svnup/<docker_id>')
def svnup(docker_id):
    with models.db_session:
        box = models.Box.get(docker_id=docker_id)
        if not box:
            return flask.jsonify({'status':1, 'message': 'docker not exists'})
        name = box.author
        host = box.host
        ret = newrpc(host).update_data(name)
        return flask.jsonify({'status':0, 'message': str(ret)})

@bp.route('/api/<action>/<docker_id>')
def control_docker(action, docker_id):
    actions = dict(start='SIGCONT', stop='SIGQUIT', restart='SIGUSR1', reload='SIGHUP')
    ok_actions = actions.keys()
    if action not in ok_actions:
        return flask.jsonify({
            'status': 1, 
            'message': 'actions should be one of <%s>'% ','.join(ok_actions)})
    with models.db_session:
        box = models.Box.get(docker_id=docker_id)
        if not box:
            return flask.jsonify({
                'status':2, 
                'message': 'docker not exists'})
        try:
            newrpc(box.host).control_container(docker_id, actions[action])
        except Exception as e:
            return flask.jsonify({'status': 2, 'message': action + ' failure:'+str(e) })
    return flask.jsonify({'status': 0, 'message': 'call %s sig:%s'%(action,actions[action])})

def popo_notify(to, msg):
    ''' @return True|False : if message send success '''
    r = requests.post('http://mt.nie.netease.com:7000/api/popo/send', data={'name':to, 'message': msg})
    return r.json().get('status') == 0

