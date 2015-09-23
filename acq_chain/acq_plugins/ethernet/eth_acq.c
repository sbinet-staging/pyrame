/*
Copyright 2012-2015 Frédéric Magniette, Miguel Rubio-Roy
This file is part of Pyrame.

Pyrame is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Pyrame is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with Pyrame.  If not, see <http://www.gnu.org/licenses/>
*/


#include "eth_acq.h"

int get_interface_index(char * name) {
  struct ifreq ifr;
  int sock=socket(AF_PACKET,SOCK_RAW,htons(ETH_P_ALL));
  strcpy(ifr.ifr_name,name);
  if (ioctl(sock,SIOCGIFINDEX, &ifr) == -1) {
    perror("ioctl");
    return -1;
  }
  close(sock);
  return ifr.ifr_ifindex; 
}

int open_acqsock(char * interface)
{
  int s;
  struct sockaddr_ll mysocket;
  int ifindex=-1;
  //int timeout=10;

  s=socket(AF_PACKET,SOCK_RAW,htons(ETH_P_ALL));
  if (s<0) {
    perror("socket");
    return -1;
  }

  if (interface!=NULL) {
    if (strcmp(interface,"all")) {
      ifindex=get_interface_index(interface);
      if (ifindex<0) {
	printf("bad interface\n");
	ifindex=-1;
      }
    }
  }
  bzero(&mysocket,sizeof(struct sockaddr_ll));
  mysocket.sll_family=AF_PACKET;
  mysocket.sll_protocol=htons(ETH_P_ALL);
  if (ifindex!=-1)
    mysocket.sll_ifindex=ifindex;
  else
    mysocket.sll_ifindex=0;

  if (bind(s,(struct sockaddr *)&mysocket, sizeof(mysocket))<0) {
    perror("bind");
    return -1;
  } 
  return s;
}



//this function should initialize acquisition
//it should allocate and fill the specific structure
struct ethacq_workspace* init_acq(char * interface,char *param2, char *param3) {
  
  //allocate and fill the workspace
  struct ethacq_workspace *ws=malloc(sizeof(struct ethacq_workspace));
  //param 1 should be the name of the interface ethx or emx
  ws->interface=strdup(interface);
  //do whatever needed to initialized
  ws->socket=-1;
  //print a message if you want
  printf("ethernet acquisition initialized with interface=%s\n",ws->interface);
  //return the workspace
  return ws;
}
 
//deinit the acquisition and destroy the specific structure
int deinit_acq(struct ethacq_workspace *ws) {
  printf("deinit the ethernet acquisition\n");
  if (ws->socket!=-1)
    close(ws->socket);
  ws->socket=-1;
  //destroy the specific structure
  free(ws->interface);
  free(ws);
  //print a message if you want
  printf("ethernet acquisition deinitialized\n");
  //return 1 if success 0 otherwise
  return 1;
}


//this function start the acquisition
//it effectively open the socket 
int start_acq(struct ethacq_workspace *ws) {
  //print a message if you want
  printf("eth_start_acq\n");
  //open a SOCKRAW
  ws->socket=open_acqsock(ws->interface);
  if (ws->socket==-1) {
    perror("open");
    return 0;
  } else
    printf("socket_id=%d\n",ws->socket);
  return 1;
}


//this function stop the acquisition*
//it effectively close the socket
int stop_acq(struct ethacq_workspace *ws) {
  //print a message if you want
  printf("eth_stop_acq\n");
  //disconnect 
  if (ws->socket!=-1) {
    close(ws->socket);
  }
  ws->socket=-1;
  return 1;
}

int acquire_one_block(struct ethacq_workspace *ws,unsigned char *buffer,int maxsize) {
  int size;
  if (ws->socket!=-1) {
    //printf("reading the socket %d\n",ws->socket);
    size=read(ws->socket,buffer,maxsize);
    if (size<=0) {
      printf("size=%d\n",size);
      perror("read");
    }
    return size;
  } else {
    return -1;
  }
}
