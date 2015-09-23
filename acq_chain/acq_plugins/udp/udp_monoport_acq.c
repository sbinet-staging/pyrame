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


#include "udp_monoport_acq.h"

int open_udpsock(int port)
{
  int s;
  int on=0;
  struct sockaddr_in mysocketudp;
  s=socket(AF_INET,SOCK_DGRAM,0);
  if (s<0) {
    perror("socket");
    return -1;
  }
  setsockopt(s,SOL_SOCKET,SO_REUSEADDR,&on,sizeof(on));
  bzero(&mysocketudp,sizeof(struct sockaddr_in));
  mysocketudp.sin_family=AF_INET;
  mysocketudp.sin_addr.s_addr = htonl(INADDR_ANY);
  mysocketudp.sin_port = htons(port);
  if (bind(s,(struct sockaddr *)&mysocketudp, sizeof(mysocketudp))<0) {
    perror("bind error");
    return -1;
  } 
  return s;
}


//this function should initialize acquisition
//it should allocate and fill the specific structure
struct udp_monoport_acq_workspace *init_acq(char * port,char *param2, char *param3) {
  struct udp_monoport_acq_workspace *ws=malloc(sizeof(struct udp_monoport_acq_workspace));
  ws->port=atoi(port);
  //do whatever needed to initialized
  ws->socket=-1;
  //print a message if you want
  printf("udp monoport acquisition initialized with port=%d\n",ws->port);
  //return the workspace
  return ws;
}
 
//deinit the acquisition and destroy the specific structure
int deinit_acq(struct udp_monoport_acq_workspace *ws) {
  //stop acquisition
  stop_acq(ws);
  //destroy the specific structure
  free(ws);
  //print a message if you want
  printf("udp monoport acquisition deinitialized\n");
  //return 1 if success 0 otherwise
  return 1;
}


//this function start the acquisition
//it effectively open the socket 
int start_acq(struct udp_monoport_acq_workspace *ws) {
  //print a message if you want
  printf("udp_monoport_start_acq\n");
  //open a udp socket
  ws->socket=open_udpsock(ws->port);
  if (ws->socket==-1) {
    return 0;
  } else {
    printf("socket_id=%d\n",ws->socket);
  }
  return 1;
}


//this function stop the acquisition*
//it effectively close the socket
int stop_acq(struct udp_monoport_acq_workspace *ws) {
  //print a message if you want
  printf("udp_monoport_stop_acq\n");
  //close the socket
  close(ws->socket);
  ws->socket=-1;
  return 1;
}

int acquire_one_block(struct udp_monoport_acq_workspace *ws,unsigned char *buffer,int maxsize) {
  int size;
  fd_set socks;
  struct timeval timeout;
 
    timeout.tv_sec = 0;
    timeout.tv_usec = 50000;
    FD_ZERO(&socks);
    FD_SET(ws->socket,&socks);

    
    size=select(ws->socket+1,&socks,NULL,NULL,&timeout);
    if (size<0) {
      perror("select");
      return -1;
    }
    if (size==0)
      return 0;
    
    
    if (FD_ISSET(ws->socket,&socks)){
      size=read(ws->socket,buffer,maxsize);
      if (size<=0) {
        printf("size=%d closing socket\n",size);
        perror("read");
        close(ws->socket);
        return -1;
      } else {
        return size;
      }
    }
 
    printf("ERROR: this should never had happened\n");
    return -1;
}
