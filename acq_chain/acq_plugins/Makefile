.SILENT:

all:
	FAIL=0; for i in `cat compile_order.txt`; do if test -d $$i; then make -C $$i 2>&1 ; if test ! $$? -eq "0"; then echo "FAILED $$i";FAIL=1; fi; fi; done; exit $$FAIL

clean:
	FAIL=0; for i in `cat compile_order.txt`; do if test -d $$i; then make -C $$i clean 2>&1 ;  if test ! $$? -eq "0"; then echo "FAILED $$i";FAIL=1; fi; fi; done; exit $$FAIL

install: all 
	if test -f install.sh; then ./install.sh; fi
	FAIL=0; for i in `cat compile_order.txt`; do if test -d $$i; then make -C $$i install 2>&1 ;  if test ! $$? -eq "0"; then echo "FAILED $$i";FAIL=1; fi; fi; done; exit $$FAIL

uninstall:
	FAIL=0; for i in `cat compile_order.txt`; do if test -d $$i; then make -C $$i uninstall 2>&1 ;  if test ! $$? -eq "0"; then echo "FAILED $$i";FAIL=1; fi; fi; done; exit $$FAIL

size: clean 
	make -C docs clean
	wc `find . -regextype posix-extended -regex "(.*Makefile|.*\.(py|c|xsl|xml|h|ino|pde|sh|cc|C|cpp|hpp|css|html|js))" -print`

unit_test:
	FAIL=0; for i in `cat compile_order.txt`; do if test -d $$i; then make -C $$i unit_test 2>&1 ;  if test ! $$? -eq "0"; then echo "FAILED $$i";FAIL=1; fi; fi; done; exit $$FAIL

tarball: clean
	make -C docs clean 2>&1 
	tar cvfz ../pyrame.tgz -X tarball_exclude ../pyrame/  2>&1 
