#!/bin/sh
. /opt/pyrame/ports.sh

if test $# -lt 2
then
  echo "usage : $0 rocid {1|2}"
  exit 1
fi
chkpyr2.py localhost $SKIROC_PORT set_end_ro_skiroc $@
