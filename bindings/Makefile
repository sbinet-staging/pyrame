all: libbindpyrame.so libbindpyrame++.so
	make -C examples

libbindpyrame.so: bindpyrame.o shbuffer.o
	$(CC) -g -o libbindpyrame.so -shared bindpyrame.o shbuffer.o -lexpat -lm

bindpyrame.o: bindpyrame.c bindpyrame.h
	$(CC) -g -c -fPIC bindpyrame.c

shbuffer.o: shbuffer.c bindpyrame.h
	$(CC) -g -c -fPIC shbuffer.c

libbindpyrame++.so: bindpyrame++.cpp bindpyrame++.hpp bindpyrame++.o
	$(CC) -g -o libbindpyrame++.so -shared bindpyrame++.o -lexpat -lstdc++

bindpyrame++.o:
	$(CC) -g -c -fPIC bindpyrame++.cpp

install: libbindpyrame.so libbindpyrame++.so
	if test -d /usr/lib/python2.6 ; then cp -f bindpyrame.py /usr/lib/python2.6; fi
	if test -d /usr/lib/python2.7 ; then cp -f bindpyrame.py /usr/lib/python2.7; fi
	if test -d /usr/lib64/python2.6 ; then cp -f bindpyrame.py /usr/lib64/python2.6; fi
	if test -d /usr/lib64/python2.7 ; then cp -f bindpyrame.py /usr/lib64/python2.7; fi
	cp -f libbindpyrame.so /usr/lib
	cp -f bindpyrame.h /usr/include
	cp -f libbindpyrame++.so /usr/lib
	cp -f bindpyrame++.hpp /usr/include
	cp -f bindpyrame.js /opt/pyrame
	make -C examples install

uninstall:
	if test -d /usr/lib/python2.6 ; then rm -f /usr/lib/python2.6/bindpyrame.py; rm -f /usr/lib/python2.6/bindpyrame.pyc; fi
	if test -d /usr/lib/python2.7 ; then rm -f /usr/lib/python2.7/bindpyrame.py; rm -f /usr/lib/python2.7/bindpyrame.pyc; fi
	if test -d /usr/lib64/python2.6 ; then rm -f /usr/lib64/python2.6/bindpyrame.py; rm -f /usr/lib64/python2.6/bindpyrame.pyc; fi
	if test -d /usr/lib64/python2.7 ; then rm -f /usr/lib64/python2.7/bindpyrame.py; rm -f /usr/lib64/python2.7/bindpyrame.pyc; fi
	rm -f /usr/lib/libbindpyrame.so
	rm -f /usr/include/bindpyrame.h
	rm -f /usr/lib/libbindpyrame++.so
	rm -f /usr/include/bindpyrame++.hpp
	make -C examples uninstall

clean :
	rm -f *.o *.so *~
	make -C examples clean 

unit_test:
	if test -f ./unit_test.sh; then ./unit_test.sh; fi
	make -C examples unit_test
