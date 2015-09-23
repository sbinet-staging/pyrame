#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1
then
  echo "usage $0 motion_id"
  exit 1
fi

chkpyr2.py localhost $MOTION_PORT inval_motion $@
