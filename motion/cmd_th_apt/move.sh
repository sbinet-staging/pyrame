#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 4
then
  echo "usage $0 th_apt_id displacement max_velocity acceleration"
  exit 1
fi

chkpyr2.py localhost $TH_APT_PORT move_th_apt $@
