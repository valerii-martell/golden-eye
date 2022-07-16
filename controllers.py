from flask import render_template, make_response, jsonify, request
import xmltodict

from models import XRate


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
        return render_template("xrates.html", xrates=xrates)


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
            {"from": rate.from_currency, "to": rate.to_currency, "rate": rate.rate} for rate in xrates]}}
        return make_response(xmltodict.unparse(d), {'Content-Type': 'text/xml'})

    def _get_json(self, xrates):
        return jsonify([{"from": rate.from_currency, "to": rate.to_currency, "rate": rate.rate} for rate in xrates])