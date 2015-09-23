#!/bin/sh
. /opt/pyrame/ports.sh
chkpyr2.py localhost $ACQ_PORT newunit_acq 1 /opt/pyrame/file_acq.so /opt/pyrame/uncap_dummy.so file_ raw.ref null null
