#!/bin/bash
. /usr/local/bin/unit_test_lib.sh

clean_all
sleep 1s
stdbuf -oL -eL cmdmod /opt/pyrame/cmd_cmod.xml > cmod.trace 2>&1 &
stdbuf -oL -eL cmdmod /opt/pyrame/cmd_sigpulse.xml > sigpulse.trace 2>&1 &
stdbuf -oL -eL cmdmod /opt/pyrame/cmd_signal.xml > signal.trace 2>&1 &
stdbuf -oL -eL cmdmod /opt/pyrame/cmd_ag_33500.xml > ag_33500.trace 2>&1 &
stdbuf -oL -eL cmdmod /opt/pyrame/cmd_gpib.xml > gpib.trace 2>&1 &
stdbuf -oL -eL cmdmod /opt/pyrame/cmd_tcp.xml > tcp.trace 2>&1 &
stdbuf -oL -eL cmdmod /opt/pyrame/cmd_serial.xml > serial.trace 2>&1 &
sleep 1s
exec_n_test ./init.sh sigpulse_test 0 "ag_33500(bus=tcp(host=10.220.0.3,port=5025))" 1
id=`cat ent.trace | awk -F= '{ print $3 }'`
exec_n_test ./config.sh $id 4.4 2.02 82.3 3e-3 min min 2

exec_n_test ../cmd_ag_33500/get_frequency.sh 0 1
freq=`cat ent.trace | awk -F= '{ print $3 }'`
check_equal_values $freq "82.3"

exec_n_test ./set_frequency.sh $id 39.3
exec_n_test ../cmd_ag_33500/get_frequency.sh 0 1
freq=`cat ent.trace | awk -F= '{ print $3 }'`
check_equal_values $freq "39.3"

exec_n_test ./inval.sh $id
exec_n_test ./deinit.sh $id

echo "all test passed"

clean_all

exit 0

