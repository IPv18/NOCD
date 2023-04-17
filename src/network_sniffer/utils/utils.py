"""
The `scapy_helper` module provides helper functions for working with the Scapy network tool.

Functions:
- `get_interfaces()`: Returns a list of the local network interfaces, 
                      excluding the loopback interface.

Dependencies:
- `scapy.all`: The Scapy library, which must be installed in order to use this module.
"""

import subprocess


def get_interfaces():
    '''
    Returns a list of the local network interfaces, excluding the loopback interface.
    '''

    output = subprocess.check_output(
        ["ip link show | awk -F': ' '{print $2}'"],
        shell=True
    )

    interfaces = output.decode("utf-8").split("\n\n")


    return [
        interface for interface in interfaces if interface and interface != "lo"
    ]
