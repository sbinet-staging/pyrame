all:

clean:
	rm -f *~

install:
	cp -f chkpyr.py /usr/bin
	cp -f chkpyr2.py /usr/bin

uninstall:
	rm -f /usr/bin/chkpyr.py
	rm -f /usr/bin/chkpyr2.py

unit_test:
	if test -f ./unit_test.sh; then ./unit_test.sh; fi
