#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 8
then
  echo "usage $0 sigpulse_id hl ll freq pw re fe phase"
  exit 1
fi

chkpyr2.py localhost $SIGPULSE_PORT config_sigpulse $@
