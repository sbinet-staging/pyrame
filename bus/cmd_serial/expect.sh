#!/bin/sh
. /opt/pyrame/ports.sh
chkpyr2.py localhost $SERIAL_PORT expect_serial $@
