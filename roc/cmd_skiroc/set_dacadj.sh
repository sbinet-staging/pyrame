#!/bin/sh
. /opt/pyrame/ports.sh

if test $# -lt 3
then
  echo "usage : $0 rocid channels delay_value"
  exit 1
fi
chkpyr2.py localhost $SKIROC_PORT set_dacadj_chans_skiroc $1 $2 $3
