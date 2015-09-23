#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 2
then
  echo "usage $0 ki_6487_id voltage"
  exit 1
fi
chkpyr2.py localhost $KI_6487_PORT set_voltage_ki_6487 $@
