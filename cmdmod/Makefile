PYTHON_VERSION=$(shell if test -f /usr/bin/python2.7-config; then echo 7; else if test -f /usr/bin/python2.6-config; then echo 6; else echo 0; fi; fi)


all: cmdmod

cmdmod: cmdmod.c cmdmod.h cmdmod_python.o cmdmod_dummy.o cmdmod_bash.o cmdmod_lua.o cmdmod_c.o
	gcc -rdynamic -O0 -g -Wall -o cmdmod cmdmod.c cmdmod_python.o cmdmod_bash.o cmdmod_lua.o cmdmod_dummy.o cmdmod_c.o -lpyrame -L../libpyrame/ -lpthread -lexpat `python2.$(PYTHON_VERSION)-config --cflags` `python2.$(PYTHON_VERSION)-config --libs` -llua -ldl;

cmdmod_python.o: cmdmod_python.c cmdmod_python.h cmdmod.h
ifeq ($(PYTHON_VERSION),0)
	echo "no python version found, please install python devel package"
	exit 1
endif
	gcc -rdynamic -O0 -g -Wall -c cmdmod_python.c `python2.$(PYTHON_VERSION)-config --cflags` ;

cmdmod_dummy.o: cmdmod_dummy.c cmdmod_dummy.h cmdmod.h
	gcc -rdynamic -O0 -g -Wall -c cmdmod_dummy.c

cmdmod_lua.o: cmdmod_lua.c cmdmod_lua.h cmdmod.h
	gcc -rdynamic -O0 -g -Wall -c cmdmod_lua.c

cmdmod_bash.o: cmdmod_bash.c cmdmod_bash.h cmdmod.h
	gcc -rdynamic -O0 -g -Wall -c cmdmod_bash.c 

cmdmod_c.o: cmdmod_c.c cmdmod_c.h cmdmod.h
	gcc -rdynamic -O0 -g -Wall -c cmdmod_c.c

install: cmdmod
	cp -f cmdmod /usr/bin
	cp -f *helper* /opt/pyrame

uninstall:
	rm -f /usr/bin/cmdmod

clean:
	rm -f cmdmod *~ *.o

unit_test:
	if test -f ./unit_test.sh; then ./unit_test.sh; fi
