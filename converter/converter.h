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
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <dlfcn.h>
#include "math.h"
#include <pyrame.h>
#include "pyrame_converter.h"

struct event {
  char used;
  int block;
  char * time;
  char *space;
  char * data;
  struct event *next;
};

struct conv_ws {
  int streamid;
  //events struct
  struct event *current;
  int nbtbnu;
  pthread_mutex_t *evt_mutex;
  //data input
  //char *host;
  //int iport;
  //int data_socket;
  struct shbuffer *shbuf;
  //pyrame server
  int oport;
  struct netserv_client *cmd_sockets;
  //convert plugin
  char * plugin_name;
  void *lib;
  void (*convert)();
  struct convlib_ws *lws;
  //statistics
  int varmod_socket;
  //clock
  int cport;
  char * clock;
  int clock_socket;
};

//private functions prototypes
struct conv_ws * init_ws();

