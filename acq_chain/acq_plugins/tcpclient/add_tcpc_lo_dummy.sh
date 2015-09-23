#!/bin/bash
. /opt/pyrame/ports.sh
chkpyr2.py localhost $ACQ_PORT newunit_acq 1 /opt/pyrame/tcpc_acq.so /opt/pyrame/uncap_dummy.so tcpc_ 127.0.0.1 5005 go 
