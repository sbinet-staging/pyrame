#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1
then
  echo "usage $0 conf_string"
  exit 1
fi

chkpyr2.py localhost $TCP_PORT init_tcp $@
