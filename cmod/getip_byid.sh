#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1
then
  echo "usage $0 name"
  exit 1
fi
chkpyr2.py localhost $CMOD_PORT get_ip_byid_cmod $@
