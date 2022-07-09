import xml.etree.ElementTree as ET

import requests

from models import XRate, peewee_datetime
from config import logging, LOGGER_CONFIG


log = logging.getLogger("CbrApi")
fh = logging.FileHandler(LOGGER_CONFIG["file"])
fh.setLevel(LOGGER_CONFIG["level"])
fh.setFormatter(LOGGER_CONFIG["formatter"])
log.addHandler(fh)
log.setLevel(LOGGER_CONFIG["level"])


def update_xrates(from_currency, to_currency):
    log.info("Started update for: %s=>%s" % (from_currency, to_currency))
    xrate = XRate.select().where(XRate.from_currency == from_currency,
                                 XRate.to_currency == to_currency).first()

    log.debug("rate before: %s", xrate)
    xrate.rate = get_cbr_rate(from_currency)
    xrate.updated = peewee_datetime.datetime.now()
    xrate.save()

    log.debug("rate after: %s", xrate)
    log.info("Finished update for: %s=>%s" % (from_currency, to_currency))


def get_cbr_rate(from_currency):
    response = requests.get("http://www.cbr.ru/scripts/XML_daily.asp")
    log.debug("response.encoding: %s" % response.encoding)
    response_text = response.text
    log.debug("response.text: %s" % response_text)
    usd_rate = find_usd_rate(response_text)

    return usd_rate


def find_usd_rate(response_text):
    root = ET.fromstring(response_text)
    valutes = root.findall("Valute")

    for valute in valutes:
        if valute.find('CharCode').text == "USD":
            return float(valute.find("Value").text.replace(",", "."))

    raise ValueError("Invalid Cbr response: USD not found")