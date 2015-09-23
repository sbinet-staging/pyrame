all: file_acq.so

file_acq.so: file_acq.c
	$(CC) -g -Wall -fPIC -o file_acq.so -shared file_acq.c

install: file_acq.so
	cp -f file_acq.so /opt/pyrame

uninstall:

clean:
	rm -rf *.so *~

unit_test:
	if test -f ./unit_test.sh; then ./unit_test.sh; fi
