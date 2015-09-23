#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1
then
  echo "usage $0 tcp_id"
  exit 1
fi

chkpyr2.py localhost $TCP_PORT config_tcp $@
