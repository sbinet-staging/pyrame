#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 2
then
  echo "usage $0 paths_id volume_id"
  exit 1
fi

chkpyr2.py localhost $PATHS_PORT add_limits_paths $@
