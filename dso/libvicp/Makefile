.SILENT:

all: libvicp

libvicp:
	$(CC) -g -Wall -fPIC vicp.c -o libvicp.so -shared

install: all
	cp -f vicp.h /usr/include
	cp -f libvicp.so /usr/lib
	cp -f libvicp.so /usr/lib64

uninstall:
	rm -f /usr/include/vicp.h
	rm -f /usr/lib/libvicp.so
	rm -f /usr/lib64/libvicp.so

clean:
	rm -rf *.so

unit_test:
	if test -f ./unit_test.sh; then ./unit_test.sh; fi
