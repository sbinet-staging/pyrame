#!/bin/bash
. /opt/pyrame/ports.sh
chkpyr2.py localhost $ACQ_PORT newunit_acq 1 /opt/pyrame/tcpc_acq.so /opt/pyrame/uncap_addclock.so tcpc_ 10.220.0.97 8001 go 
