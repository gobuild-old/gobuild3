# coding: utf-8
import flask
from flask import request

import qiniu
import qiniu.conf
import qiniu.rs

import gcfg

bp = flask.Blueprint('storage', __name__)

qiniu.conf.ACCESS_KEY = gcfg.qiniu.access_key
qiniu.conf.SECRET_KEY = gcfg.qiniu.secret_key
bucket = gcfg.qiniu.bucket

@bp.route('/apply', methods=['POST'])
def apply():
    if request.form.get('safe_token') != gcfg.safe.token:
        return flask.jsonify(dict(uptoken=None))
    key = request.form.get('key')
    policy = qiniu.rs.PutPolicy(bucket+':'+key)
    uptoken = policy.token()
    return flask.jsonify(dict(
        uptoken=uptoken, bucket=bucket, key=key,
        outlink='http://%s.qiniudn.com/%s'%(bucket, key)
        ))
