. /usr/local/bin/unit_test_lib.sh
. /opt/pyrame/ports.sh

clean_all

echo
echo
echo "TEST DUMMY TESTS"
echo
cmdmod /opt/pyrame/cmd_test_dummy.xml 2>&1 > server.trace&
exec_n_test ./void.sh
clean_all

echo
echo
echo "TEST C TESTS"
echo
cmdmod /opt/pyrame/cmd_test_c.xml 2>&1 > server.trace&
cmdmod /opt/pyrame/cmd_varmod.xml 2>&1 > varmod.trace&
exec_n_test ./void.sh
exec_n_test ./onearg.sh test1
exec_n_test ./onearg.sh ""
exec_n_test_fail ./onearg.sh
exec_n_test ./twoargs.sh test1 test2
exec_n_test_fail ./fail.sh
exec_n_test ./varmod.sh
exec_n_test ./onearg.sh `cat logo.b64`
clean_all

echo
echo
echo "TEST BASH TESTS"
echo
cmdmod /opt/pyrame/cmd_test_sh.xml 2>&1 > server.trace&
cmdmod /opt/pyrame/cmd_varmod.xml 2>&1 > varmod.trace&
exec_n_test ./void.sh
exec_n_test ./onearg.sh test1
exec_n_test ./onearg.sh ""
exec_n_test_fail ./onearg.sh
exec_n_test ./twoargs.sh test1 test2
exec_n_test_fail ./fail.sh
exec_n_test ./varmod.sh
exec_n_test ./onearg.sh `cat logo.b64`
clean_all


echo
echo
echo "TEST LUA TESTS"
echo
cmdmod /opt/pyrame/cmd_test_lua.xml 2>&1 > server.trace&
cmdmod /opt/pyrame/cmd_varmod.xml 2>&1 > varmod.trace&
exec_n_test ./void.sh
exec_n_test ./onearg.sh test1
exec_n_test ./onearg.sh ""
exec_n_test_fail ./onearg.sh
exec_n_test ./twoargs.sh test1 test2
exec_n_test_fail ./fail.sh
exec_n_test ./varmod.sh
exec_n_test ./onearg.sh `cat logo.b64`
clean_all

echo 
echo 
echo "TEST PYTHON TESTS"
echo
cmdmod /opt/pyrame/cmd_test_python.xml 2>&1 > server.trace&
cmdmod /opt/pyrame/cmd_varmod.xml 2>&1 > varmod.trace&
sleep 0.5s
exec_n_test ./void.sh
exec_n_test ./onearg.sh test1
exec_n_test ./onearg.sh ""
exec_n_test_fail ./onearg.sh
exec_n_test ./twoargs.sh test1 test2
exec_n_test_fail ./fail.sh
exec_n_test ./varmod.sh
exec_n_test ./onearg.sh `cat logo.b64`
clean_all

echo
echo
echo "AUTOLAUNCHER TESTS"
echo
autolauncher.py 2>&1 > server.trace&
sleep 1s
exec_n_test ./varmod.sh
clean_all

exit 0
