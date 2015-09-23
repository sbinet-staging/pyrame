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

#ifndef NOACQ
#define NOACQ

struct noacq_workspace {
};

struct noacq_workspace* init_acq(char *,char *,char *);


#endif
