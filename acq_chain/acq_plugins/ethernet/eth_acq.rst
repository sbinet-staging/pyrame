===============================
The ethernet acquisition plugin
===============================

This plugins opens a raw socket and get every packets from it.
This means that : 

- it gets all the packets, including signalizing and other non data thing that have to be correctly handled by the uncap plugin.
- it gets packets directly from the hardware and thus can loose some packet in case of bad schedule. In order to avoid such loss, one should use the max number of RX buffers available (you can fix that with ethtool)
- this plugin is only compatible with Linux.

It takes only one parameter : the interface on which it should listen.
