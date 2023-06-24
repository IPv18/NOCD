import os
import re

import threading
import time

from schedule import Scheduler

from notification.topic import send

log_file_path = '/var/log/nocd/firewall.log'
log_folder_path = '/var/log/nocd'
log_size = 0


def init_log_file():
    if not os.path.exists(log_folder_path):
        os.makedirs(log_folder_path)
        
    if not os.path.exists(log_file_path):
        with open(log_file_path, 'w') as f:
            f.write('')


def start_scheduler():
    init_log_file()
    scheduler = Scheduler()
    scheduler.every(20).seconds.do(add_random_notification)
    global log_size
    log_size = os.path.getsize(log_file_path)
    scheduler.every(5).seconds.do(check_firewall_logs)
    scheduler.run_continuously()


def add_random_notification():
    from random import randint
    # send('info', type='random', message=randint(0, 1000))


def format_log_string(log_string):
    log_string = log_string.replace('"', ' ')
    log_string = log_string.replace('[nocd]', '')

    log_string = re.sub(r'^\w+\s+\d+\s+\d+:\d+:\d+\s+', '', log_string)

    log_string = re.sub(r'\[(.*?)\]', r'\1', log_string)

    log_string = log_string.replace(':', ': ')

    log_string = re.sub(r'(\bIN=|\bOUT=|\bSRC=|\bDST=|\bLEN=|\bPROTO=|\bSPT=|\bDPT=|\bWINDOW=)', r'\n\1', log_string)

    log_string = log_string.replace('IN=', 'In: ')
    log_string = log_string.replace('OUT=', 'Out: ')
    log_string = log_string.replace('SRC=', 'Source: ')
    log_string = log_string.replace('DST=', 'Destination: ')
    log_string = log_string.replace('PROTO=', 'Protocol: ')
    log_string = log_string.replace('SPT=', 'Source Port: ')
    log_string = log_string.replace('DPT=', 'Destination Port: ')

    return log_string


def check_firewall_logs():
    global log_size
    current_size = os.path.getsize(log_file_path)

    if current_size > log_size:
        with open(log_file_path, 'r') as f:
            f.seek(log_size)
            for line in f:
                send('log', message=format_log_string(line))
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
