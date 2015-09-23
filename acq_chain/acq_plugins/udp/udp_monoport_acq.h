#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>

#ifndef UDP_MONOPORT_ACQ
#define UDP_MONOPORT_ACQ

struct udp_monoport_acq_workspace {
  unsigned short port;
  int socket;
};

struct udp_monoport_acq_workspace* init_acq(char *,char *,char *); 
int stop_acq(struct udp_monoport_acq_workspace *);

#endif
