import controllers

from app import app
from config import IP_LIST
from functools import wraps
from flask import request, abort, render_template


def check_ip(func):
    @wraps(func)
    def checker(*args, **kwargs):
        if request.remote_addr not in IP_LIST:
            return abort(403)

        return func(*args, **kwargs)

    return checker


@app.route("/")
def main():
    return controllers.ViewMainPage().call()


@app.route("/xrates")
def view_rates():
    return controllers.ViewAllRates().call()


@app.route("/api/xrates/<fmt>")
@app.route("/api")
def api_rates(fmt=None):
    return controllers.GetApiRates().call(fmt)


@app.route("/update/<int:from_currency>/<int:to_currency>")
@app.route("/update/all")
def update_xrates(from_currency=None, to_currency=None):
    return controllers.UpdateRates().call(from_currency, to_currency)

@app.route("/edit/<int:from_currency>/<int:to_currency>", methods=["GET", "POST"])
#@check_ip
def edit_xrate(from_currency, to_currency):
    return controllers.EditRate().call(from_currency, to_currency)

@app.route("/logs/<logs_type>/<fmt>")
def view_logs(logs_type, fmt):
    return controllers.ViewLogs().call(logs_type, fmt)

