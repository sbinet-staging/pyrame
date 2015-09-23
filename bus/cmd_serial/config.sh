#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1
then
  echo "usage $0 serial_id"
  exit 1
fi

chkpyr2.py localhost $SERIAL_PORT config_serial $@
