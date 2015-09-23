#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 4
then
  echo "usage $0 ly_zi_id stream_id sparsing output_type channel"
  exit 1
fi
chkpyr2.py localhost $LY_ZI_PORT get_data_ly_zi "$@"
