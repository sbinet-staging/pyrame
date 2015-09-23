#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 2 
then
  echo "usage $0 ag_33200_id pulse_width"
  exit 1
fi
chkpyr2.py localhost $AG_33200_PORT set_pulse_width_ag_33200 $@
