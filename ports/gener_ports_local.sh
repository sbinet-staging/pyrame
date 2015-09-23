#!/bin/bash

rm -f ports.sh
for i in `cat ports.txt`
do
port_name=`echo $i | awk -F= '{ print $1 }'`
port_number=`echo $i | awk -F= '{ print $2 }'`
echo "export $port_name=$port_number" >> ports.sh
done
chmod +x ports.sh
