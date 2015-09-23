#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1
then
  echo "usage $0 ly_zi_id"
  exit 1
fi
chkpyr2.py localhost $LY_ZI_PORT get_error_queue_ly_zi $@
