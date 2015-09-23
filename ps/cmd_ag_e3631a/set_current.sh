#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 3
then
  echo "usage $0 ag_e3631a_id current channel"
  exit 1
fi
chkpyr2.py localhost $AG_E3631A_PORT set_current_ag_e3631a $@
