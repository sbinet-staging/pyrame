#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 2 
then
  echo "usage $0 ag_33200_id duty_cycle"
  exit 1
fi
chkpyr2.py localhost $AG_33200_PORT set_duty_cycle_ag_33200 $@
