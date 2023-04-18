# TODO - Add docstrings

import subprocess

from collections import OrderedDict
from utils.utils import get_local_macs
from utils.network import SocketRecord, PacketRecord

LOCAL_MAC_LIST = get_local_macs()


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
