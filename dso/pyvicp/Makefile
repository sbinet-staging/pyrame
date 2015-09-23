.SILENT:

all: pyvicp

pyvicp:
	python2 pyvicp.py build > /dev/null

install: all
	python2 pyvicp.py install > /dev/null

clean:
	rm -rf build

uninstall:


unit_test:
	if test -f ./unit_test.sh; then ./unit_test.sh; fi

uninstall:
	rm -f /usr/local/lib/python2.6/dist-packages/vicp.so
	rm -f /usr/local/lib/python2.6/dist-packages/vicp-1.0.egg-info
	rm -f /usr/local/lib/python2.7/dist-packages/vicp.so
	rm -f /usr/local/lib/python2.7/dist-packages/vicp-1.0.egg-info
