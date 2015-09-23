#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 10
then
  echo "usage $0 motion_id max_1 min_1 max_2 min_2 max_3 min_3 d_1 d_2 d_3"
  exit 1
fi

chkpyr2.py localhost $MOTION_PORT config_motion $@
