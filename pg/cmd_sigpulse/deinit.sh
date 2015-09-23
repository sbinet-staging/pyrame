#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 4
then
  echo "usage $0 sigpulse_id"
  exit 1
fi

chkpyr2.py localhost $SIGPULSE_PORT deinit_sigpulse $@
