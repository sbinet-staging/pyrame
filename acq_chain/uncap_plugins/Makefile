all: uncap_dummy.so uncap_addclock.so uncap_extclock.so uncap_udptest.so uncap_udpdatatest.so uncap_udpcontroltest.so


%.so: %.c
	$(CC) -g -Wall -fPIC -o $@ -shared $<

clean:
	rm -f *.so *~

install: all
	cp -f *.so /opt/pyrame
	cp -f uncap.h /usr/include

uninstall:


unit_test:
	if test -f ./unit_test.sh; then ./unit_test.sh; fi
