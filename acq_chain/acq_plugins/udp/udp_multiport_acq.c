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


#include "udp_multiport_acq.h"

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
struct udp_multiport_acq_workspace *init_acq(char * ports,char *param2, char *param3) {
  int i=0;
  int p=0;
  int port;
  struct udp_multiport_acq_workspace *ws=malloc(sizeof(struct udp_multiport_acq_workspace));

  //parse port expression
  ws->ports=strdup(ports);
  ws->shports=(unsigned short *)malloc(MAX_UDP_PORTS*sizeof(unsigned short));
  ws->nb_ports=0;
  //printf("parsing ports expression : %s\n",ws->ports);
  while(ws->ports[p]!=0) {
    sscanf(ws->ports+p,"%d",&port);
    printf("port=%d\n",port);
    while ((ws->ports[p]!=':') && (ws->ports[p]!=0)) {
      //printf("c=%c;",ws->ports[p]);
      p++;
    }
    if (ws->ports[p]!=0)
      p++;
    ws->shports[i]=port;
    ws->nb_ports++;
    i++;
  }
  //Allocate sockets
  ws->sockets=malloc(sizeof(int)*MAX_UDP_PORTS);
  for (i=0;i<MAX_UDP_PORTS;i++)
    ws->sockets[i]=-1;
  //print a message if you want
  printf("udp acquisition initialized with ports=%s\n",ws->ports);
  //return the workspace
  return ws;
}
 
//deinit the acquisition and destroy the specific structure
int deinit_acq(struct udp_multiport_acq_workspace *ws) {
  //stop acquisition
  stop_acq(ws);
  //destroy the specific structure
  free(ws->sockets);
  free(ws->shports);
  free(ws->ports);
  free(ws);
  //print a message if you want
  printf("udp acquisition deinitialized\n");
  //return 1 if success 0 otherwise
  return 1;
}


//this function start the acquisition
//it effectively open the socket 
int start_acq(struct udp_multiport_acq_workspace *ws) {
  int i=0;
  //print a message if you want
  printf("udp_start_acq\n");
  for(i=0;i<ws->nb_ports;i++) {
    //printf("opening port: %d\n",ws->shports[i]);
    ws->sockets[i]=open_udpsock(ws->shports[i]);
    if (ws->sockets[i]==-1) {
      return 0;
    } else {
      //printf("socket_id=%d\n",ws->sockets[i]);
    }
  }
  return 1;
}


//this function stops the acquisition
//it effectively closes the socket
int stop_acq(struct udp_multiport_acq_workspace *ws) {
  int i;
  //print a message if you want
  printf("udp_stop_acq\n");
  //close all the sockets
  for (i=0;i<MAX_UDP_PORTS;i++) {
    if (ws->sockets[i]!=-1) {
      close(ws->sockets[i]);
    }
    ws->sockets[i]=-1;
  }
  return 1;
}

int acquire_one_block(struct udp_multiport_acq_workspace *ws,unsigned char *buffer,int maxsize) {
  int size;
  fd_set socks;
  struct timeval timeout;
  static int last=0;
  int maxs=-1;
  int i;

  timeout.tv_sec = 0;
  timeout.tv_usec = 50000;
  FD_ZERO(&socks);
  for(i=0;i<ws->nb_ports;i++) {
    if (ws->sockets[i]!=-1) {
      FD_SET(ws->sockets[i],&socks);
      if (ws->sockets[i]>maxs) {
        maxs=ws->sockets[i];
      }
    }
  }

  
  size=select(maxs+1,&socks,NULL,NULL,&timeout);
  if (size<0) {
    perror("select");
    return -1;
  }
  if (size==0) {
    return 0;
  }
  
  
  //round robin for channel equity
  //we start with the following from last acquisition
  for(i=(last+1)%ws->nb_ports;i<=last+ws->nb_ports;i++) {
    i=i%ws->nb_ports;
    printf("reading %d\n",i);
    if (FD_ISSET(ws->sockets[i],&socks)){
      size=read(ws->sockets[i],buffer+2,maxsize-2);
      size+=2;
      *((unsigned short *)buffer)=htons(ws->shports[i]);
      if (size<=0) {
        printf("size=%d closing socket\n",size);
        perror("read");
        close(ws->sockets[i]);
        continue;
      } else {
        last=i;
        //printf("read: %d bytes\n",size);
        return size;
      }
    }
  }
  printf("ERROR: this should never had happened\n");
  return -1;
}
