#!/bin/bash
. /opt/pyrame/ports.sh
for i in `seq 5000`
do
    echo $i
    chkpyr2.py localhost $ACQ_PORT init_acq `pwd` localhost
    chkpyr2.py localhost $ACQ_PORT deinit_acq 
done
