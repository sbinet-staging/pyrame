#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 2
then
  echo "usage $0 rocid channels"
  exit 1
fi
chkpyr2.py localhost $SKIROC_PORT select_leak_chans_skiroc $@
