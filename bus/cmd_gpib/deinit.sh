#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1
then
  echo "usage $0 gpib_id"
  exit 1
fi

chkpyr2.py localhost $GPIB_PORT deinit_gpib $@
