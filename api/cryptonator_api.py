from api import _Api


class Api(_Api):

    def __init__(self):
        super().__init__("CryptonatorApi")

    def _update_rate(self, xrate):
        rate = self._get_api_rate(xrate.from_currency, xrate.to_currency)
        return rate

    def _get_api_rate(self, from_currency, to_currency):
        aliases_map = {1000: "btc", 980: "uah", 643: "rub"}

        if from_currency not in aliases_map:
            raise ValueError(f"Invalid from_currency: {from_currency}")

        if to_currency not in aliases_map:
            raise ValueError(f"Invalid to_currency: {to_currency}")

        url_end = f"{aliases_map[from_currency]}-{aliases_map[to_currency]}"
        url = f"https://api.cryptonator.com/api/ticker/{url_end}"
        headers = {
            #'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
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
        response = self._send_request(url=url,
                                      method="get",
                                      headers=headers)
        response_json = response.json()
        self.log.debug("Cryptonator response: %s" % response_json)
        rate = self._find_rate(response_json)

        return rate

    def _find_rate(self, response_data):
        if "ticker" not in response_data:
            raise ValueError(f"Invalid cryptonator response: ticker not set")

        if "price" not in response_data["ticker"]:
            raise ValueError(f"Invalid cryptonator response: ticker.price not set")

        return float(response_data["ticker"]["price"])
