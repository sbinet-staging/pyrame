all: tcpc_acq.so

tcpc_acq.so: tcpc_acq.c
	$(CC) -g -Wall -fPIC -o tcpc_acq.so -shared tcpc_acq.c

install: tcpc_acq.so
	cp -f tcpc_acq.so /opt/pyrame

uninstall:

clean:
	rm -rf *.so *~ test*.raw running*.raw nc_test.txt

unit_test:
	if test -f ./unit_test.sh; then ./unit_test.sh; fi
