all: shmem_dumper 

shmem_dumper: shmem_dumper.c 
	$(CC) -g -Wall -lpthread -o shmem_dumper shmem_dumper.c -lm -lbindpyrame

%.o : %.c %.h
	$(CC) -fPIC -g -Wall  -c $< 

clean :
	rm -f *.o *~ shmem_dumper 

install:
