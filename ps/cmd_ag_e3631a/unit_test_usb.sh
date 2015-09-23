#!/bin/bash
. /usr/local/bin/unit_test_lib.sh

clean_all
sleep 1s
stdbuf -oL -eL cmdmod /opt/pyrame/cmd_ag_e3631a.xml > ag_e3631a.trace 2>&1 &
stdbuf -oL -eL cmdmod /opt/pyrame/cmd_gpib.xml > gpib.trace 2>&1 &
stdbuf -oL -eL cmdmod /opt/pyrame/cmd_serial.xml > serial.trace 2>&1 &
sleep 1s
exec_n_test ./init.sh "ag_e3631a(bus=gpib(bus=serial(),dst_addr=5))"
id=`cat ent.trace | awk -F= '{ print $3 }'`

exec_n_test ./config.sh $id

exec_n_test ./get_voltage.sh $id 1
v0=`cat ent.trace | awk -F= '{ print $3 }'`
exec_n_test ./set_voltage.sh $id 2.9 1

exec_n_test ./get_voltage.sh $id 1
v=`cat ent.trace | awk -F= '{ print $3 }'`
#check_equal_values $v "2.9"
exec_n_test ./set_voltage.sh $id $v0 1

exec_n_test ./inval.sh $id
exec_n_test ./deinit.sh $id

echo "all test passed"

clean_all

exit 0

