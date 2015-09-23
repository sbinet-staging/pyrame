#!/bin/bash

cat /opt/pyrame/ports.d/* > /opt/pyrame/ports.txt
rm -f /opt/pyrame/ports.sh
for i in `cat /opt/pyrame/ports.txt`
do
port_name=`echo $i | awk -F= '{ print $1 }'`
port_number=`echo $i | awk -F= '{ print $2 }'`
echo "export $port_name=$port_number" >> /opt/pyrame/ports.sh
done
chmod +x /opt/pyrame/ports.sh
