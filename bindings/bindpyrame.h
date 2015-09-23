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

#include <stdio.h>
#include <netdb.h>
#include <string.h>
#include <math.h>
#include <expat.h>
#include <stdarg.h>
#include <signal.h>
#include <unistd.h>
#include <sys/sem.h>
#include <sys/shm.h>
#include <sys/time.h>
#include <errno.h>

#ifndef BINDPYRAME_H
#define BINDPYRAME_H




//************************ BASIC API ***********************

struct ports_table {
  char **names;
  int *values;
  int nb_ports;
};

struct cmd {
  char *name;
  int nb_params;
  char **params;
};

struct cmd_result {
  int retcode;
  char *str;
};

int open_socket(char * host, int port);

// PORTS FUNCTIONS
struct ports_table *init_ports_table(char * filename);
void free_ports_table(struct ports_table *table);
int get_port(char *name,struct ports_table *table);
char * extract_port_name(char * func_name);

// COMMAND CONVERSION FUNCTIONS
char * args_2_strcmd(char * func_name,va_list arg);
char * cmd_2_strcmd(struct cmd *command);


// SEND COMMAND FUNCTIONS 
struct cmd_result *sendcmd(char * host,int port,char * func_name,...);
struct cmd_result *send_cmd(char * host,int port,struct cmd *command);
struct cmd_result *send_strcmd(char * host,int port,char * strcmd);


// EXEC COMMAND FUNCTIONS
struct cmd_result *execcmd(int socket,char * func_name,...);
struct cmd_result *exec_cmd(int socket,struct cmd *command);
struct cmd_result *exec_strcmd(int socket,char * strcmd);

// RESULT FUNCTIONS
struct cmd_result *get_cmd_result(int socket);
void free_cmd_result(struct cmd_result *result);



//******************* SHBUFFERS **********************



#define SHARED_BUFFER_SIZE 8192

struct shbuffer {
  int full_semid;
  int empty_semid;
  int mutex_semid;
  int ready_semid;
  int shmid;
  char * shdata;
  int flushed;
  int tmp_size;
  char *tmp;
  int data_size;
};

#define CREATE 1
#define NO_CREATE 0

struct shbuffer * open_shbuffer(int streamid,int create);
void close_shbuffer(struct shbuffer *shbuf);
int read_shbuffer(struct shbuffer *shbuf,char *buffer);
int write_shbuffer(struct shbuffer *shbuf,char *buffer,int size);
int isready_shbuffer(struct shbuffer *shbuf);
void ready_shbuffer(struct shbuffer *shbuf);
void unready_shbuffer(struct shbuffer *shbuf);



//************************** INCR_STRING FUNCTIONS ***********

struct incr_string {
  char * str;
  int alloc_size;
  int size;
};

struct incr_string *new_incr_string(void);
void suffix_incr_string(struct incr_string *res,char * addstr);
void free_incr_string(struct incr_string *res);

#endif
