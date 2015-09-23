echo 
echo 
echo "UNIT_TEST TESTS"
echo
. ./unit_test_lib.sh
exec_n_test ./always_work.sh
exec_n_test_fail ./never_work.sh
check_equal_files ./Makefile ./Makefile
check_diff_files ./Makefile ./always_work.sh
check_empty_file ./empty.txt
check_not_empty_file ./Makefile
test="1234567890"
check_equal_values $test "1234567890"
rm -f ent_trace
