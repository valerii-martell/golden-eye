from api import _Api


class Api(_Api):
    def __init__(self):
        super().__init__("TestApi")

    def _update_rate(self, xrate):
        rate = 1.01
        return rate

