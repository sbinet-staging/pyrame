#!/bin/sh
. /opt/pyrame/ports.sh

if test $# -lt 2
then
  echo "usage : $0 rocid mode:int/ext"
  exit 1
fi
chkpyr2.py localhost $SKIROC_PORT set_trigmode_skiroc $1 $2
