#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1
then
  echo "usage $0 pg_id"
  exit 1
fi
chkpyr2.py localhost $SIGNAL_PORT deinit_pg_signal $@
