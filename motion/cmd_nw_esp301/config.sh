#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 3
then
  echo "usage $0 nw_esp301_id max min"
  exit 1
fi
chkpyr2.py localhost $NW_ESP301_PORT config_nw_esp301 $@
