#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 2 
then 
echo "usage $0 streamid data"
exit 1
fi
chkpyr2.py localhost $ACQ_PORT inject_data_acq $1 $2
