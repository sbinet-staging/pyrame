#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1
then
  echo "usage $0 th_apt_id"
  exit 1
fi

chkpyr2.py localhost $TH_APT_PORT is_reset_th_apt $@
