#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 2
then
  echo "usage $0 serial_id eot_comma-separated_list"
  exit 1
fi
chkpyr2.py -mo localhost $SERIAL_PORT read_until_serial $@
