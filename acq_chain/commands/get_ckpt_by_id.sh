#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 2
then
echo "usage $0 id1 id2"
exit 1
fi
chkpyr2.py localhost $ACQ_PORT get_cpkt_byid_acq $1 $2 0 0 0
