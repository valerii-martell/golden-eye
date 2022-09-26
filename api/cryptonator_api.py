"""This module contains class that handles retrieving exchange rates
from BTC (1000) to UAH (980), RUB (643) and USD (840) using Cryptonator API

"""

from api import _Api


class Api(_Api):
    """The class that describes data requesting and retrieving from an external data source.

    Attributes:
        __aliases_map (dict): Currency codes and their abbreviations FROM what this handler can convert to UAH.

    """

    __aliases_map = {1000: "btc", 980: "uah", 643: "rub"}

    def __init__(self):
        # Initialize corresponding logger using the constructor from the base class
        super().__init__("CryptonatorApi")

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

        # Form the URL for the particular resource in Cryptonator API
        url_end = f"{self.__aliases_map[from_currency]}-{self.__aliases_map[to_currency]}"
        url = f"https://api.cryptonator.com/api/ticker/{url_end}"
        # The latest internal rules of Cryptonator API restrict from-code requests,
        # so it is needed to simulate from-browser request
        headers = {
            # 'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
            #              'Chrome/51.0.2704.103 Safari/537.36',
            'pragma': 'no-cache',
            'dnt': '1',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.8',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'cache-control': 'no-cache',
            'authority': 'www.appannie.com'
        }
        # Send request to the external data source using _send_request method from the base class
        response = self._send_request(url=url,
                                      method="get",
                                      headers=headers)
        response_json = response.json()
        self.log.debug("Cryptonator response: %s" % response_json)

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
        if "ticker" not in response_data:
            raise ValueError("Invalid cryptonator response: ticker not set")

        if "price" not in response_data["ticker"]:
            raise ValueError("Invalid cryptonator response: ticker.price not set")

        return float(response_data["ticker"]["price"])
