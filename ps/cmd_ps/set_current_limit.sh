#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 2
then
  echo "usage $0 ps_id current_limit [channel]"
  exit 1
fi
chkpyr2.py localhost $PS_PORT set_current_limit_ps $@
