all:

clean:
	rm -f *.pyc *~ *.trace

install:
	if test -d /usr/lib/python2.6 ; then cp -f pools.py /usr/lib/python2.6; fi
	if test -d /usr/lib/python2.7 ; then cp -f pools.py /usr/lib/python2.7; fi
	if test -d /usr/lib64/python2.6 ; then cp -f pools.py /usr/lib64/python2.6; fi
	if test -d /usr/lib64/python2.7 ; then cp -f pools.py /usr/lib64/python2.7; fi

uninstall:
	if test -d /usr/lib/python2.6 ; then rm -f /usr/lib/python2.6/pools.py; rm -f /usr/lib/python2.6/pools.pyc; fi
	if test -d /usr/lib/python2.7 ; then rm -f /usr/lib/python2.7/pools.py; rm -f /usr/lib/python2.7/pools.pyc; fi
	if test -d /usr/lib64/python2.6 ; then rm -f /usr/lib64/python2.6/pools.py; rm -f /usr/lib64/python2.6/pools.pyc; fi
	if test -d /usr/lib64/python2.7 ; then rm -f /usr/lib64/python2.7/pools.py; rm -f /usr/lib64/python2.7/pools.pyc; fi

unit_test:
	if test -f ./unit_test.sh; then ./unit_test.sh; fi
