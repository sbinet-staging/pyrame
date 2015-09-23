#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1
then
  echo "usage $0 ag_33200_id"
  exit 1
fi
chkpyr2.py localhost $AG_33200_PORT get_frequency_ag_33200 $@
