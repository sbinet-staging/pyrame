#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 4
then
  echo "usage $0 nw_esp301_id displacement velocity acceleration"
  exit 1
fi
chkpyr2.py localhost $NW_ESP301_PORT move_nw_esp301 $@
