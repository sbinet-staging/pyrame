#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 3
then
  echo "usage $0 th_apt_id pos_max pos_min"
  exit 1
fi

chkpyr2.py localhost $TH_APT_PORT config_th_apt $@
