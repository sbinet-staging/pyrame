#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1
then
  echo "usage $0 ag_e3631a_id"
  exit 1
fi
chkpyr2.py localhost $AG_E3631A_PORT power_on_ag_e3631a $@
