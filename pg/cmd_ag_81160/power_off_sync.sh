#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 2
then
  echo "usage $0 ag_81160_id channel"
  exit 1
fi
chkpyr2.py localhost $AG_81160_PORT power_off_sync_ag_81160 $@
