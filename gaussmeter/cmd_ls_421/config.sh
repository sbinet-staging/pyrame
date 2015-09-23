#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 4
then
  echo "usage $0 ls_421_id units mode filter"
  exit 1
fi

chkpyr2.py localhost $LS_421_PORT config_ls_421 $@
