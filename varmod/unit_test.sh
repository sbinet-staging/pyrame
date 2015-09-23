. /usr/local/bin/unit_test_lib.sh
. /opt/pyrame/ports.sh

clean_all
echo 
echo 
echo "VARMOD TESTS"
echo
cmdmod /opt/pyrame/cmd_varmod.xml 2>&1 > server.trace&
exec_n_test ./setvar.sh x 2
checkretstr 2 ./getvar.sh x
exec_n_test ./intopvar.sh x + 2
checkretstr 4 ./getvar.sh x
exec_n_test ./intopvar.sh x - 2
checkretstr 2 ./getvar.sh x
exec_n_test ./intopvar.sh x x 2
checkretstr 4 ./getvar.sh x
exec_n_test ./setvar.sh y toto
checkretstr toto ./getvar.sh y
exec_n_test ./stropvar.sh y c titi 
checkretstr tototiti ./getvar.sh y

clean_all
