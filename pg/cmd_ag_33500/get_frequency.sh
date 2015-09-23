#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 2
then
  echo "usage $0 ag_33500_id channel"
  exit 1
fi
chkpyr2.py localhost $AG_33500_PORT get_frequency_ag_33500 $@
