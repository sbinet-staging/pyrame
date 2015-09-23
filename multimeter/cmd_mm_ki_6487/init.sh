#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1
then
  echo "usage $0 conf_string"
  exit 1
fi
chkpyr2.py localhost $MM_KI_6487_PORT init_mm_ki_6487 "$@"
