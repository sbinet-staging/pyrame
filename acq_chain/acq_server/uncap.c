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

void uncap_init(struct consumer_workspace *ws) {
  //struct acq_workspace *gws=(struct acq_workspace *)ws->gws;
}

void uncap_deinit(struct consumer_workspace *ws) {
  //struct acq_workspace *gws=(struct acq_workspace *)ws->gws;
} 


void uncap_treatment(struct data_descriptor *ad,struct consumer_workspace *ws) {
  struct acq_workspace *gws=(struct acq_workspace *)ws->gws;
  unsigned char loss;
  unsigned char data;
  unsigned char corrupted;

  //printf("uncap treatment\n");
  //call the uncap lib
  (ad->auws->uncap_uncap)(ad->auws->uncapws,ad->generic_buffer->data,ad->generic_buffer->size,&ad->data,&ad->data_size,&loss,&data,&corrupted,&ad->streamid,gws->refclock);
  //printf("stream=%d\n",ad->streamid);
  if (ad->streamid>=gws->nb_streams) {
    printf("problem in localid attribution value=%d using trash instead\n",ad->streamid);
    ad->streamid=-1;
  }
  //printf("packet for streamid %d\n",ad->streamid);
  if (corrupted) {
    //printf("corrupted packet : Throwing away\n");
    ad->corrupted=1;
    set_stats(gws,NB_CORR_PKTS,SOP_PLUS,1);
  } else {
    ad->corrupted=0;
  }

  if (loss) {
    //printf("lost packet\n");
    set_stats(gws,NB_LOST_PKTS,SOP_PLUS,1);
  }

}
