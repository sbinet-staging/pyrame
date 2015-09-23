#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1
then
  echo "usage $0 ag_34401a_id [range [resolution]]"
  exit 1
fi
chkpyr2.py localhost $AG_34401A_PORT get_dc_current_ag_34401a "$@"
