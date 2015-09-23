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


void shmem_init(struct consumer_workspace *ws) {

}


void opennew_shmem(struct acq_workspace *ws) {
  int i;
  for (i=0;i<ws->nb_streams;i++) {
    if (ws->streams[i].shdata==NULL) {
      ws->streams[i].shdata=open_shbuffer(i,CREATE);
    }
  }
}

 
void shmem_deinit(struct consumer_workspace *ws) {
  struct acq_workspace *gws=(struct acq_workspace *)ws->gws;
  int i;
  for (i=0;i<gws->nb_streams;i++) {
    if (gws->streams[i].shdata!=NULL) {
      close_shbuffer(gws->streams[i].shdata);
    }
  }
}



void shmem_treatment(struct data_descriptor *ad,struct consumer_workspace *ws) {
 
  struct acq_workspace *gws=(struct acq_workspace *)ws->gws;
  if (ad->streamid!=-1 && isready_shbuffer(gws->streams[ad->streamid].shdata)) {
    write_shbuffer(gws->streams[ad->streamid].shdata,(char *)ad->data,ad->data_size);
    set_stats(gws,BYTES_ON_SHM,SOP_PLUS,ad->data_size);
  }
}

