#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1
then
  echo "usage $0 ki_6487_id"
  exit 1
fi
chkpyr2.py localhost $KI_6487_PORT power_off_ki_6487 $@
