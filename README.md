# dhcp_client

At my work we have something called 'peer groups' which is a group of people who get together and study a topic. During my networking peer group I developed a simple DHCP client. The reason for developing something which has been implemented many times before was to get a better understanding of DHCP through implementation.

This client is still a work in progress and currently only supports emitting: DHCP Discovers and DHCP Requests.

Support message types:
* DHCPDISCOVER
* DHCPREQUEST

Supported Options:
* Message Type 53
* End 255
* Request IP 50
* Server Identification 54
