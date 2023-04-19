"""
This module provides functions for obtaining information about the local network interfaces.

Functions:
    - get_interfaces(): Returns a list of the local network interfaces,
        excluding the loopback interface.
    - get_local_ips(): Returns a list of the local IP addresses for
        each network interface, excluding the loopback interface.
    - get_local_macs(): Returns a list of the local MAC addresses for
        each network interface, excluding the loopback interface.
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


def get_local_ips():
    '''
    Returns a list of the local network interfaces, excluding the loopback interface.
    '''
    output = subprocess.check_output(
        ["""ip addr show | awk '/inet / {split($2,a,"/"); print a[1]}'"""],
        shell=True
    )

    local_ips = output.decode("utf-8").split("\n")


    return [
        ip for ip in local_ips if ip
    ]


def get_local_macs():
    '''
    Returns a list of the local network interfaces, excluding the loopback interface.
    '''
    output = subprocess.check_output(
        ["""ip addr show | awk '/ether / {split($2,a,"/"); print a[1]}'"""],
        shell=True
    )

    local_ips = output.decode("utf-8").split("\n")


    return [
        ip for ip in local_ips if ip
    ]


