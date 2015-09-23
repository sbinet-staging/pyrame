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

void data_socket_init(struct consumer_workspace *ws) {
  sigset_t sigpipe_mask;
  sigemptyset(&sigpipe_mask);
  sigaddset(&sigpipe_mask, SIGPIPE);
  sigset_t saved_mask;
  if (pthread_sigmask(SIG_BLOCK, &sigpipe_mask, &saved_mask) == -1) {
    perror("pthread_sigmask");
    exit(1);
  }
}

void opennew_socket(struct acq_workspace *ws) {
  int i;
  int port;
  for (i=0;i<ws->nb_streams;i++) {
    if (ws->streams[i].socket==NULL) {
      port=get_port("STREAMBASE_PORT",ws->ports)+i;
      printf("adding socket for stream %d on port %d\n",i,port);
      ws->streams[i].socket=netserv_add_new_port(ws->nw,port);
    }
    if (ws->streams[i].socket==NULL) {
      printf("cant add new port to netserv\n");
      exit(1);
    }
 }
}

void data_socket_deinit(struct consumer_workspace *ws) {
  int i;
  struct acq_workspace *gws=(struct acq_workspace *)ws->gws;
  
  for (i=0;i<=gws->nb_streams;i++) {
    netserv_remove_port(gws->nw,get_port("STREAMBASE_PORT",gws->ports)+i);
  }
}

void data_socket_treatment(struct data_descriptor *ad,struct consumer_workspace *ws) {
  int nb_send;
  struct acq_workspace *gws=(struct acq_workspace *)ws->gws;
  //printf("data_socket treatment\n");
  if (ad->streamid!=-1) {
    nb_send=send2client(gws->streams[ad->streamid].socket,ad->data,ad->data_size);
    //printf("nb_send=%d\n",nb_send);
    set_stats(gws,BYTES_ON_SKT,SOP_PLUS,nb_send*ad->data_size);
  }
}

