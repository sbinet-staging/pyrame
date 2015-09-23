#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 4
then
  echo "usage $0 ly_lt344_id stream_id sparsing channel"
  exit 1
fi
chkpyr2.py localhost $LY_LT344_PORT get_data_ly_lt344 $@
