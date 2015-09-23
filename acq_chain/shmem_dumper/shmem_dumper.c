#include <bindpyrame.h>


int main(int argc,char **argv) {
  int streamid;
  struct shbuffer *shbuf;
  char buf[SHARED_BUFFER_SIZE+1];
  int ready;
  
  //parse arguments
  if (argc<2) {
    printf("usage : %s streamid",argv[0]);
    exit(1);
  }

  streamid=atoi(argv[0]);
  shbuf=open_shbuffer(streamid,NO_CREATE);
  printf("reading the stream %d\n",streamid);
  ready=isready_shbuffer(shbuf);
  printf("ready=%d\n",ready);
  ready_shbuffer(shbuf);
  ready=isready_shbuffer(shbuf);
  printf("ready=%d\n",ready);
 
  //infinitely read and discard data from shmem
  while(1) {
    read_shbuffer(shbuf,buf);
    buf[SHARED_BUFFER_SIZE]=0;
    printf("read : %s\n",buf);
  }
}
