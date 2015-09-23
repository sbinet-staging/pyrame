#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1
then
  echo "usage $0 ag_34401a_id [error_check]"
  exit 1
fi
chkpyr2.py localhost $AG_34401A_PORT config_ag_34401a "$@"
