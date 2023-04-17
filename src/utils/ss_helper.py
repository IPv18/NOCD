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


