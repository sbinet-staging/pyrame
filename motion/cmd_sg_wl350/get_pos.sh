#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 2
then
  echo "usage $0 sg_wl350_id units"
  exit 1
fi
chkpyr2.py localhost $SG_WL350_PORT get_pos_sg_wl350 $@
