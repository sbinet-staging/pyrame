#!/bin/sh
if test $# -lt 1 
then
  echo "usage $0 init_filename"
  exit 1
fi

if test ! -f $1
then
  echo "file not found $1"
  exit 1
fi

./calxml deinit $1 calxml_defaults.xml /opt/pyrame/ports.txt
