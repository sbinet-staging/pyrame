#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 2 
then
  echo "usage $0 signal_id frequency"
  exit 1
fi
chkpyr2.py localhost $SIGNAL_PORT set_frequency_signal $@
