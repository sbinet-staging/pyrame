all: udp_monoport_acq.so udp_multiport_acq.so

udp_monoport_acq.so: udp_monoport_acq.c
	$(CC) -g -Wall -fPIC -o udp_monoport_acq.so -shared udp_monoport_acq.c

udp_multiport_acq.so: udp_multiport_acq.c
	$(CC) -g -Wall -fPIC -o udp_multiport_acq.so -shared udp_multiport_acq.c

install: udp_monoport_acq.so udp_multiport_acq.so
	cp -f udp_monoport_acq.so /opt/pyrame
	cp -f udp_multiport_acq.so /opt/pyrame

uninstall:

clean:
	rm -rf *.so *~ running*raw test*.raw nc_test.txt

unit_test:
	if test -f ./unit_test.sh; then ./unit_test.sh; fi
