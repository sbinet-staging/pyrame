all: acq_server
OBJS=acquisition.o commands.o stats.o uncap.o buffers.o consumers.o data_socket.o shmem.o cache.o scheduler.o


%.o : %.c %.h libacq.h
	$(CC) -fPIC -g -Wall -I../../libpyrame/ -c $< 

acq_server: libacq.h acq_server.c $(OBJS)
	$(CC) -g -Wall -o acq_server $(OBJS) acq_server.c -I../../libpyrame/ -L../../libpyrame/ -lpyrame -lpthread -ldl

clean :
	rm -f *.o *~ \#* acq_server

install: all
	cp -f acq_server /usr/bin

uninstall: 
	rm -f /usr/bin/acq_server


unit_test:
	if test -f ./unit_test.sh; then ./unit_test.sh; fi
