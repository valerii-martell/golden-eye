"""This module contains class that handles retrieving exchange rates to UAH (980)
from BTC (1000) using Coinmarketcap API

"""

from api import _Api
from config import KEYS


class Api(_Api):
    """The class that describes data requesting and retrieving from an external data source.

    Attributes:
        __aliases_map (dict): Currency codes and their abbreviations FROM what this handler can convert to UAH.

    """

    __aliases_map = {1000: "btc", 980: "uah"}

    def __init__(self):
        # Initialize corresponding logger using the constructor from the base class
        super().__init__("CoinmarketcapApi")

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

        Returns:
            float: The value of exchange rate retrieved from the external source.

        """

        # Perform the checks to make us sure that we're not trying to use this handler for non-specified currencies
        if from_currency not in self.__aliases_map:
            raise ValueError(f"Invalid from_currency: {from_currency}")

        if to_currency not in self.__aliases_map:
            raise ValueError(f"Invalid to_currency: {to_currency}")

        # Form the URL for the particular resource in Coinmarketcap API
        url_end = f"{self.__aliases_map[to_currency]}"
        api_key = KEYS['coinmarketcap_api']
        url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?" \
              f"CMC_PRO_API_KEY={api_key}&sort=market_cap&start=1&limit=10&cryptocurrency_type=tokens" \
              f"&convert={url_end}"

        # Send request to the external data source using _send_request method from the base class
        response = self._send_request(url=url, method="get")
        response_json = response.json()
        self.log.debug("Coinmarketcap response: %s" % response_json)

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
        if "data" not in response_data:
            raise ValueError("Invalid coinmarketcap response: data not set")

        for token_data in response_data["data"]:
            if token_data["symbol"] == "WBTC":
                return round(float(token_data["quote"]["UAH"]["price"]), 3)

        raise ValueError("Invalid coinmarketcap response: WBTC not set")
