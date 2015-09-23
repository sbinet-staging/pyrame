#!/bin/bash
. /opt/pyrame/ports.sh
chkpyr2.py localhost $ACQ_PORT newunit_acq 1 /opt/pyrame/noacq_acq.so /opt/pyrame/uncap_dummy.so noacq_ null null null
