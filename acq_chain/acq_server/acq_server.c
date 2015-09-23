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

#include "libacq.h"

int main(int argc,char **argv)
{
  //threads declarations
  pthread_t t_burst_detector,t_commands,t_stats;
  int port;
 
  //common workspace declarations
  struct acq_workspace *ws=malloc(sizeof(struct acq_workspace));
  memset(ws,0,sizeof(struct acq_workspace));

  //common workspace initialization
  ws->deinit=0;
  ws->initialized=0;
  ws->bsched_active=0;
  ws->ports=init_ports_table("/opt/pyrame/ports.txt");
  if (ws->ports->names==NULL || ws->ports->values==NULL) {
    printf("cant load ports table\n");
    exit(1);
  }

  //initializing the acquisition units to 0
  ws->nb_streams=0;
  ws->streams=malloc(1000*sizeof(struct stream_workspace));
  ws->acqunits=NULL;
  ws->nb_acqunits=0;

  //buffers pool init
  ws->bpool=init_buffer_pool(NB_GENERIC_BUFFERS);

  //data descriptors pool init
  ws->init_data=init_data_descriptor_list(NB_DATA_DD);
  ws->current_data=ws->init_data;
  ws->data_descriptor_mutex=malloc(sizeof(pthread_mutex_t));
  pthread_mutex_init(ws->data_descriptor_mutex,NULL);

  //control descriptors pool init
  ws->init_ctrl=init_data_descriptor_list(NB_CTRL_DD);
  ws->end_ctrl=ws->init_ctrl;
  ws->begin_ctrl=ws->init_ctrl;
  ws->ctrl_descriptor_mutex=malloc(sizeof(pthread_mutex_t));
  pthread_mutex_init(ws->ctrl_descriptor_mutex,NULL);

  //init the mutex that protect the active variable
  ws->acq_active_mutex=malloc(sizeof(pthread_mutex_t));
  pthread_mutex_init(ws->acq_active_mutex,NULL);

  //disable acquisition (equivalent to stopacq)
  ws->acq_active=0;

  if (pthread_create(&t_stats,NULL,thread_stats,ws)<0) {
    perror("pthread_create");
    exit(1);
  }
  pthread_detach(t_stats);
 
  if (pthread_create(&t_burst_detector,NULL,burst_detector,ws)<0) {
    perror("pthread_create");
    exit(1);
  }
  pthread_detach(t_burst_detector);
  
  //netserv initialization
  port=get_port("ACQ_PORT",ws->ports);
  printf("port=%d\n",port);
  if (port==0) {
    printf("error : port ACQ_PORT is not defined\n");
  }

  //creating the tcp server for the command thread
  ws->nw=start_monoport_netserv(port,50);
  ws->cmd_sockets=first_client(ws->nw);

  //init consumers chain variables
  ws->deinit_mutex=malloc(sizeof(pthread_mutex_t));
  pthread_mutex_init(ws->deinit_mutex,NULL);
  pthread_mutex_unlock(ws->deinit_mutex);

  //command thread
  if (pthread_create(&t_commands,NULL,commands,ws)<0) {
    perror("pthread_create");
    exit(1);
  }
  pthread_detach(t_commands);

  while(1) {
    usleep(100000000);
  }
  printf("all threads are done, exiting\n");
  return 0; 
}
