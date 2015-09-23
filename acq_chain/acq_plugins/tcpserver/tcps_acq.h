#include <unistd.h>
#include <sys/types.h> 
#include <sys/socket.h>
#include <arpa/inet.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <net/ethernet.h>
#include <sys/ioctl.h>
#include <net/if.h>  

#ifndef TCPSACQ
#define TCPSACQ

struct tcpsacq_workspace {
  int port;
  int listen_socket;
  int client_socket;
};

struct tcpsacq_workspace* init_acq(char *,char *,char *);
int stop_acq(struct tcpsacq_workspace *);

#endif
