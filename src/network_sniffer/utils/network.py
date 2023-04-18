from dataclasses import dataclass


@dataclass(slots=True)
class IPLink:
    '''
    A data class that represents information for an IP network link 
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
