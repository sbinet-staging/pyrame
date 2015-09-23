#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 2
then
  echo "usage $0 type parent_name"
  exit 1
fi
chkpyr2.py localhost $CMOD_PORT get_name_sublist_cmod $@
