#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 3
then
  echo "usage $0 th_apt_id velocity acceleration"
  exit 1
fi

chkpyr2.py localhost $TH_APT_PORT go_min_th_apt $@
