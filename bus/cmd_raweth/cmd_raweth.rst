=================
The raweth module
=================

This is a bus module intended to send raw Ethernet packets.

API
===

.. function:: send_packet_raweth (interface, dst_mac_addr, eth_protocol, data)

    Send *data* by Ethernet with *eth_protocol* protocol through *interface* (e.g.: eth0) to *dst_mac_addr* MAC address.

    *dst_mac_addr* is a colon-separated string of 6 hexadecimal values. For example: FF:FF:FF:FF:FF:FF

    *eth_protocol* is a two-octet parameter specifying either the Ethernet protocol (Ethernet II EtherType field) if the value is >= 1536 or length of data payload if the value is <= 1500. See IEEE 802.3 for details. Its value can be indicated in hexadecimal (with leading 0x), octal (with leading 0) or decimal (without leading zeros) format.

    *data* is a comma-separated string of octets in hexadecimal (with leading 0x), octal (with leading 0) or decimal (without leading zeros) format. For example: "0x45,34,056". data is padded with zeros to the minimum payload size of 46 octets. Pyrame does not enforce a high level limit of data length. It is up to the user to be sure that host, network and destination will accept the frame.
