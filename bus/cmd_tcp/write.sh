#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 2
then
  echo "usage $0 tcp_id data"
  exit 1
fi
chkpyr2.py localhost $TCP_PORT write_tcp $@
