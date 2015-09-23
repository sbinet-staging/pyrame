#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 3
then
  echo "usage $0 ha_hmp4030_id current channel"
  exit 1
fi
chkpyr2.py localhost $HA_HMP4030_PORT set_current_ha_hmp4030 $@
