#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 2
then
  echo "usage $0 ag_n6700b_id channel"
  exit 1
fi
chkpyr2.py localhost $AG_N6700B_PORT get_voltage_ag_n6700b $@
