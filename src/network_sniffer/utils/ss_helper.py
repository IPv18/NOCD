"""
A module for working with network sockets on Linux using the iproute2/ss command.

The module provides two classes: PacketRecord, and SsHelper.

PacketRecord: 
A class that represents information for a network socket connection
between two hosts and ports on the network.
The class has the following attributes:
    - ip_src: str, optional, the source IP of the socket
    - port_src: int, optional, the source port of the socket
    - ip_dest: str, optional, the destination IP of the socket
    - port_dest: int, optional, the destination port of the socket
    - program: str, optional, the name of the program that created the socket
    - protocol: str, optional, the protocol used by the socket (e.g., TCP or UDP)
    - direction: str, optional, the direction of the connection (e.g., incoming or outgoing)

SsHelper: 
A helper class that provides functionality for working with network sockets 
on Linux using the iproute2/ss command. 

it has PacketRingBuf class and object (sockets_buf): 
A ring buffer that stores the last n packet info in a FIFO manner

It has the following methods:
    - parse_ss_output: Parses the output of the ss command and returns a PacketRecord object.
    - update_buffer: Runs the ss command and updates sockets in buffer or 
      creates a new one if it doesn't exist.
    - update_socket_info: Updates the socket info with the latest info from the system.

Note: The SsHelper methods may require sudo privileges.

Usage:
To use this module, you can import it and create an instance of the PacketRecord class.
You can then use the various methods provided by the SsHelper class
to update the socket info object with the latest information from the system.

Example:

from ss_helper import PacketRecord, SsHelper

# update the sockets buffer
SsHelper.update_buffer()

# create a socket info object
socket_info = PacketRecord(ip_src="127.0.0.1", port_src=8080, protocol="tcp")

# update the socket info object with the latest information from the system
socket_info.update_info()

# access the attributes of the socket info object
print(socket_info.direction)

# print the socket info object
print(socket_info)
"""


import subprocess

from collections import OrderedDict
from dataclasses import dataclass
from utils.utils import get_local_macs

LOCAL_MAC_LIST = get_local_macs()


@dataclass(slots=True)
class IPLink:
    '''
    A data class that represents information for a IP network link 
    (regardless connection or connectionless) between two hosts and ports on the network
    '''

    protocol: str = None
    ip_src: str = None
    port_src: int = None
    ip_dest: str = None
    port_dest: int = None


@dataclass(slots=True)
class PacketRecord(IPLink):
    '''
    A class that represents information for a network traffic
    record between two hosts and ports on the network
    '''
    timestamp: int = None
    length: int = None
    mac_src: str = None
    mac_dest: str = None
    direction: str = None
    program: str = None

    def __post_init__(self):
        self.protocol = self.protocol.lower() if self.protocol else None
        self.update_info()


    def __iter__(self) -> iter:
        '''
        Returns an iterator of key value pairs for all the attributes in the record.
        '''

        return iter({attr: getattr(self, attr) for attr in self.__slots__}.items())


    def __str__(self) -> str:
        '''
        Returns a pretty string representation of the record object.
        '''

        return \
            f"""
            Timestamp: {self.timestamp}
            Program  : {self.program}
            Protocol : {self.protocol}
            Direction: {self.direction}
            IP       : { {self.ip_src}:{self.port_src}:<{20} } --> {self.ip_dest}:{self.port_dest}
            MAC      : { self.mac_src:<{20} } --> {self.mac_dest}
            """


    def stream_key(self) -> tuple:
        '''
        Returns a tuple representation of the packet stream key.
        EXECLUDES the timestamp, MACs, and length attributes.
        Can be used for collecting network traffic statistics
        for packets that belong to the same stream.
        '''

        return(
            self.program, self.protocol, self.direction,
            self.ip_src, self.port_src, self.ip_dest, self.port_dest
        )


    def values(self) -> iter:
        '''
        Returns an iterator of the values of the socket info object.
        '''
        return iter(getattr(self, attr) for attr in self.__slots__)



    def update_info(self) -> None:
        '''
        Updates the network traffic record with the latest info from the system.
        '''
        SsHelper.update_packet_record(self)


    def copy(self, other) -> None:
        '''
        Deep copies the attributes of the other record object to this record object.
        '''

        for attr in other.__slots__:
            setattr(self, attr, getattr(other, attr))


@dataclass(slots=True)
class SocketRecord(IPLink):

    program: str = None

    def __eq__(self, other) -> bool:
        '''
        Compares two record objects.
        Two record objects can be equal given their 
        ("ip_src", "port_src", "protocol", "program") are equal.
        '''
        if isinstance(other, SocketRecord):
            # if two records being inserted -or checked- and they have
            # the same ("ip_src", "port_src", "protocol", "program") then
            # this is the same socket and we should update the existing record
            # i.e. Update instead of inserting a new one
            return all(
                (getattr(self, attr) == getattr(other, attr)) \
                    for attr in ("ip_src", "port_src", "protocol", "program")
            )
        if isinstance(other, tuple):
            # This case for indexing by a tuple TODO
            # buffer[("ip_src", "port_src", "protocol")] instead of SocketRecord
            # Used for retrieve or check if tuple exists in the buffer as a key
            return all(
                (getattr(self, attr) == other[i]) \
                    for i, attr in enumerate(("ip_src", "port_src", "protocol"))
            )
        return False


    def __hash__(self) -> int:
        '''
        Returns a hash value for the record object.
        Two record hashes can be equal given their 
        ("ip_src", "port_src", "protocol", "program") are equal.
        '''

        return hash((self.ip_src, self.port_src, self.protocol))


class SsHelper():
    '''
    A helper class that provides functionality for working with network sockets 
    on Linux using the iproute2/ss command. 
    '''

    class PacketRingBuf(OrderedDict):
        '''
        A ring buffer that stores the last n packet info in a FIFO manner
        '''

        def __init__(self, *args, size: int = 1024, **kwargs)  -> None:
            self._size = size
            super().__init__(*args, **kwargs)

        def __setitem__(self, key, value) -> None:
            # del pld item to maintain FIFO order based on update time
            if key in self:
                del self[key]
            OrderedDict.__setitem__(self, key, value)
            if self._size > 0:
                if len(self) > self._size:
                    self.popitem(False)


    sockets_buf = PacketRingBuf()

    @staticmethod
    def parse_ss_output(line: str)  -> None:
        '''
        Parses the output of the ss command and returns a SocketRecord objec.
        '''
        cols = line.split(" ")
        return SocketRecord(
            ip_src=cols[4].rsplit(":", 1)[0].split("%")[0],
            port_src=cols[4].rsplit(":", 1)[1],
            ip_dest=cols[5].rsplit(":", 1)[0].split("%")[0],
            port_dest=cols[5].rsplit(":", 1)[1],
            protocol=cols[0].lower(),
            program=cols[6].split('"')[1]
            if len(cols) > 6 and '"' in cols[6] else ""
        )

    @classmethod
    def update_buffer(cls)  -> None:
        '''
        Runs the ss command and updates sockets in buffer or creates a new one if it doesn't exist.
        '''

        popen_process = subprocess.Popen(
            ["sudo ss -tuopna | sed 's/\s\+/ /g'"],
            stdout=subprocess.PIPE, shell=True)
        # TODO - do we need to use sudo here?
        # TODO - does this support ipv6? test it :)
        try:
            reader = iter(popen_process.stdout.readline, b'')
            # skip the first line
            next(reader)
            for line in reader:
                line = line.decode("utf-8").strip()
                new_socket = cls.parse_ss_output(line)
                cls.sockets_buf[new_socket] = new_socket
        except Exception as ex:
            print(f"Error while updating ss buffer: {ex}")
            # TODO - add logger and log this
            # TODO - add exception handling

    @classmethod
    def update_packet_record(cls, packet_record:PacketRecord)  -> None:
        '''
        Updates the PacketRecord with the SocketRecord info that has created it.
        For now, we only update the dirction and program name.
        '''

        mac_src     = packet_record.mac_src
        mac_dest    = packet_record.mac_dest
        ip_src      = packet_record.ip_src
        port_src    = packet_record.port_src
        ip_dest     = packet_record.ip_dest
        port_dest   = packet_record.port_dest
        protocol    = packet_record.protocol

        if mac_src in LOCAL_MAC_LIST: 
            packet_record.direction = "outbound"
        elif mac_dest in LOCAL_MAC_LIST:
            packet_record.direction = "inbound"
        else:
            packet_record.direction = "captured(promiscuous?)"

        keys_to_check = [
            (ip_src, port_src, protocol),
            (ip_dest, port_dest, protocol),
            (ip_src, "*", protocol),
            (ip_dest, "*", protocol),
            ("0.0.0.0", port_src, protocol),
            ("[::]", port_src, protocol),
            ("0.0.0.0", port_dest, protocol),
            ("[::]", port_dest, protocol),
            ("*", port_src, protocol),
            ("*", port_dest, protocol),
            ("*", "*", protocol),
        ]

        buf = cls.sockets_buf

        for key in keys_to_check:
            if key in buf.keys():
                packet_record.program = buf[key].program # This can be dengerous if there are multiple sockets with the same key
                return


class SsHelperTest():
    '''
    Test class for SsHelper
    '''

    @classmethod
    def run(cls)  -> None:
        '''
        Runs the test
        '''
        cls.test_parse_ss_output()
        cls.test_update_buffer()
        cls.test_update_packet_info()

    @staticmethod
    def test_parse_ss_output()  -> None:
        '''
        Tests the parse_ss_output method
        '''
        line = 'tcp ESTAB 0 0 192.168.1.23:55372 13.227.219.62:443 users:(("chrome",pid=702871,fd=33)) timer:(keepalive,1.010ms,0) '
        try :
            socket_info = SsHelper.parse_ss_output(line)
            assert socket_info.ip_src == "192.168.1.23"
            assert socket_info.port_src == "55372"
            assert socket_info.ip_dest == "13.227.219.62"
            assert socket_info.port_dest == "443"
            assert socket_info.protocol == "tcp"
            assert socket_info.program == "chrome"
        except Exception as ex:
            print(f"Error while testing parse_ss_output: {ex}")


    @staticmethod
    def test_update_buffer() -> None:
        '''
        Tests the update_buffer method
        '''
        SsHelper.update_buffer()
        assert len(SsHelper.sockets_buf.values()) > 0
        first_socket = next(iter(SsHelper.sockets_buf.values()))
        assert first_socket is not None
        assert first_socket.ip_src is not None
        assert first_socket.port_src is not None
        assert first_socket.ip_dest is not None
        assert first_socket.port_dest is not None
        assert first_socket.protocol is not None
        assert first_socket.program is not None


    @staticmethod
    def test_update_packet_info() -> None:
        '''
        Tests the update_socket_info method
        '''
        target_socket = next(iter(SsHelper.sockets_buf.keys()))
        result = PacketRecord(
            ip_src=target_socket.ip_src,
            port_src=target_socket.port_src,
            protocol=target_socket.protocol
        )
        SsHelper.update_packet_record(result)
        print(result)
        assert result is not None
        assert result == target_socket
        assert result.program is not None \
            and result.program == target_socket.program
        assert result.direction is not None \
            and result.direction == "outbound"


if __name__ == "__main__":
    SsHelperTest.run()
