#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 2
then
  echo "usage $0 ag_e3631a_id channel"
  exit 1
fi
chkpyr2.py localhost $AG_E3631A_PORT get_voltage_ag_e3631a $@
