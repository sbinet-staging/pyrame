#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1
then
  echo "usage $0 ag_81160_id"
  exit 1
fi
chkpyr2.py localhost $AG_81160_PORT deinit_ag_81160 $@
