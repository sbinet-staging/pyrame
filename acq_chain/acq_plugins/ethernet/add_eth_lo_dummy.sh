#!/bin/bash
. /opt/pyrame/ports.sh
chkpyr2.py localhost $ACQ_PORT newunit_acq 1 eth_acq.so /opt/pyrame/uncap_dummy.so lodummy lo null null
