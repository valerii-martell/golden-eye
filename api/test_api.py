from api import _Api

from config import logging, LOGGER_CONFIG

log = logging.getLogger("TestApi")
fh = logging.FileHandler(LOGGER_CONFIG["file"])
fh.setLevel(LOGGER_CONFIG["level"])
fh.setFormatter(LOGGER_CONFIG["formatter"])
log.addHandler(fh)
log.setLevel(LOGGER_CONFIG["level"])


class Api(_Api):
    def __init__(self):
        super().__init__("TestApi")

    def _update_rate(self, xrate):
        rate = 1.01
        return rate

