#include <unistd.h>
#include <sys/types.h> 
#include <sys/socket.h>
#include <arpa/inet.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <netpacket/packet.h>
#include <net/ethernet.h>
#include <sys/ioctl.h>
#include <net/if.h>  

#ifndef ETHACQ
#define ETHACQ

struct ethacq_workspace {
  char *interface;
  int socket;
} eth_acq;

struct ethacq_workspace* init_acq(char *,char *,char *);


#endif
