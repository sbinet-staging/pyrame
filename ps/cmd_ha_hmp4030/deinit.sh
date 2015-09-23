#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1
then
  echo "usage $0 ha_hmp4030_id"
  exit 1
fi
chkpyr2.py localhost $HA_HMP4030_PORT deinit_ha_hmp4030 $@
