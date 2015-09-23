#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 3
then
  echo "usage $0 ag_33500_id high_level channel"
  exit 1
fi
chkpyr2.py localhost $AG_33500_PORT set_high_level_ag_33500 $@
