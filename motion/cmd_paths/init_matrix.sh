#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 8
then
  echo "usage $0 paths_id volume_id p1d p2d p3d order path_type directions"
  exit 1
fi

chkpyr2.py localhost $PATHS_PORT init_matrix_paths $@
