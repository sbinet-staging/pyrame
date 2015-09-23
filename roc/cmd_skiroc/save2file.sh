#!/bin/sh
. /opt/pyrame/ports.sh

if test $# -lt 2
then
  echo "usage : $0 rocid filename"
  exit 1
fi
chkpyr2.py localhost $SKIROC_PORT save2file_skiroc $@
