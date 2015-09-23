#!/bin/bash
. /opt/pyrame/ports.sh
chkpyr2.py localhost $ACQ_PORT init_acq "/tmp/file_unit_test" localhost
