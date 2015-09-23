.SILENT:

all :
	if [ -f Makefile.local ]; then \
		make -f Makefile.local all; \
	fi

clean:
	rm -rf *~ *.pyc *.trace __pycache__ 
	if [ -f Makefile.local ]; then \
		make -f Makefile.local clean; \
	fi

install:
	find . -name "*.xml" -exec cp {} /opt/pyrame \;
	find . -name "*.py" -exec cp {} /opt/pyrame \;
	find . -name "*.lua" -exec cp {} /opt/pyrame \;
	find . -name "cmd_*.py" | xargs -I file gen_api.py file
	find . -name "*.api" -exec mv {} /opt/pyrame \;
	if [ -f Makefile.local ]; then \
		make -f Makefile.local install; \
	fi

uninstall:
	if [ -f Makefile.local ]; then \
                make -f Makefile.local uninstall; \
        fi

unit_test:
	if test -f ./unit_test.sh; then ./unit_test.sh; fi

size: clean
	if test -d docs; then make -C docs clean; fi
	wc `find . -regextype posix-extended -regex "(.*Makefile|.*\.(py|c|xsl|xml|h|ino|pde|sh|cc|C|cpp|hpp|css|html|js))" -print`

