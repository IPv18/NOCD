import os

import threading
import time

from schedule import Scheduler

from notification.topic import send

logs_path = '/var/log/nocd/firewall.log'
log_size = 0


def start_scheduler():
    scheduler = Scheduler()
    scheduler.every(20).seconds.do(add_random_notification)
    global log_size
    log_size = os.path.getsize(logs_path)
    scheduler.every(5).seconds.do(check_firewall_logs)
    scheduler.run_continuously()


def add_random_notification():
    from random import randint
    send('info', type='random', message=randint(0, 1000))


def check_firewall_logs():
    global log_size
    current_size = os.path.getsize(logs_path)

    if current_size > log_size:
        with open(logs_path, 'r') as f:
            f.seek(log_size)
            for line in f:
                send('log', message=line)
        log_size = current_size


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
