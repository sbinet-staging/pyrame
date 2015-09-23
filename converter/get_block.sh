#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 2 
then 
echo "usage $0 port blockid"
exit 1
fi
chkpyr2.py localhost $1 get_block $2  
