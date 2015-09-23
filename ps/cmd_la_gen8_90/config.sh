#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1
then
  echo "usage $0 la_gen8_90_id [error_checking]"
  exit 1
fi
chkpyr2.py localhost $LA_GEN8_90_PORT config_la_gen8_90 $@
