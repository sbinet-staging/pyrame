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


#include "pyrame.h"

struct netserv_client * init_netserv_client(int *control_socket, int port,int max_clients,int client_id) {
  int i;
  struct netserv_client *result;
  result=malloc(sizeof(struct netserv_client));
  result->port=port;
  result->control_socket=control_socket;
  result->max_clients=max_clients;
  result->nb_sock_client=0;
  result->sock_client=malloc(max_clients*sizeof(int));
  for (i=0;i<max_clients;i++)
    result->sock_client[i]=0;
  pthread_mutex_init(&result->mutex, NULL);
  result->client_id=client_id;
  result->initialized=0;
  return result;
}

void close_n_delete_netserv_client(struct netserv_client * client) {
  int i;
  for (i=0;i<client->nb_sock_client;i++)
    close(client->sock_client[i]);
  if (client->control_socket)
    close(*client->control_socket);
  free(client->control_socket);
  free(client->sock_client);
  free(client);
}

void print_netserv_client(struct netserv_client *client) {
  int i;
  printf("client %d on port %d\n",client->client_id,client->port);
  printf("%d/%d clients\n",client->nb_sock_client,client->max_clients);
  printf("sockets : ");
  for (i=0;i<client->max_clients;i++)
    printf("%d ",client->sock_client[i]);
  printf("\n");
  
}

void add_newfd(struct netserv_client *client,int new_fd) {
  int found;
  int i;
  pthread_mutex_lock(&client->mutex);
  //searching for a room for the new fd
  found=0;
  for (i=0;i<client->nb_sock_client;i++) {
    if (client->sock_client[i]==-1) {
      client->sock_client[i]=new_fd;
      //printf("allocate slot %d,%d\n",client->client_id,i);
      found=1;
      break;
    }
  }

  if (!found) {
    if (client->nb_sock_client==client->max_clients) {
      printf("no room left for this socket! sorry!\n");
      close(new_fd);
    } else {
      //printf("allocate slot %d,%d\n",client->client_id,client->nb_sock_client);
      client->sock_client[client->nb_sock_client]=new_fd;
      client->nb_sock_client++;
    }
  }
  if (client->control_socket)
    write(client->control_socket[1],"1",1);
  pthread_mutex_unlock(&client->mutex);
}

void open_server_socket(int *lsocket,int port) {
  struct sockaddr_in my_addr;
  int on=0;
  *lsocket=socket(AF_INET,SOCK_STREAM,0);
  setsockopt(*lsocket,SOL_SOCKET,SO_REUSEADDR,&on,sizeof(on));
  if (*lsocket==-1) {
    perror("socket");
    exit(-1);
  }
  my_addr.sin_family=AF_INET;       
  my_addr.sin_port=htons(port);  
  my_addr.sin_addr.s_addr=INADDR_ANY;
  bzero(&(my_addr.sin_zero), 8);
  if (bind(*lsocket,(struct sockaddr *)&my_addr,sizeof(struct sockaddr))==-1) {
    perror("bind");
    exit(-1);
  }
  if (listen(*lsocket,BACKLOG) == -1) {
    perror("listen");
    exit(-1);
  }
  //printf("socket setup finished on fd %d \n",*lsocket);
  }

void *netserv(void *args) {

  struct netserv_workspace *ws=(struct netserv_workspace *)args;
  struct sockaddr_in their_addr;
  socklen_t sin_size;
  int i;
  fd_set readfds;
  int highest=0;
  struct timeval tv;
  int new_fd;
  

  //printf("netserv active with delay %d\n",UCMD_DELAY);
  //printf("%d clients\n",ws->nb_clients);

  //local variables initialization
  ws->listen_sockets=malloc(NETSERV_MAX_CLIENTS*sizeof(int));
  memset(ws->listen_sockets,0,NETSERV_MAX_CLIENTS*sizeof(int));

  //waiting for connexions
  while(1) {
    //acquire the semaphore for preventing modifications during the setup
    pthread_mutex_lock(&ws->mutex);
    FD_ZERO(&readfds);
    for(i=0;i<ws->nb_clients;i++) {
      //check if client is initialized
      if (ws->clients[i]->initialized==0) {
        //printf("initializing socket for client %d\n",i);
        open_server_socket(&ws->listen_sockets[i],ws->clients[i]->port);
        if (highest<ws->listen_sockets[i]) {
          highest=ws->listen_sockets[i];
        }
        ws->clients[i]->initialized=1;
      }
      //the socket is now initialized, set it in the read set
      FD_SET(ws->listen_sockets[i],&readfds);
    }

    //prepare the delay for select
    tv.tv_sec = 0;
    tv.tv_usec = 250000;
    sin_size = sizeof(struct sockaddr_in);
    //go to select (blocking)
    if (select(highest+1, &readfds, NULL, NULL, &tv) >=0 ) {
      //return from select
      for (i=0;i<ws->nb_clients;i++)
        if (FD_ISSET(ws->listen_sockets[i], &readfds)) {
          //printf("new connexion on sockets[%d]\n",i);
          if ((new_fd = accept(ws->listen_sockets[i], (struct sockaddr *)&their_addr, &sin_size)) == -1) {
            perror("accept");
            continue;
          } else { 
            add_newfd(ws->clients[i],new_fd);
          }
        }
    }
    //leave the semaphore
    pthread_mutex_unlock(&ws->mutex);
    //printf("mutex released for select\n");
    //wait 10musec for letting add function get the semaphore if needed
    usleep(10);
  } 
}

struct netserv_workspace * start_monoport_netserv(unsigned short port,int maxclients) {
  pthread_t t_netserv;
  struct netserv_workspace *nw;
  struct netserv_client *result;
  int *control_socket = malloc(2*sizeof(int));
  nw=malloc(sizeof(struct netserv_workspace));
  if (nw==NULL) {
    perror("malloc");
    exit(1);
  }
  nw->clients=malloc(NETMAXCLIENTS*sizeof(struct netserv_client *));
  pipe(control_socket);
  result=init_netserv_client(control_socket,port,NETMAXCLIENTS,0);
  nw->maxclients=maxclients;
  pthread_mutex_init(&nw->mutex, NULL);
  nw->clients[0]=result;
  nw->nb_clients=1;
  if (pthread_create(&t_netserv,NULL,netserv,nw)!=0) {
    perror("pthread_create");
    exit(1);
  }
  return nw;
}

void display_netserv(struct netserv_workspace *nw) {
  int i;
  printf("nbclients=%d\n",nw->nb_clients);
  for(i=0;i<nw->nb_clients;i++)
    printf("%d : port %d\n",i,nw->clients[i]->port);
}

struct netserv_client * netserv_add_new_port( struct netserv_workspace *nw,unsigned short newport) {
  struct netserv_client *result;
  //acquire the semaphore
  pthread_mutex_lock(&nw->mutex);
  
  if (nw->nb_clients==nw->maxclients) {
    printf("no room left for new port\n");
    return NULL;
  }
  nw->clients[nw->nb_clients]=init_netserv_client(NULL,newport,NETMAXCLIENTS,0);
  nw->nb_clients++;
  result=nw->clients[nw->nb_clients-1];
  //leave the semaphore
  pthread_mutex_unlock(&nw->mutex);
  return result;
}

int netserv_remove_port(struct netserv_workspace *nw,unsigned short port) {
  int i,j;
  int result=0;
  //acquire the semaphore
  pthread_mutex_lock(&nw->mutex);

  for (i=0;i<nw->nb_clients;i++) {
    if (nw->clients[i]->port==port) {
      //close the corresponding listening socket
      close(nw->listen_sockets[i]);
      //fill the gap
      for (j=i;j<nw->nb_clients-1;j++) {
        nw->listen_sockets[j]=nw->listen_sockets[j+1];
      }
      //closing and freeing the founded client
      close_n_delete_netserv_client(nw->clients[i]);
      //fill the gap
      for (j=i;j<nw->nb_clients-1;j++) {
        nw->clients[j]=nw->clients[j+1];
      }
      result=1;
      break;
    }
  }
  if (result==1) {
    nw->nb_clients--;
  }
  pthread_mutex_unlock(&nw->mutex); 
  return result;
}

struct netserv_client *first_client(struct netserv_workspace *nw) {
  return nw->clients[0];
}


int send2client(struct netserv_client *clients,unsigned char * data,int size) {
  int i;
  int error;
  int nb_send=0;
  for (i=0;i<clients->nb_sock_client;i++) {
    if (clients->sock_client[i]!=-1) {
      error=write(clients->sock_client[i],data,size);
      if (error<=0) {
        printf("data_socket lost socket %d\n",i);
        close(clients->sock_client[i]);
        clients->sock_client[i]=-1;
      } else {
        nb_send++;
      }
    }
  }
  return nb_send;
}
