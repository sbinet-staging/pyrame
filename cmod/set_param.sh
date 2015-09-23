#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 3
then
  echo "usage $0 id name value"
  exit 1
fi
chkpyr2.py localhost $CMOD_PORT set_param_cmod $@
