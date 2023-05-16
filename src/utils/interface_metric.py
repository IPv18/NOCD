import os
import pathlib
from django.conf import settings
from time import sleep
import json

headers = ["timestamp", "program", "protocol", "direction",
           "ip_src", "port_src", "ip_dest", "port_dest",
           "length", "pkt_count"]

NEW_DATA_TIMEOUT = 100


def read_last_pkt_batch(interface):
    try:
        file = open(settings.BASE_DIR /
                    "network_sniffer" / "data" /
                    f"{interface}.csv", 'r', encoding='utf-8')
    except FileNotFoundError:
        return json.dumps([])
    last_sent_timestamp = None
    timer = NEW_DATA_TIMEOUT
    while timer:
        last_file_timestamp = next(reversed_lines(file)).split(',')[0]
        # Long polling - wait for new data
        # keep in mind that polling should be less than 100 seconds
        if last_sent_timestamp == last_file_timestamp:
            timer -= 1
            print(interface, "Waiting for new data...", end='\r')
            sleep(0.5)
            continue
        else:
            timer = NEW_DATA_TIMEOUT
            print("New data found!")
            last_sent_timestamp = last_file_timestamp
            # TODO file = open(f"/sys/class/net/{interface}/statistics/tx_packets", 'r')
            records = list()
            for line in reversed_lines(file):
                record = {key: value for key, value in zip(
                    headers,
                    line[:-1].split(','))
                }
                if last_file_timestamp != record['timestamp']:
                    break
                if len(record) == len(headers):
                    records.append(record)

            yield json.dumps(records)


def reversed_lines(file):
    "Generate the lines of file in reverse order."
    part = ''
    for block in reversed_blocks(file):
        for c in reversed(block):
            if c == '\n' and part:
                yield part[::-1]
                part = ''
            part += c
    if part:
        yield part[::-1]


def reversed_blocks(file, blocksize=4096):
    "Generate blocks of file's contents in reverse order."
    file.seek(0, os.SEEK_END)
    here = file.tell()
    while 0 < here:
        delta = min(blocksize, here)
        here -= delta
        file.seek(here, os.SEEK_SET)
        # TODO - Fix this
        # half char can be cut
        yield file.read(delta)


if __name__ == '__main__':
    csv_path = pathlib.Path(__file__).parent.parent.absolute() / "network_sniffer" / "data" / "wlp0s20f3.csv"
    with open(csv_path, 'r') as csv_file:
        print(read_last_pkt_batch(csv_file))
    # read_last_pkt_batch()
