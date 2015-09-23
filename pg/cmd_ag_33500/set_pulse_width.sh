#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 3 
then
  echo "usage $0 ag_33500_id pulse_width channel"
  exit 1
fi
chkpyr2.py localhost $AG_33500_PORT set_pulse_width_ag_33500 $@
