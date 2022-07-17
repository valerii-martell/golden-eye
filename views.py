
from app import app
import controllers


@app.route("/")
def hello():
    return "Hello everybody!"


@app.route("/xrates")
def view_rates():
    return controllers.ViewAllRates().call()


@app.route("/api/xrates/<fmt>")
def api_rates(fmt):
    return controllers.GetApiRates().call(fmt)


@app.route("/update/<int:from_currency>/<int:to_currency>")
@app.route("/update/all")
def update_xrates(from_currency=None, to_currency=None):
    return controllers.UpdateRates().call(from_currency, to_currency)

@app.route("/edit/<int:from_currency>/<int:to_currency>", methods=["GET", "POST"])
#@check_ip
def edit_xrate(from_currency, to_currency):
    return controllers.EditRate().call(from_currency, to_currency)

@app.route("/<logs_type>/<fmt>")
def view_logs(logs_type, fmt):
    return controllers.ViewLogs().call(logs_type, fmt)
