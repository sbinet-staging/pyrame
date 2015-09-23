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


#include "tcpc_acq.h"
#include <errno.h>
#include <fcntl.h>


int open_acqsock(char * host,int port)
{
  int s;
  int res;
  int mode;
  struct sockaddr_in servaddr;
  struct timeval timeout;
  s=socket(AF_INET,SOCK_STREAM,0);
  if (s==-1) {
    perror("socket");
    return -1;
  }
  timeout.tv_sec=1;
  timeout.tv_usec=0;
  if (setsockopt(s,SOL_SOCKET,SO_RCVTIMEO,(char*)&timeout,sizeof(timeout))<0) {
      perror("setsockopt");
      return -1;
  }
  bzero(&servaddr,sizeof(servaddr));
  servaddr.sin_family=AF_INET;
  servaddr.sin_addr.s_addr=inet_addr(host);
  servaddr.sin_port=htons(port);
  res=connect(s,(struct sockaddr *)&servaddr,sizeof(servaddr));
  if (res<0) {
    perror("connect");
    return -1;
  }
  mode=fcntl(s,F_GETFL,0);
  mode|=O_NONBLOCK;
  fcntl(s,F_SETFL,mode);
  return s;
}



//this function should initialize acquisition
//it should allocate and fill the specific structure
struct tcpcacq_workspace* init_acq(char * host,char *port, char *init_string) {
  
  //allocate and fill the workspace
  struct tcpcacq_workspace *ws=malloc(sizeof(struct tcpcacq_workspace));
  //store the params
  ws->host=strdup(host);
  ws->port=atoi(port);
  ws->init_string=strdup(init_string);
  //do whatever needed to initialized
  ws->socket=-1;
  //print a message if you want
  printf("tcp client acquisition initialized with host=%s port=%d init_string=%s\n",ws->host,ws->port,ws->init_string);
  //return the workspace
  return ws;
}
 
//deinit the acquisition and destroy the specific structure
int deinit_acq(struct tcpcacq_workspace *ws) {
  //deinit the acquisition
  if (ws->socket!=-1)
    close(ws->socket);
  ws->socket=-1;
  //destroy the specific structure
  free(ws->host);
  free(ws->init_string);
  free(ws);
  //print a message if you want
  printf("tcp client acquisition deinitialized\n");
  //return 1 if success 0 otherwise
  return 1;
}


//this function start the acquisition
//it effectively open the socket 
int start_acq(struct tcpcacq_workspace *ws) {
  //print a message if you want
  char * msg=strdup(ws->init_string);
  printf("tcpc_start_acq\n");
  //open a socket
  ws->socket=open_acqsock(ws->host,ws->port);
  if (ws->socket<0) {
    return -1;
  } else
    printf("socket_id=%d\n",ws->socket);
  msg[strlen(msg)]='\n';
  write(ws->socket,msg,strlen(ws->init_string));
  return 1;
}


//this function stop the acquisition*
//it effectively close the socket
int stop_acq(struct tcpcacq_workspace *ws) {
  //print a message if you want
  printf("tcpc_stop_acq\n");
  //disconnect 
  if (ws->socket!=-1) {
    close(ws->socket);
  }
  ws->socket=-1;
  return 1;
}

int acquire_one_block(struct tcpcacq_workspace *ws,unsigned char *buffer,int maxsize) {
  int size;
  if (ws->socket!=-1) {
    //printf("reading the socket %d\n",ws->socket);
    size=read(ws->socket,buffer,maxsize);
    if (size<0) {
      if (errno==EAGAIN) {
	usleep(2000);
	return 0;
      } else {
	perror("read");
      }
    }
    return size;
  } else {
    return -1;
  }
}
