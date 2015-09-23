.SILENT:

all :

clean:
	rm -f *~ *.pyc *.trace

install:
	find . -name "*.xml" -exec cp {} /opt/pyrame \;
	find . -name "*.py" -exec cp {} /opt/pyrame \;
	find . -name "cmd_*.py" -exec gen_api.py {} \;
	find . -name "*.api" -exec mv {} /opt/pyrame \;
	cp -f get_dev_linux.sh /usr/local/bin
	cp -f get_dev_linux.py /usr/local/bin

uninstall:
	rm -f /usr/local/bin/get_dev_linux.sh

unit_test:
	if test -f ./unit_test.sh; then ./unit_test.sh; fi
