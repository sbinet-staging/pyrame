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

#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <dlfcn.h>
#include <time.h>


#include "../libpyrame/pyrame.h"



#ifndef CMDMOD_H
#define CMDMOD_H

#define DEBUG

#define NEXT_HOST   1
#define NEXT_PORT   2
#define NEXT_FILE   3
#define NEXT_FUNC   4
#define NEXT_IGNORE 5
#define NEXT_LPORT  6
#define NEXT_LANG   7
#define NEXT_NAME   8

#define MAX_ARGS 30

#define SUBMOD_TYPE_NONE 0
#define SUBMOD_TYPE_SCRIPT 1
#define SUBMOD_TYPE_HOST 2

struct cmdmod_ws {
  //language specific workspace
  void *lang_spec_ws;
  //global structs
  struct func_db *db;
  struct ports_table *pt;
  //storage for setres
  struct cmd_result *ret_store;
  //parsing variables
  struct function *current_function;
  int next_data;
  //parsed global params
  char * language;
  char *listen_port;
  char *mod_name;
  char * code_file_name;
  //cmod function cache
  char *cmod_ip;
  unsigned short cmod_port;
  struct cmod_obj *cmod_cache;
  //output redirecting
  int pipe_out[2];
};

//the structure describe the functions of the module as stated in xml file
struct function {
  //name of the function
  char *name;
  //type could be script(executed locally) or host(executed on another module)
  unsigned char type; //SUBMOD_TYPE_*
  //in case of host function
  char *host;
  int port;
  char *portstring;
  //in case of script function
  char *funcname;
};

struct func_db {
  struct function *func;
  struct func_db *next;
};

struct cmod_obj {
  char * command;
  int id;
  char *host;
  unsigned short port;
  struct cmod_obj *next;
};

void debug(const char *format, ...);
void output(struct cmdmod_ws *ws,const char *format, ...);
struct cmd_result * treat_cmd(struct cmd *command,void *data);
void init_func_db(struct cmdmod_ws *ws);
void add_new_func_db(struct cmdmod_ws *ws,struct function *new_func);
struct function *search_function_in_db(struct cmdmod_ws *ws,struct cmd *command);
struct cmod_obj *search_function_in_cmod(struct cmdmod_ws *ws,struct cmd *command);
struct cmod_obj *ask_cmod(struct cmdmod_ws *ws,struct cmd *command);
void print_func(struct function *func);

//language specific functions 

void *init_dummy(struct cmdmod_ws *cws);
void *init_python(struct cmdmod_ws *cws);
void *init_lua(struct cmdmod_ws *cws);
void *init_c(struct cmdmod_ws *cws);
void *init_bash(struct cmdmod_ws *cws);

int exec_command_dummy(struct cmd *command,struct function *func);
int exec_command_python(struct cmd *command,struct function *func);
int exec_command_lua(struct cmd *command,struct function *func);
int exec_command_c(struct cmd *command,struct function *func);
int exec_command_bash(struct cmd *command,struct function *func);

#endif
