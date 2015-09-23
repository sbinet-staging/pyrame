#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 3
then
  echo "usage $0 conf_string1 conf_string2 conf_string3"
  exit 1
fi

chkpyr2.py localhost $MOTION_PORT init_motion $@
