import threading
import os
import csv
import subprocess
from scapy.all import *
from collections import defaultdict


class SSHelper():
    '''
    iproute2/ss linux command helper class
    '''

    def __init__(self):
        self.table = ""
        self.update_ss_table()

    def update_ss_table(self):
        output = subprocess.check_output(
            ["ss", "-t", "-u", "-a", "-o", "-p", "-n"])
        self.table = output.decode("utf-8")

    def get_ss_table(self):
        return self.table

    def get_app_name(self, ip_src, ip_dest, port_src, port_dest, protocol):
        """Returns the name of the application associated with the given socket."""
        
        for socket in self.table.splitlines():
            if all(
                (
                    field in socket
                    for field in [
                        ip_src,
                        ip_dest,
                        port_src,
                        port_dest,
                        protocol.lower(),
                        "users:",
                    ]
                )
            ):
                return socket.split("users:")[1].split('"')[1]
        return "Unknown"


def store_pkt_info(writer):
    '''
    A wraper function, returns a function that stores packet information in a csv file
    '''
    
    shared_pkt_info = []

    def aggregate_pkts():
        '''
        A generator function that aggregates packets in a x seconds interval 
        and writes the aggregated information to a csv file 
        '''
        
        nonlocal gen
        interval_length = 5
        interval = shared_pkt_info[0] // interval_length
        pkts_on_interval = defaultdict(
            lambda: {"payload_size": 0, "packet_count": 0})
        while True:
            pkt_timestamp, program, ip_src, ip_dest, port_src, port_dest, protocol, payload_size = shared_pkt_info
            new_interval = pkt_timestamp // interval_length
            if new_interval == interval:
                pkt_key = (interval, program, ip_src, ip_dest,
                           port_src, port_dest, protocol)
                pkts_on_interval[pkt_key]["payload_size"] += payload_size
                pkts_on_interval[pkt_key]["packet_count"] += 1
                yield
            else:
                for (interval, program, ip_src, ip_dest, port_src, port_dest, protocol), pkt_info in pkts_on_interval.items():
                    timestamp = int(interval*interval_length)
                    writer.writerow([timestamp, program, ip_src, ip_dest,
                                     port_src, port_dest, protocol, pkt_info["payload_size"], pkt_info["packet_count"]])
                interval = new_interval
                del gen
                gen = aggregate_pkts()
                next(gen)

    def extract_pkt_info(packet):
        '''
        A function for scapy sniffer, extracts packet information and pass it to a aggregator function
        '''
        
        if packet.haslayer(IP):
            nonlocal shared_pkt_info, gen
            timestamp = packet.time
            ip_src = str(packet[IP].src)
            ip_dest = str(packet[IP].dst)
            port_src = str(packet.sport)
            port_dest = str(packet.dport)
            protocol = packet.summary().split(" ")[4]
            sshelper = SSHelper()
            program = sshelper.get_app_name(
                ip_src, ip_dest, port_src, port_dest, protocol)
            payload_size = len(packet.payload)
            shared_pkt_info = [timestamp, program, ip_src, ip_dest,
                               port_src, port_dest, protocol, payload_size]

            next(gen)

        # TODO - Add support for other protocols

    gen = aggregate_pkts()
    return extract_pkt_info


def sniff_traffic(interface):
    csv_path = f"data/{interface}.csv"
    if not os.path.exists(csv_path):
        csv_header = ["timestamp", "program", "ip_src", "ip_dest",
                      "port_src", "port_dest", "protocol", "payload_size", "packet_count"]
        csv_file = open(csv_path, "w")
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(csv_header)

    csv_file = open(csv_path, "a", newline='',
                    buffering=1)  # TODO - Fix buffering
    csv_writer = csv.writer(csv_file)

    sniffer = sniff(iface=interface, prn=store_pkt_info(
        writer=csv_writer, ), store=False)


def main():

    interfaces = get_if_list()
    interfaces.remove("lo")

    threads = [threading.Thread(target=sniff_traffic, args=(
        interface,)) for interface in interfaces]
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
