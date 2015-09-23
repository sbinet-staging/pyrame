. /usr/local/bin/unit_test_lib.sh
. /opt/pyrame/ports.sh

clean_all
echo 
echo 
echo "TCPCLIENT ACQ_PLUGIN TESTS"
echo
rm -rf /tmp/tcpc_unit_test
mkdir /tmp/tcpc_unit_test
stdbuf -oL -eL acq_server 2>&1 > server.trace&
sleep 1s
exec_n_test ./init_ut.sh
exec_n_test ./add_tcpc_lo_dummy.sh
nc localhost $STREAMBASE_PORT > socket.trace &
./tcp_server.py &
exec_n_test ./startacq.sh
exec_n_test ./stopacq.sh
exec_n_test ./flush_files.sh test
check_exist_file /tmp/tcpc_unit_test/test_tcpc_0.raw
check_equal_files /tmp/tcpc_unit_test/test_tcpc_0.raw raw.ref
check_equal_files socket.trace raw.ref
exec_n_test ./deinit.sh
echo "all test passed"
rm -rf /tmp/tcpc_unit_test
clean_all
exit 0
