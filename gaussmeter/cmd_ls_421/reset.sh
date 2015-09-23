#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1
then
  echo "usage $0 ls_421_id"
  exit 1
fi

chkpyr2.py localhost $LS_421_PORT reset_ls_421 $@
