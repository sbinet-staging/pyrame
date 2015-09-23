#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1
then
  echo "usage $0 multimeter_id [resolution]"
  exit 1
fi
chkpyr2.py localhost $MULTIMETER_PORT get_period_multimeter "$@"
