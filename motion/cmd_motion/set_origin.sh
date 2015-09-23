#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 4
then
  echo "usage $0 motion_id o1 o2 o3"
  exit 1
fi

chkpyr2.py localhost $MOTION_PORT set_origin_motion $@
