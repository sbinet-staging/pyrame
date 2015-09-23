all: tcps_acq.so

tcps_acq.so: tcps_acq.c
	$(CC) -g -Wall -fPIC -o tcps_acq.so -shared tcps_acq.c

install: tcps_acq.so
	cp -f tcps_acq.so /opt/pyrame

uninstall:

clean:
	rm -rf *.so *~ running*.raw test*.raw nc_test.txt


unit_test:
	if test -f ./unit_test.sh; then ./unit_test.sh; fi
