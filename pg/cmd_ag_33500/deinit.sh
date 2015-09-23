#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1
then
  echo "usage $0 ag_33500_id"
  exit 1
fi
chkpyr2.py localhost $AG_33500_PORT deinit_ag_33500 $@
