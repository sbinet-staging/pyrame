#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#ifndef UDPACQ
#define UDPACQ

#define MAX_UDP_PORTS 128

struct udp_multiport_acq_workspace {
  char *ports;
  unsigned short *shports;
  int *sockets;
  int nb_ports;
} udp_acq;

struct udp_multiport_acq_workspace* init_acq(char *,char *,char *); 
int stop_acq(struct udp_multiport_acq_workspace *);

#endif
