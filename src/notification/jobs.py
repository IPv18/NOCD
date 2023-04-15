import threading
import time

from schedule import Scheduler

from notification.topic import send


def start_scheduler():
    scheduler = Scheduler()
    scheduler.every(20).seconds.do(add_random_notification)
    scheduler.run_continuously()


def add_random_notification():
    from random import randint
    send('info', type='random', message=randint(0, 1000))


def run_continuously(self, interval=1):
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):

        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                self.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.setDaemon(True)
    continuous_thread.start()
    return cease_continuous_run


Scheduler.run_continuously = run_continuously
