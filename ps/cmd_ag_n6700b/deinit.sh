#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1
then
  echo "usage $0 ag_n6700b_id"
  exit 1
fi
chkpyr2.py localhost $AG_N6700B_PORT deinit_ag_n6700b $@
