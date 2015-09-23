. /usr/local/bin/unit_test_lib.sh
. /opt/pyrame/ports.sh

clean_all
echo 
echo 
echo "NOACQ ACQ_PLUGIN TESTS"
echo
rm -rf /tmp/noacq_unit_test
mkdir /tmp/noacq_unit_test
stdbuf -oL -eL acq_server > server.trace 2>&1 &
sleep 1s
exec_n_test ./init_ut.sh
exec_n_test ./add_noacq_dummy.sh
nc localhost $STREAMBASE_PORT > socket.trace &
exec_n_test ./startacq.sh
exec_n_test ./inject_data.sh 0 "84,79,84,79"
exec_n_test ./stopacq.sh
exec_n_test ./flush_files.sh test
check_exist_file /tmp/noacq_unit_test/test_noacq_0.raw
check_equal_files /tmp/noacq_unit_test/test_noacq_0.raw raw.ref
check_equal_files socket.trace raw.ref
exec_n_test ./deinit.sh
echo "all test passed"
rm -rf /tmp/noacq_unit_test
clean_all

exit 0
