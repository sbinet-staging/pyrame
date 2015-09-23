#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1
then
  echo "usage $0 rocid"
  exit 1
fi
chkpyr2.py localhost $SKIROC_PORT dump_sc_skiroc $@
