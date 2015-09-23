#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1
then
  echo "usage $0 ps_id [channel]"
  exit 1
fi
chkpyr2.py localhost $PS_PORT get_current_ps $@
