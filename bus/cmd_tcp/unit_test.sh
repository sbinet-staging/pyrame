. /usr/local/bin/unit_test_lib.sh
. /opt/pyrame/ports.sh

conf_string="tcp(host=localhost,port=38472)"

clean_all
echo
echo
echo "TCP TESTS"
echo
stdbuf -oL -eL cmdmod /opt/pyrame/cmd_tcp.xml > cmd_tcp.trace 2>&1 &
sleep 1s
stdbuf -oL -eL nc -l 38472 > tcp.trace &
exec_n_test ./init.sh $conf_string
exec_n_test ./config.sh 0
exec_n_test ./write.sh 0 TEST
exec_n_test ./write_bin.sh 0 544553540a
check_equal_files tcp.trace raw.ref
exec_n_test ./inval.sh 0
exec_n_test ./deinit.sh 0

stdbuf -oL -eL cat raw.ref | nc -l 38472 > tcp.trace &
exec_n_test ./init.sh $conf_string 
exec_n_test ./config.sh 0
exec_n_test ./read_mo.sh 0 9
check_equal_files raw.ref ent.trace
exec_n_test ./inval.sh 0
exec_n_test ./deinit.sh 0

stdbuf -oL -eL cat raw2.ref | nc -l 38472 > tcp.trace &
exec_n_test ./init.sh $conf_string 
exec_n_test ./config.sh 0
exec_n_test ./read_until_mo.sh 0 E
check_equal_files raw3.ref ent.trace
exec_n_test ./inval.sh 0
exec_n_test ./deinit.sh 0

stdbuf -oL -eL cat raw.ref | nc -l 38472 > tcp.trace &
exec_n_test ./init.sh $conf_string 
exec_n_test ./config.sh 0
exec_n_test ./wrnrd_mo.sh 0 `cat raw2.ref` 9 
check_equal_files raw.ref ent.trace
check_equal_files raw2.ref tcp.trace
exec_n_test ./inval.sh 0
exec_n_test ./deinit.sh 0

stdbuf -oL -eL cat raw2.ref | nc -l 38472 > tcp.trace &
exec_n_test ./init.sh $conf_string 
exec_n_test ./config.sh 0
exec_n_test ./wrnrd_until_mo.sh 0 `cat raw2.ref` E
check_equal_files raw3.ref ent.trace
check_equal_files raw2.ref tcp.trace
exec_n_test ./inval.sh 0
exec_n_test ./deinit.sh 0

stdbuf -oL -eL cat raw2.ref | nc -l 38472 > tcp.trace &
exec_n_test ./init.sh $conf_string 
exec_n_test ./config.sh 0
exec_n_test ./read_bin_mo.sh 0 8
check_equal_files raw2_bin.ref ent.trace
exec_n_test ./inval.sh 0
exec_n_test ./deinit.sh 0

stdbuf -oL -eL cat raw2.ref | nc -l 38472 > tcp.trace &
exec_n_test ./init.sh $conf_string 
exec_n_test ./config.sh 0
exec_n_test ./read_bin_until_mo.sh 0 E
check_equal_files raw3_bin.ref ent.trace
exec_n_test ./inval.sh 0
exec_n_test ./deinit.sh 0

stdbuf -oL -eL cat raw.ref | nc -l 38472 > tcp.trace &
exec_n_test ./init.sh $conf_string 
exec_n_test ./config.sh 0
exec_n_test ./wrnrd_bin_mo.sh 0 `cat raw2_bin.ref` 9 
check_equal_files raw_bin.ref ent.trace
check_equal_files raw2.ref tcp.trace
exec_n_test ./inval.sh 0
exec_n_test ./deinit.sh 0

stdbuf -oL -eL cat raw2.ref | nc -l 38472 > tcp.trace &
exec_n_test ./init.sh $conf_string 
exec_n_test ./config.sh 0
exec_n_test ./wrnrd_bin_until_mo.sh 0 `cat raw2_bin.ref` E
check_equal_files raw3_bin.ref ent.trace
check_equal_files raw2.ref tcp.trace
exec_n_test ./inval.sh 0
exec_n_test ./deinit.sh 0

echo "all test passed"

clean_all

exit 0
