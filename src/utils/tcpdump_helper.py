"""
This module provides a TCPDumpHelper class that makes it easier
to use tcpdump to capture network traffic on a specific interface.
It allows starting and stopping the tcpdump process and provides
a default output handler to print the captured packets.
"""

import subprocess
from dataclasses import dataclass
from utils.ss_helper import PacketRecord
from utils.utils import get_local_macs
from utils.ss_helper import SsHelper

@dataclass
class TCPDumpHelper:
    """
    The TCPDumpHelper class provides a way to start and stop 
    tcpdump process on a specific network interface. 
    It takes an interface name, an optional output_handler function, 
    a list of additional arguments to tcpdump, and a Popen process object. 
    It validates the input arguments in the constructor and 
    provides a default_output_handler method to print 
    the output of the tcpdump process if no output_handler is provided.
    """

    interface: str
    output_handler: callable = None
    args: list[str] = None
    process: subprocess.Popen = None


    def __post_init__(self):
        """
        Validates the input arguments and raises a TypeError if any of the arguments
        have incorrect types.
        """

        if not isinstance(self.interface, str):
            raise TypeError('interface must be a string')
        elif self.output_handler and not callable(self.output_handler):
            raise TypeError('output_handler must be a callable or None')
        elif self.args and not isinstance(self.args, list):
            raise TypeError('args must be a list or None')
        elif self.args and not all(isinstance(x, str) for x in self.args):
            raise TypeError('args must be a list of strings')


    def start(self):
        """
        Starts the tcpdump process with the given interface and arguments.
        If an output_handler is provided, it is called to process the output of
        the tcpdump process. Otherwise, the default_output_handler method is called.
        """

        self.process = subprocess.Popen(
            # TODO - Fix sudo
            ['sudo', 'tcpdump', '-i', self.interface, *self.args],
            stdout=subprocess.PIPE
        )
        output = iter(self.process.stdout.readline, b'')
        pkt_reader = self.tcpdump_parser(output)
        if self.output_handler:
            self.output_handler(pkt_reader)
        else:
            self.default_output_handler(pkt_reader)


    def stop(self):
        """
        Terminates the tcpdump process if it is running.
        """

        if self.process:
            self.process.terminate()
            self.process.wait()


    def default_output_handler(self, pkt_reader):
        """
        Prints the output of the tcpdump process to the console.
        This method is called by start() method if no output_handler is provided.
        """

        for pkt in pkt_reader:
            print(pkt)


    def tcpdump_parser(self, output):
        """
        Parses the output of the tcpdump process and yields a PacketRecord object
        for each packet captured.
        """

        for line in output:
            line = line.decode('utf-8').rstrip()
            cols = line.split(" ")

            network_proto = cols[5]

            if network_proto == "IPv4" or network_proto == "IPv6":
                if cols[1] not in get_local_macs() and cols[3][:-1] not in get_local_macs():
                    continue
                pkt = PacketRecord(
                    timestamp=int(cols[0].split(".")[0]),
                    mac_src=cols[1],
                    mac_dest=cols[3][:-1],
                    ip_src=".".join(cols[9].split(".")[:-1]),
                    port_src=cols[9].split(".")[-1],
                    ip_dest=".".join(cols[11].split(".")[:-1]),
                    port_dest=cols[11].split(".")[-1][:-1],
                    protocol="udp" if cols[12] == "UDP," else "tcp",
                    length=int(cols[8][:-1]) if "(" not in cols[-1] else int(cols[-1][1:-2])
                )
                SsHelper.update_packet_record(pkt)

                yield pkt