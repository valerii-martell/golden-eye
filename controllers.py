"""This module contains all app's controllers."""

from datetime import datetime

from flask import render_template, make_response, jsonify, request, redirect, url_for
import xmltodict

from app import app
from models import XRate, ApiLog, ErrorLog, LatestUpdate
import api


class BaseController:
    """The base class of app's controller. All app's controllers have to inherit from it.

    The main purpose of this abstraction is to add API calls logging at higher level of
    abstraction, to avoid code duplication in different controllers. Also, it encapsulates some
    important aliases and methods that are using by more than one controller.

    Attributes:
        aliases_map (dict): a collection that provide converting from codes to text names of currencies on the frontend
        sources_map (dict): a collection that provide converting from API handlers module names to their direct links

    """
    aliases_map = {1000: ("BTC", "Bitcoin"),
                   643: ("RUB", "Russian Ruble"),
                   980: ("UAH", "Ukrainian Hryvnia"),
                   840: ("USD", "United States Dollar")}

    sources_map = {"cbr_api": "https://cbr.ru/development/sxml/",
                   "privat_api": "https://api.privatbank.ua/",
                   "coinmarketcap_api": "https://coinmarketcap.com/api",
                   "blockchaininfo_api": "https://www.blockchain.com/api"}

    def __init__(self):
        self.request = request

    def call(self, *args, **kwds):
        try:
            app.logger.info(f"Started {self.__class__.__name__}")
            # Actual logic, this method will be found in particular derived class-controller
            return self._call(*args, **kwds)
        except Exception as ex:
            app.logger.exception("Error: %s" % ex)
            # Return internal server error message if controller's call was unsuccessful
            return make_response(str(ex), 500)

    def _call(self, *args, **kwds):
        """An abstract method that must contain controller's particular logic realized in derived class"""
        raise NotImplementedError("_call")

    def _minutes_past_last_update(self):
        """Utility method that allows us to get the number of seconds past the latest updating of any rate

        Returns:
            float: The total number of seconds past the latest update, rounded to two digits after the point

        """
        latest_update = LatestUpdate.get(id=1).datetime
        return round((datetime.now() - latest_update).total_seconds() / 60, 2)


class ViewMainPage(BaseController):
    """The Main page controller.

    Provides the main page rendering from a template.

    """

    def _call(self):
        return render_template("index.html", title="Golden Eye", minutes=self._minutes_past_last_update())


class ViewAllRates(BaseController):
    """The exchange rates page controller.

    Provides rendering the page that contains all currencies rates combinations in the DB.

    """

    def _call(self):
        xrates = XRate.select()
        return render_template("xrates.html", xrates=xrates, title="Rates", aliases_map=self.aliases_map,
                               sources_map=self.sources_map, minutes=self._minutes_past_last_update())


class GetApiRates(BaseController):
    """The exchange rates page controller.

    Provides rendering the page that contains all currencies rates combinations in the DB.

    """

    def _call(self, fmt):
        if not fmt:
            # Display basic page if user doesn't request specific format
            from_currencies = XRate.select(XRate.from_currency).distinct()
            to_currencies = XRate.select(XRate.to_currency).distinct()

            return render_template("api.html", from_currencies=from_currencies, to_currencies=to_currencies,
                                   title="API", aliases_map=self.aliases_map,
                                   minutes=self._minutes_past_last_update())
        else:
            # Display rate(s) if user requests specific format
            xrates = XRate.select()

            app.logger.info(f"Asked for API in format {fmt}")
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
            {"alias": f'{self.aliases_map[rate.from_currency][0]}-{self.aliases_map[rate.to_currency][0]}',
             "from": rate.from_currency,
             "to": rate.to_currency,
             "rate": rate.rate} for rate in xrates]}}
        return make_response(xmltodict.unparse(d), {'Content-Type': 'text/xml'})

    def _get_json(self, xrates):
        return jsonify([{"alias": f'{self.aliases_map[rate.from_currency][0]}-{self.aliases_map[rate.to_currency][0]}',
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
            app.logger.exception("Error: %s" % "from_currency and to_currency")
            raise ValueError("from_currency and to_currency")
        return redirect(url_for("view_rates"))

    def _update_rate(self, from_currency, to_currency):
        api.update_rate(from_currency, to_currency)

    def _update_all(self):
        xrates = XRate.select()
        for rate in xrates:
            try:
                self._update_rate(rate.from_currency, rate.to_currency)
            except Exception as ex:
                app.logger.exception("Error: %s" % ex)
                print(ex)


class ViewLogs(BaseController):
    def _call(self, logs_type, fmt):
        app.logger.debug("log_type: %s" % logs_type)
        page = int(self.request.args.get("page", 1))
        page = 1 if page == 0 else page

        if page < 0:
            app.logger.exception("Error: %s" % f"Page number must be greater than zero: {logs_type}")
            raise ValueError(f"Page number must be greater than zero: {logs_type}")

        models = {'api': ApiLog, 'errors': ErrorLog}
        if logs_type not in models:
            app.logger.exception("Error: %s" % f"Unknown logs type: {logs_type}")
            raise ValueError(f"Unknown logs type: {logs_type}")

        logs = models[logs_type].select().paginate(page, 10).order_by(models[logs_type].id.desc())
        title = "API logs" if logs_type == "api" else "Error logs"

        if fmt == "json":
            return jsonify([log.json() for log in logs])
        elif fmt == 'html':
            return render_template("logs.html", jsons=jsonify([log.json() for log in logs]), logs_len=len(logs),
                                   title=title, page_number=page, logs_type=logs_type)
        else:
            app.logger.exception("Error: %s" % f"Unknown format: {fmt}")
            raise ValueError(f"Unknown format: {fmt}")


class EditRate(BaseController):
    """Manual rate edit page controller.

    Provides rendering the page that contains a form for manual editing of some particular exchange rate
    and updating exchange rate in the DB if requested rate exists.

    """

    def _call(self, from_currency, to_currency):
        # Handle request of the page with the updating form
        if self.request.method == "GET":
            current_rate = XRate.get(XRate.from_currency == from_currency, XRate.to_currency == to_currency).rate

            if not current_rate:
                app.logger.exception("Error: %s" % "Unknown currencies combination")
                raise Exception("Unknown currencies combination!")

            return render_template("rate_edit.html",
                                   from_currency=from_currency,
                                   to_currency=to_currency,
                                   aliases_map=self.aliases_map,
                                   current_rate=current_rate,
                                   title="Edit rate")

        # POST request - from the form
        if "new_rate" not in request.form:
            app.logger.exception("Error: %s" % "new_rate parameter is required")
            raise Exception("new_rate parameter is required")

        if not request.form["new_rate"]:
            app.logger.exception("Error: %s" % "new_rate must be not empty")
            raise Exception("new_rate must be not empty")

        (XRate.update({XRate.rate: float(request.form["new_rate"]), XRate.updated: datetime.now()})
         .where(XRate.from_currency == from_currency,
                XRate.to_currency == to_currency).execute())

        # print("upd_count", upd_count)
        # After successful editing return the user to the page that contains all exchange rates
        # from where he highly-likely came to editing page
        return redirect(url_for('view_rates'))
