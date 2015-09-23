#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1
then
  echo "usage $0 la_gen8_90_id"
  exit 1
fi
chkpyr2.py localhost $LA_GEN8_90_PORT power_on_la_gen8_90 $@
