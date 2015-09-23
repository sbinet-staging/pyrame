all: test_test test_test++

test_test : test_test.c
	$(CC) -o test_test test_test.c -L.. -lbindpyrame -lm

test_test++ : test_test++.cpp
	$(CXX) -o test_test++ test_test++.cpp -L..  -lbindpyrame++

clean:
	rm -f *~ *.o test_test test_test++ 

install: all

uninstall:

unit_test:
	if test -f ./unit_test.sh; then ./unit_test.sh; fi
