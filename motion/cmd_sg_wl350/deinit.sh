#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1
then
  echo "usage $0 sg_wl350_id"
  exit 1
fi
chkpyr2.py localhost $SG_WL350_PORT deinit_sg_wl350 $@
