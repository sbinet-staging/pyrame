#!/bin/bash
. /opt/pyrame/ports.sh
chkpyr2.py localhost $ACQ_PORT newunit_acq 1 /opt/pyrame/tcps_acq.so /opt/pyrame/uncap_dummy.so tcps_ 8003 null null
