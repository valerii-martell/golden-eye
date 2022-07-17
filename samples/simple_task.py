from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()


@sched.scheduled_job('interval', minutes=1)
def get_now():
    print(f"Inside function now: {datetime.now()}")


print(f"Before sched started now: {datetime.now()}")
sched.start()
