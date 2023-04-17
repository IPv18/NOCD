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
        elif not isinstance(self.output_handler, (type(None), callable)):
            raise TypeError('output_handler must be a callable or None')
        elif not isinstance(self.args, (type(None), list)):
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
            ['tcpdump', '-i', self.interface, " ".join(self.args) if self.args else ""],
            stdout=subprocess.PIPE
        )
        reader = self.process.stdout.readline
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
