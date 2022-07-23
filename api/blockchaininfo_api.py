from api import _Api


class Api(_Api):

    def __init__(self):
        super().__init__("BlockchainInfoApi")

    def _update_rate(self, xrate):
        rate = self._get_api_rate(xrate.from_currency, xrate.to_currency)
        return rate

    def _get_api_rate(self, from_currency, to_currency):
        aliases_map = {1000: "btc", 643: "rub"}

        if from_currency not in aliases_map:
            raise ValueError(f"Invalid from_currency: {from_currency}")

        if to_currency not in aliases_map:
            raise ValueError(f"Invalid to_currency: {to_currency}")

        response = self._send_request(url='https://blockchain.info/ticker', method="get")
        response_json = response.json()
        self.log.debug("BlockchainInfo response: %s" % response_json)
        rate = self._find_rate(response_json)

        return rate

    def _find_rate(self, response_data):
        if "RUB" not in response_data:
            raise ValueError("Invalid BlockchainInfo response: RUB not set")

        if "sell" not in response_data["RUB"]:
            raise ValueError("Invalid BlockchainInfo response: RUB.sell not set")

        return float(response_data["RUB"]["sell"])
