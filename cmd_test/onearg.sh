#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 1
then
  echo "usage $0 arg1"
  exit 1
fi
chkpyr2.py localhost $TEST_PORT onearg_test "$1" 

