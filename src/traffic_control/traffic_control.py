import subprocess as sp
import json 
from pyroute2 import IPRoute
from pyroute2.netlink.exceptions import NetlinkError
from utils.utils import get_interfaces


def format_net_cls(net_cls):
    if "k" in net_cls["burst"]:
        net_cls["burst"] = int(net_cls["burst"].replace("k", "")) * 1000 
    elif "mb" in net_cls["burst"]:
        net_cls["burst"] = int(net_cls["burst"].replace("mb", "")) * 1000000
    # kbit, mbit, gbit to kbyte, mbyte, gbyte
    if "kbit" in net_cls["rate"]:
        net_cls["rate"] = int(net_cls["rate"].replace("kbit", "")) * 128
    elif "mbit" in net_cls["rate"]:
        net_cls["rate"] = int(net_cls["rate"].replace("mbit", "")) * 131072
    elif "gbit" in net_cls["rate"]:
        net_cls["rate"] = int(net_cls["rate"].replace("gbit", "")) * 134217728
    if isinstance(net_cls["prio"], str):
        net_cls["prio"] = int(net_cls["prio"])


# TODO: Add a Config class to encapsulate the config dict.
def pack_config(**kwargs):
    '''
    Returns a tc policy config.
    '''
    return {
        "class": {
            "rate": kwargs.get('rate', None),
            "burst": kwargs.get('burst', None),
            "prio": kwargs.get('prio', None)
        },
        "match": {
            "transport": kwargs.get('transport', None),
            "ip_src": kwargs.get('ip_src', None),
            "ip_dest": kwargs.get('ip_dest', None),
            "sport": kwargs.get('sport', None),
            "dport": kwargs.get('dport', None),
        },
        "interface": kwargs.get('interface', None),
        "direction": kwargs.get('direction', None),
        "programs": kwargs.get('programs', None)
    }


def unpack_config(config):
    '''
    Returns a flat dict with the config for a tc policy.
    '''
    return {
        "rate": config.get('class', {}).get('rate', None),
        "burst": config.get('class', {}).get('burst', None),
        "prio": config.get('class', {}).get('prio', None),
        "interface": config.get('interface', None),
        "direction": config.get('direction', None),
        "programs": config.get('programs', None),
        "transport": config.get('match', {}).get('transport', None),
        "ip_src": config.get('match', {}).get('ip_src', None),
        "ip_dest": config.get('match', {}).get('ip_dest', None),
        "sport": config.get('match', {}).get('sport', None),
        "dport": config.get('match', {}).get('dport', None),
    }


def get_program_pids(program):
    pids = []
    try:
        pids = sp.check_output(
            ["pgrep", "-x", program],
            encoding="utf-8"
        ).split()
    except sp.CalledProcessError as e:
        if e.returncode != 1:
            raise e
    return pids


def try_if_exists(commands):
    '''
    Run commands and and ignore errors if the return code is 2.
    '''
    for command in commands:
        try:
            sp.run(command, shell=True, check=True)
        except sp.CalledProcessError as e:
            if e.returncode != 2:
                print(e)
        except Exception as e:
            raise e


def classify_program(program, qdisc_handle, classid, interface, reverse=False):
    '''
    Mark packets from a program with the specified net_cls qdisc_handle:1

    Note:
        classid - the classid of the net_cls qdisc that will be created -
        on the interface's root qdisc.
    '''
    pids = get_program_pids(program)
    if len(pids) == 0:
        return
    # Get the cgroup of each pid, typically there will be only one cgroup.
    # On a systemd init Linux, every program is in a cgroup named after -
    # the program/ service under the user slice.
    # e.g. 0::/user.slice/user@1000.service/app.slice/chrome.service
    cgroups = set()
    for pid in pids:
        cgroups.add(
            sp.check_output(
                ["cat", f"/proc/{pid}/cgroup"],
                encoding="utf-8"
            ).split(":")[2].strip()
        )

    # Determine the iptables option (delete or append) and the iptables chain
    opt = "-D" if reverse else "-A"
    check_condition = "&&" if reverse else "||"
    chain = f"OUTPUT -o {interface}" if qdisc_handle == "1" \
        else f"INPUT -i {interface}"
    try:
        for cgroup in cgroups:
            rule = f"{chain} -t mangle -m cgroup --path '{cgroup}' \
            -j CLASSIFY --set-class {qdisc_handle}:{classid}"
            sp.run(
                f"sudo iptables -C {rule} \
                    {check_condition} \
                    sudo iptables {opt} {rule} ",
                shell=True, check=True
            )
    except sp.CalledProcessError as e:
        print(e)


def connmark_program(program, tc_id, interface, reverse=False):
    '''
    Mark packets from a program with a iptables CONNMARK
        used with tc-conmark & tc-fwmark
    This mark is set on OUTPUT and used to determine the
        conn of the packet on INPUT.
    (bidirectional)
    Note:
        classid - the classid of the net_cls qdisc that will
            be created on the interface's root qdisc.
    '''
    pids = get_program_pids(program)
    if len(pids) == 0:
        return
    # Get the cgroup of each pid, typically there will be only one cgroup.
    # On a systemd init Linux, every program is in a cgroup named after -
    # the program/ service under the user slice.
    # e.g. 0::/user.slice/user@1000.service/app.slice/chrome.service
    cgroups = set()
    for pid in pids:
        cgroups.add(
            sp.check_output(
                ["cat", f"/proc/{pid}/cgroup"],
                encoding="utf-8"
            ).split(":")[2].strip()
        )

    # Determine the iptables option (delete or append) and the iptables chain
    opt = "-D" if reverse else "-A"
    check_condition = "&&" if reverse else "||"
    chain = f"OUTPUT -o {interface}"
    try:
        for cgroup in cgroups:
            rule = f"{chain} -t mangle -m cgroup --path '{cgroup}' \
            -j MARK  --set-mark 0x{tc_id}"
            # Check if the rule exists first, then append or delete it.
            sp.run(
                f"sudo iptables -C {rule} {check_condition} \
                    sudo iptables {opt} {rule}",
                shell=True, check=True
            )
            sp.run(
                f"sudo iptables {opt} {chain} \
                    -t mangle -j CONNMARK  --save-mark",
                shell=True, check=True)
    except sp.CalledProcessError as e:
        print(e)


def delete_filter(interface, qdisc_handle, classid):
    '''
    Delete a filter from an interface's root qdisc.
    '''
    try_if_exists([
        f"sudo tc filter del dev {interface} prio {int(classid, 16)}"
    ])


def add_net_cls(net_cls, qdisc_handle, classid, interface, reverse=False):
    '''
    Add or update a net_cls on the qdisc with the specified qdisc_handle.
    '''
    ip = IPRoute()
    interface_index = ip.link_lookup(ifname=interface)[0]

    delete_filter(interface, qdisc_handle, classid)
    try:
        # Delete the filter if it already exists
        # redirect_to_class("", qdisc_handle, classid, interface, True)
        # Delete the class if it already exists
        ip.tc(command="del-class", kind="htb",
              index=interface_index,
              handle=f"{qdisc_handle}:{classid}"
              )
    except NetlinkError as netlink_error:
        if netlink_error.code == 2:
            pass
        else:
            raise netlink_error

    if not reverse:
        try:
            # Create a new class under the qdisc
            # with the specified net_cls parameters
            ip.tc(
                command="add-class", kind="htb", index=interface_index,
                handle=f"{qdisc_handle}:{classid}",
                rate=net_cls["rate"], burst=net_cls["burst"],
                prio=net_cls["prio"]
                )
        except NetlinkError as netlink_error:
            if netlink_error.code == 17:
                ip.tc("del-class", kind="htb", index=interface_index,
                      handle=f"{qdisc_handle}:{classid}")
                ip.tc("add-class", kind="htb", index=interface_index,
                      handle=f"{qdisc_handle}:{classid}",
                      rate=net_cls["rate"], burst=net_cls["burst"],
                      prio=net_cls["prio"]
                      )
            else:
                raise netlink_error

    ip.close()


def tc_filter_to_net_cls(_match, qdisc_handle, classid, interface,
                         reverse=False):
    '''
    Redirect packets matching the specified match to the class
        with the specified classid.
    Note: add-filter isn't fully supported by pyroute2 yet, or
        at least I couldn't get it to work ;)
    '''
    try_if_exists([
        f"sudo tc filter del dev {interface} prio {int(classid, 16)}"
        ])

    if not reverse:
        n_transport = 17 if _match["transport"] == "udp" else 6

        ip_src = _match["ip_src"] if _match["ip_src"] else "0.0.0.0/0"
        ip_dest = _match["ip_dest"] if _match["ip_dest"] else "0.0.0.0/0"
        port_src = _match["sport"] if _match["sport"] else "0 0x0000"
        port_dest = _match["dport"] if _match["dport"] else "0 0x0000"

        port_src = port_src if "0x" in port_src else f"{port_src}  0xffff"
        port_dest = port_dest if "0x" in port_dest else f"{port_dest} 0xffff"
        try:
            sp.run(
                f"sudo tc filter add dev {interface} \
                    prio {int(classid, 16)}  \
                    protocol ip u32 \
                    match ip protocol {n_transport} 0xff \
                    match ip src {ip_src} match ip dst {ip_dest} \
                    match ip sport {port_src}  \
                    match ip dport {port_dest} \
                    flowid {qdisc_handle}:{classid}",
                check=True, shell=True
            )
        except sp.CalledProcessError as e:
            print(e)


def tc_filter_policer(tc_id, interface, rate, burst, _match=None,
                      reverse=False):
    """
    Apply policer on the interface's ingress packets with the specified tc_id.
        - tc_id: the connmark id to match and the priority id of the filter.
        - interface: the interface to apply the policer on.
        - rate: the rate of the policer.
        - burst: the burst of the policer.
        - reverse: if True, delete the policer instead of adding it.
    """
    try_if_exists([
        f"sudo tc filter del dev {interface} ingress prio {int(tc_id, 16)}",
        f"sudo tc filter del dev ifb4nocd            prio {int(tc_id, 16)}"
    ])

    if not reverse:

        try:
            # Retrieve CONNMARK value from the interface's ingress packet
            # then redirect them all to the ifb interface
            sp.run(
                    f"sudo tc filter add dev {interface} parent ffff: \
                        protocol all prio {int(tc_id, 16)} \
                        u32 match u32 0 0 flowid 1:1 \
                        action connmark \
                        action mirred egress redirect dev ifb4nocd",
                    check=True, shell=True
            )

        except sp.CalledProcessError as e:
            print(e)

        try:
            if _match:
                n_transport = 17 if _match["transport"] == "udp" else 6

                ip_src = _match["ip_src"] if _match["ip_src"] \
                    else "0.0.0.0/0"
                ip_dest = _match["ip_dest"] if _match["ip_dest"] \
                    else "0.0.0.0/0"
                port_src = _match["sport"] if _match["sport"] \
                    else "0 0x0000"
                port_dest = _match["dport"] if _match["dport"] \
                    else "0 0x0000"

                port_src = port_src if "0x" in port_src \
                    else f"{port_src}  0xffff"
                port_dest = port_dest if "0x" in port_dest \
                    else f"{port_dest} 0xffff"
                sp.run(
                    f"sudo tc filter add dev ifb4nocd parent 1: \
                        prio {int(tc_id, 16)} \
                        protocol ip u32 \
                        match ip protocol {n_transport} 0xff \
                        match ip src {ip_src} \
                        match ip dst {ip_dest} \
                        match ip sport {port_src}  \
                        match ip dport {port_dest} \
                        action police rate {rate} burst {burst} drop \
                        flowid :1",
                    check=True, shell=True
                )
            else:
                # Apply policer on the ifb interface for the given CONNMARK
                sp.run(
                    f"sudo tc filter add dev ifb4nocd parent 1: \
                        protocol ip prio {int(tc_id, 16)} \
                        handle 0x{tc_id} fw \
                        action police rate {rate} burst {burst} drop \
                        flowid :1",
                    check=True, shell=True
                )

        except sp.CalledProcessError as e:
            print(e)


def enable_policy(tc_policy, reverse=False):
    '''
    Enable a traffic control policy on the system.
    '''
    tc_id = hex(tc_policy.id + 1000)[2:]
    # Outbound policies will be shaped on the egress qdisc using net_cls
    if tc_policy.config["direction"] == "outbound":
        # PS: the VerY SmArT pyroute2 tc developers decided to use
        # different unit than the one used by the tc command line tool
        # so we have to convert the rate and burst
        # command line tool unit (bit), pyroute2 uses byte.
        format_net_cls(tc_policy.config["class"])
        qdisc_handle = "1"
        # Create a new class on the interface's root qdisc
        add_net_cls(
            net_cls=tc_policy.config["class"],
            qdisc_handle=qdisc_handle,
            classid=tc_id,
            interface=tc_policy.config["interface"],
            reverse=reverse
        )

        if tc_policy.config.get("programs"):
            for program in json.loads(tc_policy.config["programs"]):
                classify_program(
                    program=program,
                    qdisc_handle=qdisc_handle,
                    classid=tc_id,
                    interface=tc_policy.config["interface"],
                    reverse=reverse
                )
        elif tc_policy.config.get("match"):
            tc_filter_to_net_cls(
                _match=tc_policy.config["match"],
                qdisc_handle=qdisc_handle,
                classid=tc_id,
                interface=tc_policy.config["interface"],
                reverse=reverse
            )

    # Inbound policies will be policed on the ingress qdisc
    else:
        if tc_policy.config.get("programs"):
            for program in json.loads(tc_policy.config["programs"]):
                connmark_program(
                    program=program,
                    tc_id=tc_id,
                    interface=tc_policy.config["interface"],
                    reverse=reverse
                )
            tc_filter_policer(
                tc_id=tc_id,
                interface=tc_policy.config["interface"],
                rate=tc_policy.config["class"]["rate"],
                burst=tc_policy.config["class"]["burst"],
                reverse=reverse
            )
        elif tc_policy.config.get("match"):
            tc_filter_policer(
                tc_id=tc_id,
                interface=tc_policy.config["interface"],
                rate=tc_policy.config["class"]["rate"],
                burst=tc_policy.config["class"]["burst"],
                _match=tc_policy.config["match"],
                reverse=reverse
            )


def disable_policy(tc_policy):
    enable_policy(tc_policy, reverse=True)


def update_tc(tc_policy):
    if tc_policy.enabled:
        enable_policy(tc_policy)
    else:
        disable_policy(tc_policy)


def bootstrap_tc(startup_policies):
    '''
    Register bootstrapped traffic control policies during system startup.
    This includes:
        - Creating egress(root) and ingress qdiscs on all interfaces
        - Applying startup policies
        - Creating ifb4nocd qdisc for inbound policing

    TODO: Move some of this to a separate installation script
    '''
    ip = IPRoute()
    interfaces = get_interfaces()
    # Create root & ingress qdiscs on all interfaces
    for interface in interfaces:
        interface_index = ip.link_lookup(ifname=interface)[0]
        try:
            ip.tc(command="add", kind="htb",
                  index=interface_index, handle="1:")
            ip.tc(command="add", kind="ingress",
                  index=interface_index, handle="ffff:")
        # If the qdiscs already exist, skip...
        except NetlinkError as netlink_error:
            if netlink_error.code != 17:
                raise netlink_error

    # Create ifb4nocd qdisc - used for inbound policing
    try:

        sp.run("sudo modprobe ifb && \
                    sudo ip link add ifb4nocd type ifb &&\
                    sudo ip link set ifb4nocd up", shell=True, check=True)
        ip.tc(command="add", kind="htb", handle="1:",
              index=ip.link_lookup(ifname="ifb4nocd")[0])
    except sp.CalledProcessError as e:
        # if ifb4nocd already exists, skip...
        if e.returncode != 2:
            raise e
    except NetlinkError as netlink_error:
        # If the qdiscs already exist, skip...
        if netlink_error.code != 17:
            raise netlink_error

    # Apply startup policies
    for tc_policy in startup_policies:
        update_tc(tc_policy)


# pylint: disable=pointless-string-statement
"""
sudo iptables -A OUTPUT -t mangle -m cgroup --path '/user.slice/user-1000.slice/user@1000.service/app.slice/app-google\x2dchrome-6f28379714104c16b90afd1fb3f598d0.scope' \
    -j MARK --set-mark 0x01/0xff
sudo iptables -A OUTPUT -t mangle -j CONNMARK  --save-mark
tc filter add dev wlp0s20f3 parent ffff: protocol all prio 10 u32 match u32 0 0 flowid 1:1 \
    action connmark \
    action mirred egress redirect dev ifb0
tc filter add dev ifb0 parent 1: protocol ip prio 20 handle 0x01 fw \
    action drop 


tjson = {
    "class": {
        "rate": "1000kbit",
        "burst": "100024",
        "prio": 1
    },
    "programs": ["chrome"],
    "interface": "wlp0s20f3",
    "direction": "outbound",
    "match": {
        "ip_src": "",
        "ip_dest": "10.3.141.1",
        "transport": "tcp",
        "sport": "",
        "dport": ""
    }
}

"""