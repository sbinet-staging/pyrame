#!/bin/bash
. /opt/pyrame/ports.sh
chkpyr2.py localhost $ACQ_PORT newunit_acq 1 /opt/pyrame/udp_multiport_acq.so /opt/pyrame/uncap_dummy.so udpmultiport_ 9000:9001 null null
