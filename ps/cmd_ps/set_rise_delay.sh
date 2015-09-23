#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 2
then
  echo "usage $0 ps_id rise_delay channel"
  exit 1
fi
chkpyr2.py localhost $PS_PORT set_rise_delay_ps $@
