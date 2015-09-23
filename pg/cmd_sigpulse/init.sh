#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 4
then
  echo "usage $0 dev_name parent_device conf_string channel"
  exit 1
fi

chkpyr2.py localhost $SIGPULSE_PORT init_sigpulse $@
