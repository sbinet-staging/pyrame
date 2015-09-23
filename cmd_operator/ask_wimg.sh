#!/bin/sh
. /opt/pyrame/ports.sh
if test $# != 2
then
    echo "usage $0 message image"
    exit 1
fi
chkpyr2.py localhost $OPERATOR_PORT ask_wimg_operator "$1" "$2" 

