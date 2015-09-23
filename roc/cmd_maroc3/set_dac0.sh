#!/bin/sh
. /opt/pyrame/ports.sh

if test $# -lt 2
then
  echo "usage : $0 maroc3_id value"
  exit 1
fi
chkpyr2.py localhost $MAROC3_PORT set_dac0_maroc3 $1 $2
