all: converter

converter: converter.h converter.c
	gcc -g -Wall -o converter converter.c -I../libpyrame/ -L../libpyrame/ -L../bindings -lpyrame -lbindpyrame -lpthread -ldl -lm

clean:
	rm -f *.o *~ \#* converter

install: all
	cp -f converter /usr/bin
	cp -f pyrame_converter.h /usr/include

uninstall:
	rm -f /usr/bin/converter
	rm -f /usr/include/pyrame_converter.h

unit_test:
	if test -f ./unit_test.sh; then ./unit_test.sh; fi
