#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 4
then
  echo "usage $0 ag_81160_id rising_edge falling_edge channel"
  exit 1
fi
chkpyr2.py localhost $AG_81160_PORT set_edges_ag_81160 $@
