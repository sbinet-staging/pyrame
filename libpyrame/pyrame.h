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

#include <stdlib.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <stdio.h>
#include <netdb.h>
#include <net/if.h>
#include <sys/time.h>
#include <sys/stat.h>
#include <unistd.h>
#include <pthread.h>
#include <string.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <arpa/inet.h>
#include <sys/ipc.h>
#include <math.h>
#include <expat.h>
#include <errno.h>
#include <stdarg.h>
#include <signal.h>
#include "bindpyrame.h"

#ifndef PYRAME_H
#define PYRAME_H

#define UCMD_DELAY 2000000

#define BACKLOG 100
#define ETH_P_ALL	0x0003
#define BACKLOG 100
#define NETMAXCLIENTS 255

#define NETSERV_MAX_CLIENTS 1000

struct netserv_client {
  int *sock_client;
  int *control_socket;
  int nb_sock_client;
  int port;
  int max_clients;
  pthread_mutex_t mutex;
  int client_id;
  char initialized;
} netserv_client;

struct netserv_workspace {
  struct netserv_client **clients;
  int nb_clients;
  int reload;
  int maxclients;
  pthread_mutex_t mutex;
  int *listen_sockets;
} netserv_workspace;

struct cmdcontext {
  int socket;
  int port;
  char *host;
} cmdcontext;

//TODO allow infinite number of params
#define MAX_PARAMS 30

struct cmdcontext * init_cmdcontext(char * host,int port);
void check_for_cmd(struct cmdcontext *context,struct cmd_result *(*treat_func)(struct cmd *, void *),void *sdata);
void wait_for_cmd(struct netserv_client * clients,struct cmd_result *(*treat_func)(struct cmd *, void *),void *sdata);
struct cmd_result *parse_command(char * buf,struct cmd_result *(*treat_func)(struct cmd *, void *),void *sdata);
void free_cmd(struct cmd* tofree);
void print_cmd(struct cmd *command);
void *netserv(void *);
struct netserv_client * init_netserv_client(int*,int,int,int);
void close_n_delete_netserv_client(struct netserv_client *);
void print_netserv_client(struct netserv_client *);
struct netserv_workspace * start_monoport_netserv(unsigned short,int);
struct netserv_client * netserv_add_new_port(struct netserv_workspace *,unsigned short);
int netserv_remove_port(struct netserv_workspace *,unsigned short);
void display_netserv(struct netserv_workspace *);
struct netserv_client *first_client(struct netserv_workspace *);
int send2client(struct netserv_client *,unsigned char *,int);
struct cmd_result *get_cmd_result(int socket);
void free_cmd_result(struct cmd_result *result);
int send_result(int socket,struct cmd_result *result);
int create_from_file(char *, unsigned char *);
int is_caldata(unsigned char *);
void * create_shmem(char *,int,int);
void destroy_shmem(void *);
int create_semaphore(char *,int,unsigned char,int);
void destroy_semaphore(int);
void P(int);
void V(int);
int file_open(char *);
char * newstr(char *);
int iohtoi(char *);

#endif
