. /usr/local/bin/unit_test_lib.sh
. /opt/pyrame/ports.sh

clean_all
echo 
echo 
echo "APIPOOLS TESTS"
echo
exec_n_test ./unit_test.py
