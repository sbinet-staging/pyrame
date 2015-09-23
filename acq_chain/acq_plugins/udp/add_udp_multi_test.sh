#!/bin/bash
. /opt/pyrame/ports.sh
chkpyr2.py localhost $ACQ_PORT newunit_acq 1 /opt/pyrame/udp_multiport_acq.so /opt/pyrame/uncap_udptest.so udptest_ $1 null null
