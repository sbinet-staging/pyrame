#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

#ifndef FILEACQ
#define FILEACQ

struct fileacq_workspace {
  char *filename;
  int tempo;
  int fd;
};

struct fileacq_workspace* init_acq(char *,char *,char *);


#endif
