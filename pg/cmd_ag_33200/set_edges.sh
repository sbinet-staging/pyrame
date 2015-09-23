#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 3
then
  echo "usage $0 ag_33200_id edge_time"
  exit 1
fi
chkpyr2.py localhost $AG_33200_PORT set_edges_ag_33200 $@
