#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 2
then
  echo "usage $0 tcp_id bytes_to_read [timeout]"
  exit 1
fi
chkpyr2.py -mo localhost $TCP_PORT read_tcp $@
