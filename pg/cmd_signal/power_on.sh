#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1
then
  echo "usage $0 signal_id"
  exit 1
fi
chkpyr2.py localhost $SIGNAL_PORT power_on_signal $@
