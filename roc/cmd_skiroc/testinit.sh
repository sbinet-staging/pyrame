#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 2
then
  echo "usage $0 difid name"
  exit 1
fi
chkpyr2.py localhost $SKIROC_PORT init_skiroc $1 $2
