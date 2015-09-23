all: libpyrame.so
OBJS=netserv.o cmdserv.o cmdclient.o utils.o bindpyrame.o shbuffer.o

%.o : %.c pyrame.h
	gcc -O0 -fPIC -g -Wall -c $<

libpyrame.so: pyrame.h $(OBJS)
	gcc -O0 -g -Wall -fPIC -o libpyrame.so -shared $(OBJS) -lexpat -lpthread -lm 

install: libpyrame.so
	cp -f pyrame.h /usr/include
	cp -f libpyrame.so /usr/lib64
	cp -f libpyrame.so /usr/lib

uninstall:
	rm -f  /usr/include/pyrame.h
	rm -f /usr/lib/libpyrame.so
	rm -f /usr/lib64/libpyrame.so

clean :
	rm -f *.o *~ \#*  libpyrame*.so

unit_test:
	if test -f ./unit_test.sh; then ./unit_test.sh; fi
