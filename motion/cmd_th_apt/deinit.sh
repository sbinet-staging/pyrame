#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1
then
  echo "usage $0 th_apt_id"
  exit 1
fi

chkpyr2.py localhost $TH_APT_PORT deinit_th_apt $@
