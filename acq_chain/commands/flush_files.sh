#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1 
then 
echo "usage $0 prefix"
exit 1
fi
chkpyr2.py localhost $ACQ_PORT flush_files_acq $1
