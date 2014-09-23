# coding: utf-8

import qiniu.conf
import qiniu.rs

import gcfg

qiniu.conf.ACCESS_KEY = gcfg.qiniu.access_key
qiniu.conf.SECRET_KEY = gcfg.qiniu.secret_key

key = 'hello.txt'
policy = qiniu.rs.PutPolicy(gcfg.qiniu.bucket+":"+key)
uptoken = policy.token()
print uptoken, type(uptoken)

import qiniu.io
import StringIO
import sys

extra = qiniu.io.PutExtra()
#data = StringIO.StringIO("hello!!!")
ret, err = qiniu.io.put_file(uptoken, key, 'out.json', extra)
if err is not None:
    sys.stderr.write('error: %s ' % err)
