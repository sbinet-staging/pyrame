all: noacq_acq.so

noacq_acq.so: noacq_acq.c
	$(CC) -g -Wall -fPIC -o noacq_acq.so -shared noacq_acq.c

install: noacq_acq.so
	cp -f noacq_acq.so /opt/pyrame

uninstall:

clean:
	rm -rf *.so *~

unit_test:
	if test -f ./unit_test.sh; then ./unit_test.sh; fi
