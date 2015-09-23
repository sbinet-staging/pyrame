. /usr/local/bin/unit_test_lib.sh
. /opt/pyrame/ports.sh

clean_all
echo 
echo 
echo "UDP ACQ_PLUGIN TESTS"
echo
rm -rf /tmp/udp_unit_test
mkdir /tmp/udp_unit_test
stdbuf -oL -eL acq_server > server.trace 2>&1 &
sleep 1s
exec_n_test ./init_ut.sh
exec_n_test ./add_udp_mono_control_test.sh 2057
exec_n_test ./add_udp_mono_control_test.sh 2064
exec_n_test ./add_udp_mono_data_test.sh 2065
nc localhost $((STREAMBASE_PORT+2)) > socket.trace &
exec_n_test ./startacq.sh
exec_n_test ./udp_sender.py 2065 TEST
exec_n_test ./stopacq.sh
exec_n_test ./startacq.sh
exec_n_test ./udp_sender.py 2057 AATEST
exec_n_test ./udp_sender.py 2064 ABTEST
exec_n_test ./stopacq.sh
exec_n_test ./flush_files.sh test
exec_n_test ./getstats.sh
# 16705 is 0x4141 (network order) = (unsigned short)("AA")
# 16706 is 0x4142 (network order) = (unsigned short)("AB")
exec_n_test ./get_ckpt_by_id.sh 0 16705
exec_n_test ./get_ckpt_by_id.sh 1 16706
check_exist_file /tmp/udp_unit_test/test_udpdatatest_2.raw
check_equal_files /tmp/udp_unit_test/test_udpdatatest_2.raw raw.ref
check_equal_files socket.trace raw.ref
exec_n_test ./deinit.sh

exec_n_test ./init_ut.sh
exec_n_test ./add_udp_multi_test.sh 2057:2064:2065
nc localhost $STREAMBASE_PORT > socket.trace &
exec_n_test ./startacq.sh
exec_n_test ./udp_sender.py 2065 TEST
exec_n_test ./udp_sender.py 2057 AATEST
exec_n_test ./udp_sender.py 2064 ABTEST
exec_n_test ./stopacq.sh
exec_n_test ./flush_files.sh test
exec_n_test ./getstats.sh
# 16705 is 0x4141 (network order) = (unsigned short)("AA")
# 16706 is 0x4142 (network order) = (unsigned short)("AB")
exec_n_test ./get_ckpt_by_id.sh 0 16705
exec_n_test ./get_ckpt_by_id.sh 0 16706
check_exist_file /tmp/udp_unit_test/test_udptest_0.raw
check_equal_files /tmp/udp_unit_test/test_udptest_0.raw raw.ref
check_equal_files socket.trace raw.ref
exec_n_test ./deinit.sh
echo "all test passed"
rm -rf /tmp/udp_unit_test

clean_all

exit 0
