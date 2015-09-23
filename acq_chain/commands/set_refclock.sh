#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1 
then 
echo "usage $0 prefix"
exit 1
fi
chkpyr2.py localhost $ACQ_PORT set_refclock_acq $1
