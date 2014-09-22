# coding: utf-8
import os
import json
import time
import datetime

import jenkins
import flask
from flask import Blueprint
from flask import request, flash, redirect, url_for, render_template

import models
import gcfg

bp = Blueprint('result', __name__)
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__) or '.', 'static/images/screenshot')
SCREENSHOT_DIR = 'static/images/screenshot'
JENKINS_ARGS = ('http://jenkins.mt.nie.netease.com', 'hzsunshx', 'ccyber')

BADGE_SERVICE = 'http://img.shields.io/badge/job-{status}-{color}.svg'
STATUS_MAP = {
        'pending': 'yellow',
        'running': 'blue',
        'success': 'green',
        'failure': 'red',}
for status, color in STATUS_MAP.items():
    STATUS_MAP[status] = BADGE_SERVICE.format(status=status, color=color)

def jenkins_job_status(job_name, build_id):
    ''' @return job status(string) '''
    j = gcfg.JENKINS
    try:
        r = j.get_build_info(job_name, build_id)
    except jenkins.JenkinsException:
        return 'pending'
    return r.get('result', 'pending').lower()

@bp.route('/<test_id>')
def home(test_id):
    trigger_time = '2014/09/01 12:00'
    spend_time = '0s'
    finish_time = '-'
    job_name = 'MT-samsung-GT-I9502-4d005f1f9df03107'
    job_id = 9
    job_status = jenkins_job_status(job_name, job_id)
    job_log_url = gcfgjenkins.host+'/job/%s/%d/console' %(job_name, job_id)
    job_report_url = 'http://jenkins.mt.nie.netease.com/job/%s/%d/HTML_Report/' %(job_name, job_id)
    return render_template('result.html', **{
        'test_id': test_id,
        'trigger_time': trigger_time,
        'spend_time': spend_time,
        'finish_time': finish_time,
        'job_status': job_status,
        'job_status_badge': STATUS_MAP[job_status],
        'job_log_url': job_log_url,
        'job_report_url': job_report_url,
        })
