. /usr/local/bin/unit_test_lib.sh
. /opt/pyrame/ports.sh

clean_all
echo
echo
echo "BINDING EXAMPLE TESTS"
echo
cmdmod /opt/pyrame/cmd_test.xml 2>&1 > server.trace&
sleep 1s
exec_n_test ./test_test
exec_n_test ./test_test++
exec_n_test ./test_test.py
exec_n_test ./test_test.sh
clean_all
