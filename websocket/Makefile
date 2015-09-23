.SILENT:

all :

clean:
	rm -f *~ *.pyc

install:
	find . -name "*_wsh.py" -exec cp {} /opt/pyrame \;

uninstall:

unit_test:
	if test -f ./unit_test.sh; then ./unit_test.sh; fi
