#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1
then
  echo "usage $0 matrix_id"
  exit 1
fi

chkpyr2.py localhost $PATHS_PORT deinit_matrix_paths $@
