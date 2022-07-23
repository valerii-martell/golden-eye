from api import _Api
from config import KEYS


class Api(_Api):

    def __init__(self):
        super().__init__("CoinmarketcapApi")

    def _update_rate(self, xrate):
        rate = self._get_api_rate(xrate.from_currency, xrate.to_currency)
        return rate

    def _get_api_rate(self, from_currency, to_currency):
        aliases_map = {1000: "btc", 980: "uah"}

        if from_currency not in aliases_map:
            raise ValueError(f"Invalid from_currency: {from_currency}")

        if to_currency not in aliases_map:
            raise ValueError(f"Invalid to_currency: {to_currency}")

        url_end = f"{aliases_map[to_currency]}"
        api_key = KEYS['coinmarketcap_api']
        url = f"https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?" \
              f"CMC_PRO_API_KEY={api_key}&sort=market_cap&start=1&limit=10&cryptocurrency_type=tokens" \
              f"&convert={url_end}"

        response = self._send_request(url=url, method="get")
        response_json = response.json()
        self.log.debug("Coinmarketcap response: %s" % response_json)
        rate = self._find_rate(response_json)

        return rate

    def _find_rate(self, response_data):
        if "data" not in response_data:
            raise ValueError("Invalid coinmarketcap response: data not set")

        for token_data in response_data["data"]:
            if token_data["symbol"] == "WBTC":
                return round(float(token_data["quote"]["UAH"]["price"]), 3)

        raise ValueError("Invalid coinmarketcap response: WBTC not set")
