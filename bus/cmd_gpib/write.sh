#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 2
then
  echo "usage $0 gpib_id data"
  exit 1
fi

chkpyr2.py localhost $GPIB_PORT write_gpib $1 "$2" 
