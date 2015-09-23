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

#define _FILE_OFFSET_BITS 64

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <pthread.h>
#include <string.h>
#include <errno.h>

#include <sys/types.h>
#include <sys/socket.h>
#include <sys/resource.h>
#include <sys/time.h>
#include <sys/stat.h>
#include <sys/ipc.h>
#include <sys/sem.h>
#include <sys/shm.h>
#include <sys/ioctl.h>
#include <netdb.h>
#include <net/if.h>
#include <fcntl.h>
#include <math.h>
#include <expat.h>
#include <dlfcn.h>

#include "pyrame.h"



#ifndef LIBACQ_H
#define LIBACQ_H

#define ETH_P_ALL	0x0003
#define BACKLOG 100
//#define NETMAXCLIENTS 100
#define MAXID 4

//this is the global workspace of the whole acquisition chain
struct acq_workspace {
  int initialized; //0 before init_cmd, 1 after
  int nb_streams; // from init_cmd : param 0
  //acquisition units chained list
  struct acqunit_workspace *acqunits;
  int nb_acqunits;
  //threads synchronization
  unsigned char acq_active; //1 if acquisition is active
  pthread_mutex_t *acq_active_mutex;
  //reference clock
  char *refclock;
  //scheduler
  int bsched_active; //the scheduler is active or not
  unsigned char burst_state; //are we in a burst or not?
  pthread_mutex_t *burst_state_mutex;
  pthread_mutex_t **sched_clients;
  int sched_nb_clients;
  unsigned char packet_detector;
  //data descriptors
  struct data_descriptor *init_data;
  struct data_descriptor *current_data;
  pthread_mutex_t *data_descriptor_mutex;
  struct data_descriptor *init_ctrl;
  struct data_descriptor *begin_ctrl;
  struct data_descriptor *end_ctrl;
  pthread_mutex_t *ctrl_descriptor_mutex;
  struct buffer_pool *bpool;
  //netserv
  struct netserv_workspace *nw;
  //sockets
  struct netserv_client **sockets_nc;
  struct ports_table *ports;
  //shared memory
  int active_shmem;
  //files
  char * datadir; // from init_cmd : param 3
  //consumers
  int deinit;
  pthread_mutex_t *deinit_mutex;
  int endinit;
  struct consumer_workspace **consumers;

  //Raw output : fill a file with all the data from this acq unit
  int transfer_file; //raw output file
  int rawoutp_active;

  //Trash for unknown data
  int trash_file;

  //stream workspaces
  struct stream_workspace * streams;

  int autoflush_active; //flush automatically the files when autoflush_limit is reached
  int autoflush_limit; //in Mo
  int rawsize;
  pthread_mutex_t *file_mutex;
  //command module
  struct netserv_client *cmd_sockets;

  //statistics
  unsigned long long *stats;
  char **stats_name;
  int stat_socket;
  pthread_mutex_t *stat_mutex;

} acq_workspace;


struct stream_workspace {
  //output file
  int output;
  //output socket
  struct netserv_client *socket;
  //shared memory
  struct shbuffer *shdata;
  //stream id
  int id;
  //corresponding acquisition unit
  struct acqunit_workspace * acqunit;
} stream_workspace;

//this is the specific workspace for every acquisition unit
struct acqunit_workspace {
  int auid;
  //streams
  int nb_streams;
  int first_stream; // the id of the first stream of this acquisition unit
  int deinit; //put it to 1 to make the acqunit to stop its thread
  //acquisition library
  void *lib_acq;
  void * (*init_acq)();
  void (*deinit_acq)();
  void (*start_acq)();
  void (*stop_acq)();
  int (*acquire_one_block_acq)();
  //uncap library
  void *lib_uncap;
  void * (*init_uncap)();
  void (*deinit_uncap)();
  int (*prefilter_uncap)();
  int (*uncap_uncap)();
  int (*select_packet_uncap)(); 
  //stream file suffix
  char *stream_suffix;
  //acquistion plugin workspace
  void *specws;
  //uncap plugin workspace
  void *uncapws;
  //global workspace
  struct acq_workspace *globalws;
  //streams
  struct stream_workspace *streams;
  //acquisition thread
  pthread_t t_acquisition;
  //chaining 
  struct acqunit_workspace *next;
} acqunit_workspace;

//burst detector
#define OUTOFBURST 0
#define INBURST 1
#define BURST_TRESHOLD 2000 //microseconds

struct shared_cmds {
  unsigned char flush_requested;
  int flush_result;
  char *flush_prefix;
  pthread_mutex_t *flush_synchro;
} shared_cmds;

//Number of data descriptor for data and control
#define NB_DATA_DD 100000
#define NB_CTRL_DD 4096

//specific parts headers
#include "stats.h"
#include "buffers.h"
#include "consumers.h"
#include "acquisition.h"
#include "commands.h"
#include "data_socket.h"
#include "shmem.h"
#include "cache.h"
#include "scheduler.h"
#include "uncap.h"


#endif
