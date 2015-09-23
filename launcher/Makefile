OBJS=kill_pyrame.sh launch_pyrame_xfce4.sh launch_pyrame_gnome.sh autolauncher.py

all: 

clean:
	rm -f *.o *~ *.pyc

install: all
	cp -f $(OBJS) /usr/local/bin
	chmod +x /usr/local/bin/*pyrame*
	cp -f services.txt /opt/pyrame/services.d/pyrame_services.txt
	cat /opt/pyrame/services.d/* > /opt/pyrame/services.txt

uninstall:
	cd /usr/local/bin ; rm -f $(OBJS) 


unit_test:
	if test -f ./unit_test.sh; then ./unit_test.sh; fi
