#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1
then
  echo "usage $0 ly_lt344_id"
  exit 1
fi
chkpyr2.py localhost $LY_LT344_PORT deinit_ly_lt344 $@
