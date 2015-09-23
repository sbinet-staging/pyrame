#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 7
then
  echo "usage $0 motion_id d1 d2 d3 s1 s2 s3 [order]"
  exit 1
fi

chkpyr2.py localhost $MOTION_PORT reset_motion $@
