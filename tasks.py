"""This module contains all scheduled tasks that is necessary for the app."""

import api
import config
import os
import logging
from logging.config import dictConfig
from apscheduler.schedulers.blocking import BlockingScheduler
from models import XRate, ApiLog, ErrorLog


# Initialize a scheduler
sched = BlockingScheduler()
dictConfig(config.LOGGING)
log = logging.getLogger("Tasks")


@sched.scheduled_job('interval', hours=1)
def update_rates():
    """The function for periodic updating all rates in the application."""
    log.info("Job started")
    xrates = XRate.select()
    for rate in xrates:
        try:
            api.update_rate(rate.from_currency, rate.to_currency)
        except Exception as ex:
            log.exception(ex)
    log.info("Job finished")


@sched.scheduled_job('interval', days=7)
def cleanup():
    """The function for periodic erasing all logs."""
    # Erase internal app's logs
    log.info("Cleanup started")
    try:
        if os.path.exists("app.log"):
            os.remove("app.log")
            log.info("Logs cleaned")
        else:
            log.exception("Logs file does not exist")
    except Exception as ex:
        log.exception(ex)

    # Erase logs of calls to external APIs and occurred errors
    try:
        for table_log in ApiLog, ErrorLog:
            table_log.drop_table()
            table_log.create_table()
            log.info(f"{table_log.__name__} cleaned")
    except Exception as ex:
        log.exception(ex)

    log.info("Cleanup finished")


def start():
    """Scheduler entrypoint"""
    sched.start()
    log.info("Scheduler started")


# Start as a module (necessary for manual start)
if __name__ == '__main__':
    start()
