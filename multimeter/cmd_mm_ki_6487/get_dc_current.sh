#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1
then
  echo "usage $0 mm_ki_6487_id [range [resolution]]"
  exit 1
fi
chkpyr2.py localhost $MM_KI_6487_PORT get_dc_current_mm_ki_6487 "$@"
