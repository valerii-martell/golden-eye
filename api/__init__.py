"""This module contains base class that encapsulates all external APIs processing."""

import traceback
import importlib
import requests

from config import logging, HTTP_TIMEOUT
from models import XRate, peewee_datetime, ApiLog, ErrorLog, LatestUpdate


def update_rate(from_currency, to_currency):
    """The main function (e.g. an entry-point) of this package, for updating any exchange rate in the system.

    The main purpose of this function is to provide a simple and common interface for updating
    an exchange rate between any two currencies in the system. So the user

    The main algorithm:
    1. Receive from the calling code exactly two parameters - the international digital code of the currency
    to be exchanged from and the code of the currency to be exchanged to;
    2. Find the corresponding record in the database, based on the combination of received codes;
    3. Get from the record the name of the module responsible for obtaining this exchange rate;
    4. Import this module dynamically;
    5. Create an instance of the API class implemented in imported module (which encapsulates all
    the auxiliary functions for making a request to the correspondent bank API and response processing);
    6. Call the update_rate method of this class on the instance of this class, the result of which
    will be the update of the exchange rate of the specified currencies in the system.

    Thus, we removed from the calling code the need to know which module to import and manually import each module
    for each combination of currencies (if the system grows further, it will contain hundreds of modules, it will be
    easy to make a mistake and try to update the currencies rate using the wrong module for them) and call on the
    method corresponding to it. Now the system itself is able to determine which module to process the request.

    International digital currency codes are used instead of abbreviations because they are always the same
    in all banks, while abbreviations could be slightly different (for example, RUB or RUR for the Russian ruble)

    Args:
        from_currency (int): the international digital code of the currency to be exchanged from.
        to_currency (int): the international digital code of the currency to be exchanged to.

    """
    # Find corresponding record in the database
    xrate = XRate.select().where(XRate.from_currency == from_currency,
                                 XRate.to_currency == to_currency).first()

    # Get the name of particular handler responsible for processing of rate updating
    # and import this module dynamically
    module = importlib.import_module(f"api.{xrate.module}")

    # Crate an instance of the API class, which has to be realized in the imported module
    # and call the update_rate method of this class with founded database record as a parameter
    module.Api().update_rate(xrate)


class _Api:
    """The base class of an external API processor. All particular API processors have to inherit from it.

    The main purposes of this abstraction are:
    1. Implement an idea similar to the Strategy pattern in the main method of this class (update_rate).
    2. Move all identical actions of API handlers to the base class, avoiding code duplication
    3. Unify logging and move the bulk of it to the base class, thereby again avoiding code duplication.

    """

    def __init__(self, logger_name):
        # Initialize corresponding logger (should be called from derived classes constructors)
        self.log = logging.getLogger("Api")
        self.log.name = logger_name

    def update_rate(self, xrate):
        """This method encapsulates all operations for updating particular exchange rate in the system.

        It describes the algorithm of any API handler and implements almost all the steps.
        Therefore, to add processing of a new data source (f.e. a new API of a bank or cryptocurrency exchange),
        it is enough to create the handler class "API" in the new module that will be responsible for the processing,
        inherit it from the "_API" base class, and implement the method of actual response parsing in it
        (_update_rate). This method has to return exactly one float number - parsed exchange rate.
        And there all derived classes are able to very simply realize parsing in their own particular way.

        The whole process of the exchange rate updating:
        1. The update_rate method calls on the instance of derived class.
        2. It will not be found in derived class, so it will be called from the base class (_API).
        3. Inside the update_rate method will be called the auxiliary method _update_rate.
        4. Inside the _update_rate method in the derived class will be called the auxiliary method _send_request.
        5. It will not be found in derived class, so it will be called from the base class (_API).
        6. Inside the _send_request method will be called the auxiliary method _send.
        7. It will not be found in derived class, so it will be called from the base class (_API).

        Args:
            xrate (XRate): the corresponding DB entity.

        """
        self.log.info("Started update for: %s" % xrate)
        self.log.debug("Rate before: %s", xrate)

        xrate.rate = self._update_rate(xrate)
        time = peewee_datetime.datetime.now()
        xrate.updated = time
        xrate.save()

        latest_update = LatestUpdate.get(id=1)
        latest_update.datetime = time
        latest_update.save()

        self.log.debug("Rate after: %s", xrate)
        self.log.info("Finished update for: %s" % xrate)

    def _update_rate(self, xrate):
        """This abstract method have to be implemented in each derived classes-handlers where it will be
        responsible for directly obtaining the value of the new exchange rate and updating it in the system.

        Args:
            xrate (Xrate): the corresponding DB entity.

        """

        # Pythonic way to describe an abstract method
        raise NotImplementedError("_update_rate")

    def _send_request(self, url, method, data=None, headers=None):
        """This auxiliary method is responsible for creating the request and returning the response.

        It is necessary because it allows to avoid code duplications since in general the requesting
        process is absolutely similar for all data sources as well as it's logging and error processing.

        Args:
            method (str): HTTP method's name.
            url (str): the URL of the particular data source
            headers (int): (optional) http request headers (f.e. some API authentication token)
            data (any): (optional) additional data for the request

        """
        log = ApiLog(request_url=str(url).split('?')[0], request_data=data, request_method=method,
                     request_headers=headers)
        try:
            response = self._send(method=method, url=url, headers=headers, data=data)
            log.response_text = response.text
            return response
        except Exception as ex:
            self.log.exception("Error during request sending")
            log.error = str(ex)
            ErrorLog.create(request_data=data, request_url=str(url).split('?')[0], request_method=method,
                            error=str(ex), traceback=traceback.format_exc(chain=False))
            raise
        finally:
            log.finished = peewee_datetime.datetime.now()
            log.save()

    def _send(self, url, method, data=None, headers=None):
        """This auxiliary method is responsible for actual sending the request.

        It is necessary in order to replace it with a mock in testing, thereby avoiding sending real requests
        to the APIs, which may have limitations or be paid.

        Args:
            method (str): HTTP method's name.
            url (str): the URL of the particular data source
            headers (int): (optional) http request headers (f.e. some API authentication token)
            data (any): (optional) additional data for the request
            timeout (int): (optional) HTTP timeout is taken from the configs, and it can be changed there
            allow_redirection (bool): (optional) allow redirection is better to be true

        """
        return requests.request(method=method, url=url, headers=headers, data=data, timeout=HTTP_TIMEOUT,
                                allow_redirects=True)
