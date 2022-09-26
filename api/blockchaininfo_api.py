"""This module contains class that handles retrieving exchange rates
from BTC (1000) to RUB (643) using Blockchaininfo API

"""

from api import _Api


class Api(_Api):
    """The class that describes data requesting and retrieving from an external data source.

    Attributes:
        __aliases_map (dict): Currency codes and their abbreviations FROM what this handler can convert to UAH.

    """

    __aliases_map = {1000: "btc", 643: "rub"}

    def __init__(self):
        # Initialize corresponding logger using the constructor from the base class
        super().__init__("BlockchainInfoApi")

    def _update_rate(self, xrate):
        """The main method of this class-handler. It must return the final rate.

        This method will be called from the update_rate method that is described in the base class _API.

        Args:
            xrate (XRate): the corresponding DB entity.

        Returns:
            float: The value of exchange rate retrieved from the external source.

        """
        rate = self._get_api_rate(xrate.from_currency, xrate.to_currency)
        return rate

    def _get_api_rate(self, from_currency, to_currency):
        """The auxiliary method that describes the algorithm of the corresponding external data source processing.

        Args:
            from_currency (int): the international digital code of the currency to be exchanged from.
            to_currency (int): the international digital code of the currency to be exchanged to.

        Returns:
            float: The value of exchange rate retrieved from the external source.

        """

        # Perform the checks to make us sure that we're not trying to use this handler for non-specified currencies
        if from_currency not in self.__aliases_map:
            raise ValueError(f"Invalid from_currency: {from_currency}")

        if to_currency not in self.__aliases_map:
            raise ValueError(f"Invalid to_currency: {to_currency}")

        # Send request to the external data source using _send_request method from the base class
        response = self._send_request(url='https://blockchain.info/ticker', method="get")
        response_json = response.json()
        self.log.debug("BlockchainInfo response: %s" % response_json)

        # Parse the response json to find the latest exchange rate value
        rate = self._find_rate(response_json)

        return rate

    def _find_rate(self, response_data):
        """The auxiliary method that performs the data source's response parsing to find the exchange rate value.

        Args:
            response_data (dict): json-formatted response from the data source

        Returns:
            float: The value of exchange rate retrieved from the external source.

        """
        if "RUB" not in response_data:
            raise ValueError("Invalid BlockchainInfo response: RUB not set")

        if "sell" not in response_data["RUB"]:
            raise ValueError("Invalid BlockchainInfo response: RUB.sell not set")

        return float(response_data["RUB"]["sell"])
