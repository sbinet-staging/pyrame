#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 3
then
  echo "usage $0 tcp_id data eot_comma-separated_list"
  exit 1
fi
chkpyr2.py -mo localhost $TCP_PORT wrnrd_bin_until_tcp $@
