#include <unistd.h>
#include <sys/types.h> 
#include <sys/socket.h>
#include <arpa/inet.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <net/ethernet.h>
#include <sys/ioctl.h>
#include <net/if.h>  

#ifndef ETHACQ
#define ETHACQ

struct tcpcacq_workspace {
  char *host;
  int port;
  char *init_string;
  int socket;
} tcpc_acq;

struct tcpcacq_workspace* init_acq(char *,char *,char *);


#endif
