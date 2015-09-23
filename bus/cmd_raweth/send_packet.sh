#!/bin/sh
. /opt/pyrame/ports.sh
if test $# -lt 4
then
  echo "usage $0 pc_device dest_mac_adr eth_type data"
  exit 1
fi

chkpyr2.py localhost $RAWETH_PORT send_packet_raweth "$1" "$2" "$3" "$4" 
