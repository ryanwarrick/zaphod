import os
import time

from flask import Blueprint, current_app, g, render_template, send_file

bp = Blueprint("home",
               __name__,
               url_prefix="/home",
               template_folder='templates',
               static_folder="static"
               )


@bp.before_app_request
def before_app_request():
    # https://flask.palletsprojects.com/en/2.0.x/api/#flask.Blueprint.before_app_request
    # Like Flask.before_request(). Such a function is executed before each request, even if outside of a blueprint.
    g.start = time.time()


@bp.after_app_request
def after_app_request(response):
    # https://flask.palletsprojects.com/en/2.0.x/api/#flask.Blueprint.after_app_request
    # Like Flask.after_request() but for a blueprint. Such a function is executed after each request, even if outside of the blueprint.
    diff = time.time() - g.start
    diff = round(diff * 1000, 3)  # convert to millisec (rounded to thousands)
    if ((response.response) and
        (200 <= response.status_code < 300) and
            (response.content_type.startswith('text/html'))):
        response.set_data(response.get_data().replace(
            b'__EXECUTION_TIME__', bytes(str(diff), 'utf-8')))
    return response


@bp.route("/")
def home():
    return render_template('home/home.html')
