all: eth_acq.so

eth_acq.so: eth_acq.c
	if test `uname -s` != "Linux"; then echo "compilable only on Linux"; else gcc -g -Wall -fPIC -o eth_acq.so -shared eth_acq.c; fi

install: eth_acq.so
	cp -f eth_acq.so /opt/pyrame

uninstall:

clean:
	rm -rf *.so *~

unit_test:
	if test -f ./unit_test.sh; then ./unit_test.sh; fi
