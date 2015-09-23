#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 2 
then
  echo "usage $0 signal_id pg_id [channel]"
  exit 1
fi
chkpyr2.py localhost $SIGNAL_PORT set_pg_signal $@
