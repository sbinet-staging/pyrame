#!/bin/sh
. /opt/pyrame/ports.sh
if test $# != 1
then
    echo "usage $0 message"
    exit 1
fi
chkpyr2.py localhost $OPERATOR_PORT ask_operator "$1" 

