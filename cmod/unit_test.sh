. /usr/local/bin/unit_test_lib.sh
. /opt/pyrame/ports.sh

clean_all
echo 
echo 
echo "CMOD TESTS"
echo
cmdmod /opt/pyrame/cmd_cmod.xml 2>&1 > server.trace&
exec_n_test ./new_device.sh det mydet 0
exec_n_test ./new_device.sh lda lda1 1
exec_n_test ./set_param.sh 2 "lda_mac_addr" "00:0a:35:01:fe:07"
exec_n_test ./set_param.sh 2 "lda_pc_dev" "eth1"
exec_n_test ./new_device.sh dif dif1 2
exec_n_test ./set_param.sh 3 "dif_lda_port" "6"
exec_n_test ./new_device.sh domain arduino 0
exec_n_test ./set_param.sh 4 "domain_ip" "10.220.0.99"
exec_n_test ./new_device.sh ard resetter 4
exec_n_test ./new_device.sh roc roc1 3
exec_n_test ./new_device.sh roc roc2 3
exec_n_test ./new_device.sh roc roc3 3
exec_n_test ./new_device.sh roc roc4 3
clean_all

