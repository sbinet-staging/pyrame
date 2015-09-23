all:
	./gener_ports_local.sh

clean:	
	rm -f *~
	rm -f ports.sh

install: all
	cp -f ports.txt /opt/pyrame/ports.d/pyrame_ports.txt
	cp -f gener_ports.sh /opt/pyrame
	/opt/pyrame/gener_ports.sh

uninstall:

unit_test:
	if test -f ./unit_test.sh; then ./unit_test.sh; fi
