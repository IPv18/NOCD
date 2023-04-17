"""
The `scapy_helper` module provides helper functions for working with the Scapy network tool.

Functions:
- `get_local_macs()`: Returns a list of the local MAC addresses.
- `get_interfaces()`: Returns a list of the local network interfaces, 
                      excluding the loopback interface.

Dependencies:
- `scapy.all`: The Scapy library, which must be installed in order to use this module.
"""


from scapy.all import conf

def get_local_macs():
    '''
    Returns a list of the local MAC addresses.
    '''
    return [iface.mac for iface in conf.ifaces.values()]

def get_interfaces():
    '''
    Returns a list of the local network interfaces, excluding the loopback interface.
    '''
    return [iface.name for iface in conf.ifaces.values()].remove("lo")
