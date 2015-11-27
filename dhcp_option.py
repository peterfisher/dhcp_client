""" Classes representing DHCP options

"""

from struct import pack


class DHCPOption(object):
    format = None
    length = None
    code = None
    value = None

    def get_encoded_option(self):
        return pack(self.format, *self.value)

class MessageTypeOption(DHCPOption):
    """ DHCP Option 53
    """

    format = '!3b'
    code = 53
    length = 1
    type_lookup = {'DHCPDISCOVER': 1,
                   'DHCPOFFER': 2,
                   'DHCPREQUEST': 3,
                   'DHCPDECLINE': 4,
                   'DHCPACK': 5,
                   'DHCPNAK': 6,
                   'DHCPRELEASE': 7,
                   'DHCPINFORM': 8}

    def __init__(self, type):
        try:
            self.value = [self.code, self.length, self.type_lookup[type]]
        except AttributeError:
            raise AttributeError("Unknown DHCP option 53 Message Type: {}".format(type))

class EndOption(DHCPOption):
    """ End Option
    """
    format = '!B'
    code = 255
    value = [code]


class RequestIPOption(DHCPOption):
    """ DHCP Option 50 for requesting specific IP address

    """
    format = '!6B'
    code = 50
    length = 4

    def __init__(self, ip_address):
        self.value = [self.code, self.length]
        self.value.extend(map(int, ip_address.split('.')))


class ServerIdentifierOption(DHCPOption):
    """ DHCP Option 54 - to identify which dhcp server you're responding to
    """

    format = '!6B'
    code = 54
    length = 4

    def __init__(self, server_ident):
        self.value = [self.code, self.length]
        self.value.extend(map(int, server_ident.split('.')))
