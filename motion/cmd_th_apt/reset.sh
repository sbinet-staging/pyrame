#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1
then
  echo "usage $0 th_apt_id [direction, velocity]"
  exit 1
fi

chkpyr2.py localhost $TH_APT_PORT reset_th_apt $@
