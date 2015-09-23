#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 2
then
  echo "usage $0 ps_id command"
  exit 1
fi
chkpyr2.py localhost $PS_PORT free_command_ps $1 "$2"
