""" DHCP Client implementation
"""


from dhcp_option import (MessageTypeOption, RequestIPOption,
                         ServerIdentifierOption)
from dhcp import DHCP

__author__ = 'peter@phyn3t.com'


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





