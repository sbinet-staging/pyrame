all:

clean:
	rm -f *.pyc *~ *_noblank*.xml

install:
	if test -d /usr/lib/python2.6 ; then cp -f xmlConf.py /usr/lib/python2.6; fi
	if test -d /usr/lib/python2.7 ; then cp -f xmlConf.py /usr/lib/python2.7; fi
	if test -d /usr/lib64/python2.6 ; then cp -f xmlConf.py /usr/lib64/python2.6; fi
	if test -d /usr/lib64/python2.7 ; then cp -f xmlConf.py /usr/lib64/python2.7; fi
	if test -d /usr/lib/python2.6 ; then cp -f apc.py /usr/lib/python2.6; fi
	if test -d /usr/lib/python2.7 ; then cp -f apc.py /usr/lib/python2.7; fi
	if test -d /usr/lib64/python2.6 ; then cp -f apc.py /usr/lib64/python2.6; fi
	if test -d /usr/lib64/python2.7 ; then cp -f apc.py /usr/lib64/python2.7; fi
	cp -f calxml /usr/bin
	cp -f pyrame.xml /opt/pyrame/calxml_defaults.d
	cp -f gener_calxml_defaults.sh /opt/pyrame
	/opt/pyrame/gener_calxml_defaults.sh

uninstall:
	if test -d /usr/lib/python2.6 ; then rm -f /usr/lib/python2.6/xmlConf.py; rm -f /usr/lib/python2.6/xmlConf.pyc; fi
	if test -d /usr/lib/python2.7 ; then rm -f /usr/lib/python2.7/xmlConf.py; rm -f /usr/lib/python2.7/xmlConf.pyc; fi
	if test -d /usr/lib64/python2.6 ; then rm -f /usr/lib64/python2.6/xmlConf.py; rm -f /usr/lib64/python2.6/xmlConf.pyc; fi
	if test -d /usr/lib64/python2.7 ; then rm -f /usr/lib64/python2.7/xmlConf.py; rm -f /usr/lib64/python2.7/xmlConf.pyc; fi
	if test -d /usr/lib/python2.6 ; then rm -f /usr/lib/python2.6/apc.py; rm -f /usr/lib/python2.6/apc.pyc; fi
	if test -d /usr/lib/python2.7 ; then rm -f /usr/lib/python2.7/apc.py; rm -f /usr/lib/python2.7/apc.pyc; fi
	if test -d /usr/lib64/python2.6 ; then rm -f /usr/lib64/python2.6/apc.py; rm -f /usr/lib64/python2.6/apc.pyc; fi
	if test -d /usr/lib64/python2.7 ; then rm -f /usr/lib64/python2.7/apc.py; rm -f /usr/lib64/python2.7/apc.pyc; fi
	rm -f /usr/bin/calxml


unit_test:
	if test -f ./unit_test.sh; then ./unit_test.sh; fi
