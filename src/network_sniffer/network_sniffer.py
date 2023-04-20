"""
This module provides a packet sniffing tool to monitor network traffic 
and store the information in a CSV file. It also provides a daemon 
to periodically update the buffer used by the `SsHelper` class.

Functions:
    - store_pkt_info: A wrapper function that returns a function 
        to store packet information in a CSV file.
    - sniff_traffic: Function that uses TCPDump to capture network 
        packets and store the packet information in a CSV file.
    - update_ss_buffer_daemon: A daemon that periodically updates 
        the buffer used by the `SsHelper` class.
    - main: The main function that starts the packet sniffing and 
        buffer update threads.

Constants:
    - SS_DAEMON_INTERVAL: The interval at which the buffer used by 
        the `SsHelper` class should be updated.
"""

import csv
import os
import threading
from collections import defaultdict

from utils.ss_helper import SsHelper
from utils.tcpdump_helper import TCPDumpHelper
from utils.utils import get_interfaces

SS_DAEMON_INTERVAL = os.environ.get("UPDATE_INTERVAL", 0.5)

def store_pkt_info(writer):
    '''
    A wrapper function, returns a function that stores packet information in a csv file
    '''
    def extract_pkt_info(pkt_reader):
        '''
            TODO
        '''
        interval_length = 5
        interval = 0
        pkts_on_interval = defaultdict(
            lambda: {"length": 0, "pkt_count": 0}
        )

        for pkt in pkt_reader:
            new_interval = pkt.timestamp // interval_length
            pkt_key = pkt.stream_key()
            if interval == new_interval:
                pkts_on_interval[pkt_key]["length"] += pkt.length
                pkts_on_interval[pkt_key]["pkt_count"] += 1
            else:
                for pkt_key, pkt_sum in pkts_on_interval.items():
                    timestamp = int(interval*interval_length)
                    writer.writerow([
                        timestamp, *pkt_key ,pkt_sum["length"], pkt_sum["pkt_count"]
                    ])
                interval = new_interval
                # Start a new interval
                pkts_on_interval.clear()
                pkts_on_interval[pkt_key]["length"] += pkt.length
                pkts_on_interval[pkt_key]["pkt_count"] += 1

    return extract_pkt_info


def sniff_traffic(interface):
    csv_path = os.path.dirname(__file__) +  f"/data/{interface}.csv" # TODO - Fix path
    if not os.path.exists(csv_path):
        csv_header = [
            "timestamp", "program", "protocol", "direction",
            "ip_src", "port_src", "ip_dest", "port_dest", 
            "length", "pkt_count"
        ]
        with open(csv_path, "w", encoding="utf-8") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(csv_header)

    csv_file = open(csv_path, "a", newline='',
                    encoding="utf-8" ,buffering=1)  # TODO - Fix buffering
    csv_writer = csv.writer(csv_file)

    tcpdump_helper = TCPDumpHelper(
        interface=interface,
        output_handler=store_pkt_info(writer=csv_writer),
        args=["-n", "-tt", "-e", "tcp", "or" ,"udp"]
    )
    tcpdump_helper.start()


def update_ss_buffer_daemon():
    '''
    A daemon that periodically updates the buffer used by the `SsHelper` class.
    '''
    SsHelper.update_buffer()
    threading.Timer(SS_DAEMON_INTERVAL, update_ss_buffer_daemon).start()
    print("Updated buffer")


def main():

    interfaces = get_interfaces()
    
    threads = [
        threading.Thread(target=sniff_traffic, 
                         args=(interface,)) for interface in interfaces] +\
        [threading.Thread(target=update_ss_buffer_daemon)
    ]
        
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
