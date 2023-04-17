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
