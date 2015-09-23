#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 2
then
  echo "usage $0 module function [params...]"
  exit 1
fi

chkpyr2.py localhost $PATHS_PORT init_volume_paths $@
