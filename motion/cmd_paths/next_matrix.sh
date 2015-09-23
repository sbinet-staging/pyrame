#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 7
then
  echo "usage $0 matrix_id s1 s2 s3 a1 a2 a3 [strategy]"
  exit 1
fi

chkpyr2.py localhost $PATHS_PORT next_matrix_paths $@
