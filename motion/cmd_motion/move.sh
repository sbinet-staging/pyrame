#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 10
then
  echo "usage $0 motion_id d1 d2 d3 s1 s2 s3 a1 a2 a3 [strategy, [real]]"
  exit 1
fi

chkpyr2.py localhost $MOTION_PORT move_motion $@
