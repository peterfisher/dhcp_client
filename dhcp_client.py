""" DHCP Client implementation
"""

import os
import binascii
import socket
from constants import (HEADER_FIELDS, MessageTypeOption, EndOption,
                       RequestIPOption, ServerIdentifierOption)
from struct import pack


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


class DHCPClient(object):
    def __init__(self, server, port=67):
        self.packets = list()
        self.server = server
        self.port = port

    def set_server(self, server):
        self.server = server

    def set_port(self, port):
        self.port = port

    def discover_emit(self, ident=None, xid=None):
        """ Send a DHCP Discover but dont listen for a response

        :param ident: Layer 2 address, default local active interface
        :param xid: random transaction identifier

        :return: DHCP discover response from server

        """

        if ident is None:
            # TODO: add support for local mac address
            raise NotImplementedError("Cannot determine local active interface")

        discover = DHCP(server=self.server, port=self.port)

        # Set all the required fields for a DHCP discover packet
        discover.set_field_chaddr(ident)
        discover.set_field_xid(xid)
        discover.set_generic_field('op', value=1)
        discover.set_generic_field('hlen', value=6)
        discover.set_generic_field('htype', value=1)
        discover.options.append(MessageTypeOption(type='DHCPDISCOVER'))

        discover.send(wait_response=False)

        return discover

    def request_emit(self, ip_address, server_ident, ident=None, xid=None):
        """ Send a DHCP Request but dont listen for a response

        """

        if ident is None:
            # TODO: add support for local mac address
            raise NotImplementedError("Cannot determine local active interface")

        request = DHCP(server=self.server, port=self.port)

        # Set all the required fields for DHCP request packet
        request.set_field_chaddr(ident)
        request.set_field_xid(xid)
        request.set_generic_field('op', value=1)
        request.set_generic_field('hlen', value=6)
        request.set_generic_field('htype', value=1)
        request.options.append(MessageTypeOption(type='DHCPREQUEST'))
        request.options.append(RequestIPOption(ip_address))
        request.options.append(ServerIdentifierOption(server_ident))

        request.send(wait_response=False)

        return request





