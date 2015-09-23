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

#include "tcps_acq.h"



int open_acqsock(int port)
{
  int s;
  int res;
  struct sockaddr_in servaddr;
  s=socket(AF_INET,SOCK_STREAM,0);
  if (s==-1) {
    printf("cant create tcps socket on port %d\n",port);
    perror("socket");
    return -1;
  }
  bzero(&servaddr,sizeof(servaddr));
  servaddr.sin_family=AF_INET;
  servaddr.sin_addr.s_addr=htonl(INADDR_ANY);
  servaddr.sin_port=htons(port);
  res=bind(s,(struct sockaddr *)&servaddr,sizeof(servaddr));
  if (res<0) {
    printf("cant bind tcps socket on port %d\n",port);
    perror("bind");
    return -1;
  }
  res=listen(s,1024);
  if (res<0) {
    printf("cant listen on tcps socket on port %d\n",port);
    perror("listen");
    return -1;
  }
  return s;
}



//this function should initialize acquisition
//it should allocate and fill the specific structure
struct tcpsacq_workspace* init_acq(char * port,char *param2, char *param3) {
  
  //allocate and fill the workspace
  struct tcpsacq_workspace *ws=malloc(sizeof(struct tcpsacq_workspace));
  //store the params
  ws->port=atoi(port);
  //do whatever needed to initialized
  ws->listen_socket=open_acqsock(ws->port);
  if (ws->listen_socket<0) {
    perror("socket");
    ws->listen_socket=-1;
  } else
    printf("socket_id=%d\n",ws->listen_socket);
  ws->client_socket=-1;
  //print a message if you want
  printf("tcp server acquisition initialized \n");
  //return the workspace
  return ws;
}
 
//deinit the acquisition and destroy the specific structure
int deinit_acq(struct tcpsacq_workspace *ws) {
  //stop the acquisition if necessary
  stop_acq(ws);
  //stop the listening socket
  if (ws->listen_socket!=-1)
    close(ws->listen_socket);
  //destroy the specific structure
  free(ws);
  //print a message if you want
  printf("tcp server acquisition deinitialized\n");
  //return 1 if success 0 otherwise
  return 1;
}


//this function start the acquisition
int start_acq(struct tcpsacq_workspace *ws) {
  //print a message if you want
  printf("tcps_start_acq\n");
  return 1;
}


//this function stop the acquisition*
//it effectively close the socket
int stop_acq(struct tcpsacq_workspace *ws) {
  //print a message if you want
  printf("tcps_stop_acq\n");
  //close current connection
  if (ws->client_socket!=-1)
    close(ws->client_socket);
  ws->client_socket=-1;
  return 1;
}

int acquire_one_block(struct tcpsacq_workspace *ws,unsigned char *buffer,int maxsize) {
  int size;
  struct sockaddr_in cliaddr;
  socklen_t clilen;
  fd_set rset;
  struct timeval timeout;
  fd_set rfds;
  int res;
  
  if (ws->client_socket==-1) {
    //printf("accepting new client...");
    FD_ZERO(&rfds);
    FD_SET(ws->listen_socket,&rfds);
    timeout.tv_sec=0;
    timeout.tv_usec=5000;
    res=select(ws->listen_socket+1,&rfds,(fd_set *)0,(fd_set *)0,&timeout);
    if (res>0)
      ws->client_socket=accept(ws->listen_socket,(struct sockaddr *)&cliaddr,&clilen);
    else
      return 0;
  }
  if (ws->client_socket!=-1) {
    FD_ZERO (&rset);
    FD_SET (ws->client_socket,&rset);
    timeout.tv_sec=1;
    timeout.tv_usec=0;
    //printf("go to select\n");
    if (select (ws->client_socket+1,&rset,NULL,NULL,&timeout)<0) {
      perror("select");
      return 0;
    }
    if (FD_ISSET(ws->client_socket,&rset)) {
      //printf("client is there : reading\n");
      size=read(ws->client_socket,buffer,maxsize);
      if (size<=0) {
	perror("read");
	close(ws->client_socket);
	ws->client_socket=-1;
	return 0;
      } else {
	//printf("read %d bytes\n",size);
	return size;
      }
    } 
  }
  return 0;
}
