#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1
then
  echo "usage $0 nw_esp301_id"
  exit 1
fi
chkpyr2.py localhost $NW_ESP301_PORT inval_nw_esp301 $@
