all: cmd_raweth.so

cmd_raweth.so: cmd_raweth.c 
	if test `uname -s` != "Linux"; then echo "compilable only on Linux"; else gcc -rdynamic -g -Wall -fPIC -o cmd_raweth.so -shared cmd_raweth.c ; fi

clean:
	rm -f cmd_raweth.so *~

install: all
	cp -f cmd_raweth.so cmd_raweth.xml /opt/pyrame

uninstall:

unit_test:
	if test -f ./unit_test.sh; then ./unit_test.sh; fi
