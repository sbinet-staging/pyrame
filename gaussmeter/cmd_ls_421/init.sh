#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1
then
  echo "usage $0 conf_string"
  exit 1
fi

chkpyr2.py localhost $LS_421_PORT init_ls_421 $@
