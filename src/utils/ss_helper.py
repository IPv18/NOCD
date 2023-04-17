import subprocess
from collections import OrderedDict


class SocketInfo():
    '''
    A class that represents information for a network socket
    connection between two hosts and ports on the network
    '''

    __slots__ = ("ip_src", "port_src", "ip_dest", "port_dest", "program", "protocol", "direction")


    def __init__(self, ip_src: str = None, port_src: int = None,
                 ip_dest: str = None, port_dest: int = None,
                 program: str = None, protocol: str = None, direction: str = None) -> None:
        '''
        Initializes a socket info object, all the parameters are optional.
        '''
        self.ip_src = ip_src
        self.port_src = port_src
        self.ip_dest = ip_dest
        self.port_dest = port_dest
        self.program = program
        self.protocol = protocol.lower() if protocol else None
        self.direction = direction


    def __iter__(self) -> iter:
        '''
        Returns an iterator of key value pairs for all the attributes in the socket info objec.
        '''
        return iter({attr: getattr(self, attr) or "Not Set"  for attr in self.__slots__}.items())


    def __eq__(self, other) -> bool:
        '''
        Compares two socket info objects.
        Two socket info objects can be equal even if their ( ip_dest, port_dest, direction ) diffe.
        '''
        return all(
            (getattr(self, attr) == getattr(other, attr)) \
                for attr in ("ip_src", "port_src", "protocol")
        )


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


class SsHelper():
    '''
    A helper class that provides functionality for working with network sockets 
    on Linux using the iproute2/ss command. 
    '''

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
                key = (new_socket.ip_src, new_socket.port_src, new_socket.protocol)
                cls.sockets_buf[key] = new_socket

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


