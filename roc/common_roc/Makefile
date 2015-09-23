all:

clean:
	rm -f *.pyc *~ *.trace

install:
	if test -d /usr/lib/python2.6 ; then cp -f common_roc.py /usr/lib/python2.6; fi
	if test -d /usr/lib/python2.7 ; then cp -f common_roc.py /usr/lib/python2.7; fi
	if test -d /usr/lib64/python2.6 ; then cp -f common_roc.py /usr/lib64/python2.6; fi
	if test -d /usr/lib64/python2.7 ; then cp -f common_roc.py /usr/lib64/python2.7; fi

uninstall:
	if test -d /usr/lib/python2.6 ; then rm -f /usr/lib/python2.6/common_roc.py; rm -f /usr/lib/python2.6/common_roc.pyc; fi
	if test -d /usr/lib/python2.7 ; then rm -f /usr/lib/python2.7/common_roc.py; rm -f /usr/lib/python2.7/common_roc.pyc; fi
	if test -d /usr/lib64/python2.6 ; then rm -f /usr/lib64/python2.6/common_roc.py; rm -f /usr/lib64/python2.6/common_roc.pyc; fi
	if test -d /usr/lib64/python2.7 ; then rm -f /usr/lib64/python2.7/common_roc.py; rm -f /usr/lib64/python2.7/common_roc.pyc; fi

unit_test:
	if test -f ./unit_test.sh; then ./unit_test.sh; fi
