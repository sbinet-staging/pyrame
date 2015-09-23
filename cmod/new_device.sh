#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 3
then
  echo "usage $0 type name parent_id"
  exit 1
fi
chkpyr2.py localhost $CMOD_PORT new_device_cmod $@
