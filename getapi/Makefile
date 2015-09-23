all:

clean:
	rm -f *~
	rm -f *.pyc

install:
	cp -f gen_api.py /usr/bin
	cp -f apipools.js /opt/pyrame
	if test -d /usr/lib/python2.6 ; then cp getapi.py /usr/lib/python2.6; fi
	if test -d /usr/lib/python2.7 ; then cp getapi.py /usr/lib/python2.7; fi
	if test -d /usr/lib64/python2.6 ; then cp getapi.py /usr/lib64/python2.6; fi
	if test -d /usr/lib64/python2.7 ; then cp getapi.py /usr/lib64/python2.7; fi
	if test -d /usr/lib/python2.6 ; then cp apipools.py /usr/lib/python2.6; fi
	if test -d /usr/lib/python2.7 ; then cp apipools.py /usr/lib/python2.7; fi
	if test -d /usr/lib64/python2.6 ; then cp apipools.py /usr/lib64/python2.6; fi
	if test -d /usr/lib64/python2.7 ; then cp apipools.py /usr/lib64/python2.7; fi

uninstall:
	rm -f /usr/bin/gen_api.py
	if test -d /usr/lib/python2.6 ; then rm -f /usr/lib/python2.6/getapi.py; rm -f /usr/lib/python2.6/getapi.pyc; fi
	if test -d /usr/lib/python2.7 ; then rm -f /usr/lib/python2.7/getapi.py; rm -f /usr/lib/python2.7/getapi.pyc; fi
	if test -d /usr/lib64/python2.6 ; then rm -f /usr/lib64/python2.6/getapi.py; rm -f /usr/lib64/python2.6/getapi.pyc; fi
	if test -d /usr/lib64/python2.7 ; then rm -f /usr/lib64/python2.7/getapi.py; rm -f /usr/lib64/python2.7/getapi.pyc; fi
	if test -d /usr/lib/python2.6 ; then rm -f /usr/lib/python2.6/apipools.py; rm -f /usr/lib/python2.6/apipools.pyc; fi
	if test -d /usr/lib/python2.7 ; then rm -f /usr/lib/python2.7/apipools.py; rm -f /usr/lib/python2.7/apipools.pyc; fi
	if test -d /usr/lib64/python2.6 ; then rm -f /usr/lib64/python2.6/apipools.py; rm -f /usr/lib64/python2.6/apipools.pyc; fi
	if test -d /usr/lib64/python2.7 ; then rm -f /usr/lib64/python2.7/apipools.py; rm -f /usr/lib64/python2.7/apipools.pyc; fi

unit_test:
	if test -f ./unit_test.sh; then ./unit_test.sh; fi

