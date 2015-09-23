#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 2
then
  echo "usage $0 ls_421_id range"
  exit 1
fi

chkpyr2.py localhost $LS_421_PORT measure_ls_421 $@
