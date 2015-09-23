all:

clean:
	rm -f *.pyc *~ *.trace

install:
	if test -d /usr/lib/python2.6 ; then cp -f scpi.py /usr/lib/python2.6; fi
	if test -d /usr/lib/python2.7 ; then cp -f scpi.py /usr/lib/python2.7; fi
	if test -d /usr/lib64/python2.6 ; then cp -f scpi.py /usr/lib64/python2.6; fi
	if test -d /usr/lib64/python2.7 ; then cp -f scpi.py /usr/lib64/python2.7; fi

uninstall:
	if test -d /usr/lib/python2.6 ; then rm -f /usr/lib/python2.6/scpi.py; rm -f /usr/lib/python2.6/scpi.pyc; fi
	if test -d /usr/lib/python2.7 ; then rm -f /usr/lib/python2.7/scpi.py; rm -f /usr/lib/python2.7/scpi.pyc; fi
	if test -d /usr/lib64/python2.6 ; then rm -f /usr/lib64/python2.6/scpi.py; rm -f /usr/lib64/python2.6/scpi.pyc; fi
	if test -d /usr/lib64/python2.7 ; then rm -f /usr/lib64/python2.7/scpi.py; rm -f /usr/lib64/python2.7/scpi.pyc; fi

unit_test:
	if test -f ./unit_test.sh; then ./unit_test.sh; fi
