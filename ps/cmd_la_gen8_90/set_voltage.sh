#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 2
then
  echo "usage $0 la_gen8_90_id voltage"
  exit 1
fi
chkpyr2.py localhost $LA_GEN8_90_PORT set_voltage_la_gen8_90 $@
