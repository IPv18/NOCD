"""
A module for working with network sockets on Linux using the iproute2/ss command.

The module provides two classes: SocketInfo, and SsHelper.

SocketInfo: 
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
    - parse_ss_output: Parses the output of the ss command and returns a SocketInfo object.
    - update_buffer: Runs the ss command and updates sockets in buffer or 
      creates a new one if it doesn't exist.
    - update_socket_info: Updates the socket info with the latest info from the system.

Note: The SsHelper methods may require sudo privileges.

Usage:
To use this module, you can import it and create an instance of the SocketInfo class.
You can then use the various methods provided by the SsHelper class
to update the socket info object with the latest information from the system.

Example:

from ss_helper import SocketInfo, SsHelper

# update the sockets buffer
SsHelper.update_buffer()

# create a socket info object
socket_info = SocketInfo(ip_src="127.0.0.1", port_src=8080, protocol="tcp")

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


@dataclass(slots=True)
class SocketInfo:
    '''
    A class that represents information for a network socket
    connection between two hosts and ports on the network
    '''

    ip_src: str = None
    port_src: int = None
    ip_dest: str = None
    port_dest: int = None
    program: str = None
    protocol: str = None
    direction: str = None

    def __post_init__(self):
        self.protocol = self.protocol.lower() if self.protocol else None


    def __iter__(self) -> iter:
        '''
        Returns an iterator of key value pairs for all the attributes in the socket info objec.
        '''

        return iter({attr: getattr(self, attr) for attr in self.__slots__}.items())


    def __eq__(self, other) -> bool:
        '''
        Compares two socket info objects.
        Two socket info objects can be equal even if their ( ip_dest, port_dest, direction ) diffe.
        '''

        if isinstance(other, SocketInfo):
            return all(
                (getattr(self, attr) == getattr(other, attr)) \
                    for attr in ("ip_src", "port_src", "protocol")
            )
        elif isinstance(other, tuple):
            return all(
                (getattr(self, attr) == other[i]) \
                    for i, attr in enumerate(("ip_src", "port_src", "protocol"))
            )
        else:
            return False


    def __hash__(self) -> int:
        '''
        Returns a hash value for the socket info object.
        Two socket info hashes can be equal even if their ( ip_dest, port_dest, direction ) diffe.
        '''

        return hash((self.ip_src, self.port_src, self.protocol))


    def __str__(self) -> str:
        '''
        Returns a pretty string representation of the socket info objec.
        '''

        return \
            f"""
            Program  : {self.program}
            Protocol : {self.protocol}
            Direction: {self.direction}
            IP       : {self.ip_src}:{self.port_src} --> {self.ip_dest}:{self.port_dest}
            """


    def values(self) -> iter:
        '''
        Returns an iterator of the values of the socket info object.
        '''
        return iter(getattr(self, attr) for attr in self.__slots__)



    def update_info(self) -> None:
        '''
        Updates the socket info with the latest info from the syste.
        '''
        SsHelper.update_socket_info(self)


    def copy(self, other) -> None:
        '''
        Copies the attributes of the other socket info object to this socket info object.
        '''

        for attr in self.__slots__:
            setattr(self, attr, getattr(other, attr))


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
            OrderedDict.__setitem__(self, key, value)
            if self._size > 0:
                if len(self) > self._size:
                    self.popitem(False)


    sockets_buf = PacketRingBuf()

    @staticmethod
    def parse_ss_output(line: str)  -> None:
        '''
        Parses the output of the ss command and returns a SocketInfo objec.
        '''
        cols = line.split(" ")
        return SocketInfo(
            ip_src=cols[4].rsplit(":", 1)[0].split("%")[0],
            port_src=cols[4].rsplit(":", 1)[1],
            ip_dest=cols[5].rsplit(":", 1)[0].split("%")[0],
            port_dest=cols[5].rsplit(":", 1)[1],
            protocol=cols[0].lower(),
            program=cols[6].split('"')[1]
            if '"' in cols[6] else "Unknown"
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
    def update_socket_info(cls, socket_info:SocketInfo)  -> bool:
        '''
        Returns the socket that has created the input packet.
        '''

        ip_src = socket_info.ip_src
        port_src = socket_info.port_src
        ip_dest = socket_info.ip_dest
        port_dest = socket_info.port_dest
        protocol = socket_info.protocol

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

        for key in keys_to_check:
            if key in cls.sockets_buf.keys():
                result = cls.sockets_buf[key]
                if ip_src in key or port_src in key:
                    result.direction = "outbound"
                else:
                    result.direction = "inbound"
                # Deep copy the socket info object
                socket_info.copy(result)
                return True

        return False


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
        cls.test_update_socket_info()

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
    def test_update_socket_info() -> None:
        '''
        Tests the update_socket_info method
        '''
        target_socket = next(iter(SsHelper.sockets_buf.keys()))
        result = SocketInfo(
            ip_src=target_socket.ip_src,
            port_src=target_socket.port_src,
            protocol=target_socket.protocol
        )
        SsHelper.update_socket_info(result)
        print(result)
        assert result is not None
        assert result == target_socket
        assert result.ip_dest is not None \
            and result.ip_dest == target_socket.ip_dest
        assert result.port_dest is not None \
            and result.port_dest == target_socket.port_dest
        assert result.program is not None \
            and result.program == target_socket.program
        assert result.direction is not None \
            and result.direction == "outbound"


if __name__ == "__main__":
    SsHelperTest.run()
