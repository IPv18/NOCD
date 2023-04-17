"""
This module provides a TCPDumpHelper class that makes it easier
to use tcpdump to capture network traffic on a specific interface.
It allows starting and stopping the tcpdump process and provides
a default output handler to print the captured packets.
"""

import subprocess
from dataclasses import dataclass

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
            ['sudo', 'tcpdump', '-i', self.interface, " ".join(self.args) if self.args else ""],
            stdout=subprocess.PIPE
        )
        output = iter(self.process.stdout.readline, b'')
        reader = self.tcpdump_parser(output)
        if self.output_handler:
            self.output_handler(reader)
        else:
            self.default_output_handler(reader)


    def stop(self):
        """
        Terminates the tcpdump process if it is running.
        """

        if self.process:
            self.process.terminate()
            self.process.wait()


    def default_output_handler(self, reader):
        """
        Prints the output of the tcpdump process to the console.
        This method is called by start() method if no output_handler is provided.
        """

        for line in iter(reader, b''):
            print(line.decode('utf-8').rstrip())


    def tcpdump_parser(self, output):
        """
        Parses the output of the tcpdump process and yields the output line by line.
        """

        for line in output:
            line = line.decode('utf-8').rstrip()
            cols = line.split(" ")

            network_proto = cols[1]

            if network_proto != "IP":
                continue

            yield {
                "timestamp" : cols[0],
                # For IP: remove port - e.g. 10.3.141.250.31686
                "ip_src" : ".".join(cols[2].split(".")[:-1]),
                "port_src" : cols[2].split(".")[-1],
                "ip_dest" : ".".join(cols[4].split(".")[:-1]),
                "port_dest" : cols[4].split(".")[-1],
                "protocol" : "TCP"  if cols[5] == "Flags" else "UDP",
                "length" : cols[-1] if cols[5] == "Flags" else cols[-1][1:-1]
            }

