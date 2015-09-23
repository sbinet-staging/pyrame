#!/bin/sh
. /opt/pyrame/ports.sh
chkpyr2.py localhost $TCP_PORT expect_tcp $@
