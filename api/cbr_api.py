"""This module contains class that handles retrieving exchange rates
from USD (840) to RUB (643) using Russian Central Bank's API

"""

import xml.etree.ElementTree as ET

from api import _Api


class Api(_Api):
    """The class that describes data requesting and retrieving from an external data source.

    Attributes:
        __aliases_map (dict): Currency codes and their abbreviations FROM what this handler can convert to UAH.

    """

    __aliases_map = {840: "USD"}

    def __init__(self):
        # Initialize corresponding logger using the constructor from the base class
        super().__init__("CbrApi")

    def _update_rate(self, xrate):
        """The main method of this class-handler. It must return the final rate.

        This method will be called from the update_rate method that is described in the base class _API.

        Args:
            xrate (XRate): the corresponding DB entity.

        Returns:
            float: The value of exchange rate retrieved from the external source.

        """
        rate = self._get_cbr_rate(xrate.from_currency)
        return rate

    def _get_cbr_rate(self, from_currency):
        """The auxiliary method that describes the algorithm of the corresponding external data source processing.

        Args:
            from_currency (int): the international digital code of the currency to be exchanged from.

        Returns:
            float: The value of exchange rate retrieved from the external source.

        """

        # Send request to the external data source using _send_request method from the base class
        response = self._send_request(url="http://www.cbr.ru/scripts/XML_daily.asp", method="get")
        self.log.debug("response.encoding: %s" % response.encoding)

        response_text = response.text
        self.log.debug("response.text: %s" % response_text)

        # Parse the response json to find the latest exchange rate value
        rate = self._find_rate(response_text, from_currency)

        return rate

    def _find_rate(self, response_text, from_currency):
        """The auxiliary method that performs the data source's response parsing to find the exchange rate value.

        Args:
            response_data (dict): json-formatted response from the data source
            from_currency (int): the international digital code of the currency to be exchanged from.

        Returns:
            float: The value of exchange rate retrieved from the external source.

        """

        # Perform the check to make us sure that we're not trying to use this handler for non-specified currencies
        if from_currency not in self.__aliases_map:
            raise ValueError(f"Invalid from_currency: {from_currency}")

        # Convert XML text to convenient for processing format
        root = ET.fromstring(response_text)
        valutes = root.findall("Valute")

        # Get corresponding currency abbreviations exchange rate to UAH from what we're interested in during this call.
        currency_cbr_alias = self.__aliases_map[from_currency]

        # Look for the object from the json which contains the corresponding abbreviation like "from currency" value
        for valute in valutes:
            if valute.find('CharCode').text == currency_cbr_alias:
                return float(valute.find("Value").text.replace(",", "."))

        raise ValueError("Invalid Cbr response: %s not found" % from_currency)
