import logging
from logging.config import dictConfig

from apscheduler.schedulers.blocking import BlockingScheduler

import config
from models import XRate
import api

sched = BlockingScheduler()

dictConfig(config.LOGGING)
log = logging.getLogger("Tasks")


@sched.scheduled_job('interval', minutes=10)
def update_rates():
    log.info("Job started")
    xrates = XRate.select()
    for rate in xrates:
        try:
            api.update_rate(rate.from_currency, rate.to_currency)
        except Exception as ex:
            log.exception(ex)
    log.info("Job finished")


sched.start()

log.info("Scheduler started")
