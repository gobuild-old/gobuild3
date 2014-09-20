# coding: utf-8
from flask import Blueprint
from flask import request, flash, redirect, url_for, render_template
import flask
import models
import time
import datetime
import json
import os

import requests

import gcfg

bp = Blueprint('job', __name__)
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__) or '.', 'static/images/screenshot')
SCREENSHOT_DIR = 'static/images/screenshot'
JENKINS_URL = gcfg.cf.get('jenkins', 'domain')

@bp.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

@bp.route('/')
def home():
    return render_template('job.html', phones=models.get_phones(), jenkins_url=JENKINS_URL)

@bp.route('/phone')
def phone():
    return render_template('phone.html', phones=models.get_phones(), jenkins_url=JENKINS_URL)

@bp.route('/create', methods=['POST'])
def create_job():
    j = gcfg.JENKINS
    job_name = request.form['job-name']
    code_uri = request.form['code-uri']
    username = request.form['username']
    password = request.form['password']
    author = 'anonymous' # FIXME: use yixin oauth2
    with models.db_session:
        if models.Job.get(name=job_name):
            flash("job_name conflict, choose another name", "error")
            return render_template('job.html', phones=models.get_phones())
        job = models.Job(name=job_name)
        job.author = author
        job.code_url = code_uri
        job.username = username
        job.password = password
        models.commit()
        flash("job created success", "success")
        return render_template('job.html', phones=models.get_phones())
    #phone_list = request.form.getlist('phoneid')
    #if not phone_list:
    #    flash("select phone you would like to use", "error")
    #    return render_template('job.html', phones=models.get_phones())
    #links = []
    # FIXME: code need to clean below

    '''
    with models.db_session:
        for phoneid in phone_list:
            p = models.Phone[phoneid]
            build_number = j.get_job_info(p.job_name)['nextBuildNumber']
            j.build_job(p.job_name, dict(TESTCODE=code_uri))
            links.append(j.server + 'job/'+p.job_name+'/'+str(build_number))
    '''

def popo_notify(to, msg):
    ''' @return True|False : if message send success '''
    r = requests.post('http://mt.nie.netease.com:7000/api/popo/send', data={'name':to, 'message': msg})
    return r.json().get('status') == 0

@bp.route('/api/start', methods=['POST'])
def start_job():
    name = request.form.get('name')
    phones = request.form.getlist('phone')
    popo = request.form.get('popo')
    if not name:
        return flask.jsonify({'status': 1, 'message': 'need var "name" -- the job name'})
    if popo:
        def _test():
            popo_notify(popo, '=AIRTEST= Start test on '+ ','.join(phones))
            for p in phones:
                time.sleep(2)
                popo_notify(popo, '=AIRTEST= Test on [%s] SUCCESS\nhttp://www.baidu.com' %(p))
        import threading
        t = threading.Thread(target=_test)
        t.daemon = True
        t.start()
    return flask.jsonify({'status': 0, 'message': 'started ' + name +', this is test message'})

@bp.route('/api/list')
def list_all():
    out = ''
    with models.db_session:
        for p in models.select(p for p in models.Phone)[:]:
            out += '* %s-%s\n' %(p.brand, p.model)
    return flask.jsonify({'status': 0, 'message': out})

def file2name(screen_file):
    filename = os.path.join(SCREENSHOT_DIR, screen_file+'.png')
    filename_small = os.path.join(SCREENSHOT_DIR, screen_file+'-small.png')
    return filename, filename_small

@bp.route('/update', methods=['POST'])
def update_phone():
    try:
        with models.db_session:
            node_name = request.form['node-name']
            node = models.Jenkins.get(name=node_name) or models.Jenkins(name=node_name)
            devno = request.form['devno']
            p = models.Phone.get(number=devno) or models.Phone(number=devno)
            p.brand = request.form['product-brand']
            p.model = request.form['product-model']
            p.memory_size = request.form['memory-size']
            p.width = int(request.form['width'])
            p.height = int(request.form['height'])
            p.jenkins = node
            p.job_name = '-'.join(['MT', p.brand, p.model, str(p.number)]).replace(' ', '_').replace(':', '_colon_')
            p.updated = datetime.datetime.fromtimestamp(time.time())
            p.connected = True
            # clean old screenshot file
            if p.screen_file:
                fbig, fsmall = file2name(p.screen_file)
                if os.path.exists(fbig):
                    os.unlink(fbig)
                    os.unlink(fsmall)

            models.commit() # update p.id
            p.screen_file = '%d-%d' %(p.id, int(time.time()))

            file = request.files['screenshot']
            filename, filename_small = file2name(p.screen_file)
            file.save(filename)
            try:
                from PIL import Image
                im = Image.open(filename)
                im.thumbnail((100, 30), Image.ANTIALIAS) # max-width:30 max-height:30
                im.save(filename_small)
            except:
                import shutil
                shutil.copyfile(filename, filename_small)
    except Exception as e:
        return flask.jsonify({'status': 1, 'message': 'errmsg:'+str(e)})
    return flask.jsonify({'status': 0, 'message': 'success'})

@bp.route('/update_done', methods=['POST'])
def update_done():
    node_name = request.form['node-name']
    job_template = request.form.get('JOB_TEMPLATE', 'mt-template-4d005f1f9df03107')
    j = gcfg.JENKINS
    with models.db_session:
        node = models.Jenkins.get(name=node_name) or models.Jenkins(name=node_name)
        outdate = datetime.datetime.fromtimestamp(time.time()-60) # 1min agao
        for p in models.select(p for p in models.Phone if p.jenkins == node and p.updated < outdate)[:]:
            print 'done', p.id, p.job_name
            p.connected = False

        # Jenkins enable or disable job
        for p in models.select(p for p in models.Phone):
            if not j.job_exists(p.job_name):
                j.copy_job(job_template, p.job_name)
            print p.job_name, p.connected
            if p.connected:
                j.enable_job(p.job_name)
            else:
                j.disable_job(p.job_name)

    return flask.jsonify({'status': 0, 'message': 'update done'})

@bp.route('/hook/<devno>', methods=['POST'])
def hook_job(devno):
    try:
        data = json.loads(request.data)
    except:
        return flask.jsonify(dict(status=4, message='request body not json'))
    ret = models.add_record(devno, data)
    if not ret:
        return flask.jsonify(dict(status=1, message='add record to db failed, maybe devno(%s) not exists' %(devno)))
    return flask.jsonify(dict(status=0, message='success update dev: %s' %(devno)))

@bp.route('/record/<devno>/<date>', methods=['GET'])
def get_record(devno, date):
    record = models.get_latest_record(devno, date)
    if not record:
        return flask.jsonify(dict(status=1, message='record of dev(%s) not found' %(devno)))
    return flask.jsonify(dict(status=0, message='success', data=record))
