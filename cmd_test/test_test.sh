#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 2
then
  echo "usage $0 arg1 arg2"
  exit 1
fi
chkpyr2.py localhost $TEST_PORT test_test "$1" "$2"
