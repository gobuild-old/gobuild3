# coding: utf-8
import threading
import time

import flask
import psutil

bp = flask.Blueprint('home', __name__)

@bp.route('/ruok', methods=['GET', 'POST'])
def ruok():
    return 'imok'

cpu_percent = 0.0
def get_system_status():
    global cpu_percent
    while True:
        cpu_percent = psutil.cpu_percent()
        time.sleep(3)

t = threading.Thread(target=get_system_status)
t.daemon = True
t.start()

@bp.route('/')
def home():
    return flask.render_template('index.html', cpu_percent=cpu_percent)
