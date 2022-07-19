import api
import config
import os
import logging
from logging.config import dictConfig
from apscheduler.schedulers.blocking import BlockingScheduler
from models import XRate, ApiLog, ErrorLog


sched = BlockingScheduler()
dictConfig(config.LOGGING)
log = logging.getLogger("Tasks")


@sched.scheduled_job('interval', minutes=15)
def update_rates():
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
    log.info("Cleanup started")
    try:
        if os.path.exists("app.log"):
            os.remove("app.log")
            log.info("Logs cleaned")
        else:
            log.exception("Logs file does not exist")
    except Exception as ex:
        log.exception(ex)

    try:
        for m in ApiLog, ErrorLog:
            m.drop_table()
            m.create_table()
            log.info(f"{m.__name__} cleaned")
    except Exception as ex:
        log.exception(ex)

    log.info("Cleanup finished")


def start():
    sched.start()
    log.info("Scheduler started")


if __name__ == '__main__':
    start()
