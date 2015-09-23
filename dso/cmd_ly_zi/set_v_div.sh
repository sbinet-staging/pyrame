#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 2
then
  echo "usage $0 ly_zi_id v_div"
  exit 1
fi
chkpyr2.py localhost $LY_ZI_PORT set_v_div_ly_zi "$@"
