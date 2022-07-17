from datetime import datetime

from flask import render_template, make_response, jsonify, request, redirect, url_for
import xmltodict

from models import XRate, ApiLog, ErrorLog
import api

aliases_map = {1000: "BTC", 643: "RUB", 980: "UAH", 840: "USD"}

class BaseController:
    def __init__(self):
        self.request = request

    def call(self, *args, **kwds):
        try:
            return self._call(*args, **kwds)
        except Exception as ex:
            return make_response(str(ex), 500)

    def _call(self, *args, **kwds):
        raise NotImplementedError("_call")


class ViewAllRates(BaseController):
    def _call(self):
        xrates = XRate.select()
        return render_template("xrates.html", xrates=xrates, aliases_map=aliases_map)


class GetApiRates(BaseController):
    def _call(self, fmt):
        xrates = XRate.select()
        xrates = self._filter(xrates)

        if fmt == "json":
            return self._get_json(xrates)
        elif fmt == "xml":
            return self._get_xml(xrates)
        raise ValueError(f"Unknown fmt: {fmt}")

    def _filter(self, xrates):
        args = self.request.args

        if "from_currency" in args:
            xrates = xrates.where(XRate.from_currency == args["from_currency"])

        if "to_currency" in args:
            xrates = xrates.where(XRate.to_currency == args.get("to_currency"))

        return xrates

    def _get_xml(self, xrates):
        d = {"xrates": {"xrate": [
            {"alias": f'{aliases_map[rate.from_currency]}-{aliases_map[rate.to_currency]}',
             "from": rate.from_currency,
             "to": rate.to_currency,
             "rate": rate.rate} for rate in xrates]}}
        return make_response(xmltodict.unparse(d), {'Content-Type': 'text/xml'})

    def _get_json(self, xrates):
        return jsonify([{"alias": f'{aliases_map[rate.from_currency]}-{aliases_map[rate.to_currency]}',
                         "from": rate.from_currency,
                         "to": rate.to_currency,
                         "rate": rate.rate} for rate in xrates])


class UpdateRates(BaseController):
    def _call(self, from_currency, to_currency):
        if not from_currency and not to_currency:
            self._update_all()

        elif from_currency and to_currency:
            self._update_rate(from_currency, to_currency)

        else:
            ValueError("from_currency and to_currency")
        return redirect(url_for("view_rates"))

    def _update_rate(self, from_currency, to_currency):
        api.update_rate(from_currency, to_currency)

    def _update_all(self):
        xrates = XRate.select()
        for rate in xrates:
            try:
                self._update_rate(rate.from_currency, rate.to_currency)
            except Exception as ex:
                print(ex)


class ViewLogs(BaseController):
    def _call(self, logs_type, fmt):
        page = int(self.request.args.get("page", 1))

        models = {'api': ApiLog, 'errors': ErrorLog}
        if logs_type not in models:
            raise ValueError(f"Unknown logs type: {logs_type}")

        logs = models[logs_type].select().paginate(page, 10).order_by(models[logs_type].id.desc())

        if fmt == "json":
            return jsonify([log.json() for log in logs])
        elif fmt == 'html':
            return render_template("logs.html", logs=logs)
        else:
            raise ValueError(f"Unknown format: {fmt}")


class EditRate(BaseController):
    def _call(self, from_currency, to_currency):
        if self.request.method == "GET":
            return render_template("rate_edit.html",
                                   from_currency=from_currency,
                                   to_currency=to_currency,
                                   aliases_map=aliases_map)

        # POST request is got
        print(request.form)
        if "new_rate" not in request.form:
            raise Exception("new_rate parameter is required")

        if not request.form["new_rate"]:
            raise Exception("new_rate must be not empty")

        upd_count = (XRate.update({XRate.rate: float(request.form["new_rate"]), XRate.updated: datetime.now()})
                          .where(XRate.from_currency == from_currency,
                                 XRate.to_currency == to_currency).execute())

        print("upd_count", upd_count)
        return redirect(url_for('view_rates'))

