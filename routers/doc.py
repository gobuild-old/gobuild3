from flask import Blueprint
from flask import request, flash, redirect, url_for, render_template

bp = Blueprint('doc', __name__)

@bp.route('/')
def doc():
    flash('not finished yet')
    return render_template('index.html')
