""" Represent DHCP packet

"""
import os
import binascii
import socket

from struct import pack

from constants import HEADER_FIELDS
from dhcp_option import EndOption

__author__ = 'peter@phyn3t.com'


class DHCP(object):
    """ DHCP Packet
    """

    STATES = ('INIT', 'SELECTING', 'REQUESTING', 'INIT-REBOOT', 'REBOOTING',
              'BOUND', 'RENEWING', 'REBINDING',)

    SEND_MAP = {'INIT': 'discover_send'}

    def __init__(self, server, port):
        self.data = {k: pack(HEADER_FIELDS[k].fmt, *HEADER_FIELDS[k].default)
                     for k in HEADER_FIELDS}
        self.options = [EndOption()]
        self.state = self.STATES[0]
        self.server = server
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, wait_response=True):
        """ Send DHCP packet over the wire
        """

        try:
            getattr(self, self.SEND_MAP[self.state])(self)
        except AttributeError:
            pass

        encode_string = DHCP.encode_packet(header=self.data,
                                           option=self.options)

        self.sock.sendto(encode_string, (self.server, self.port))

    @staticmethod
    def encode_packet(header, option):
        """ Convert string to bytestring used in UDP packet

            We assume at this point all fields which will be sent are specified
            and of proper size and format.

        """

        encoded_string = str()

        for k in sorted(header.keys(), key=lambda x: HEADER_FIELDS[x].location):
            encoded_string += header[k]

        for dhcp_option in sorted(option, key=lambda x: x.code):
            encoded_string += dhcp_option.get_encoded_option()

        return encoded_string

    def set_generic_field(self, field, value):
        """ Set specified on DHCP packet

        :param field:
        :param value:

        """

        length = HEADER_FIELDS[field].length

        if isinstance(value, str) and len(value) > HEADER_FIELDS[field].length:
            err_msg = "Field {}, with value: {} exceeds byte limit: {}".format(
                field, length, value
            )
            raise ValueError(err_msg)

        value = [value] # TODO: clean this up? Or maybe not
        self.data[field] = pack(HEADER_FIELDS[field].fmt, *value)

    def set_field_chaddr(self, value):
        """ Set the xid dhcp header field
        """
        ident = value.replace(':', '').decode('hex')
        self.set_generic_field('chaddr', value=ident)

    def set_field_xid(self, value):
        """  Set the XID dhcp header field
        """
        if value is None:
            xid = binascii.b2a_hex(os.urandom(4)).decode("hex")
        else:
            xid = value
        self.set_generic_field('xid', xid)

    @staticmethod
    def discover_send(p):
        p.state_next()
        return p

    def state_next(self):
        # TODO: Finish implementing
        try:
            self.state = self.STATES[self.STATES.index(self.state) + 1]
        except IndexError as e:
            e.args = ("You're at last state, you cannot call next!", )
            raise e
