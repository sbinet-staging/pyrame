#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1
then
  echo "usage $0 multimeter_id"
  exit 1
fi
chkpyr2.py localhost $MULTIMETER_PORT deinit_multimeter "$@"
