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


//the generic consumer is a generic code from the distribution bus system
void *generic_consumer(void *args) {

  struct consumer_workspace *ws=(struct consumer_workspace *)args;
  struct acq_workspace *gws=(struct acq_workspace *)ws->gws;
  unsigned char bs=0;
  struct data_descriptor *active_descriptor=ws->init_descriptor;
  fd_set wake_pipe;
  char buf[2];
  struct timeval timeout;
  int dres;

  printf("%s active\n",ws->name);

  //calling the specific init part of the consumer
  ws->myinit(ws);

  //we set this variable to allow the consumer chain to allocate the next one
  gws->endinit=1;

  //infinite loop
  while(1) {
  
    //look for deinit
    if (gws->deinit>0) {
      ws->mydeinit(ws);
      pthread_mutex_lock(gws->deinit_mutex);
      gws->deinit--;
      pthread_mutex_unlock(gws->deinit_mutex);
      return NULL;
    }

    //the consumer is looking if it is allowed to work (in respect to the burst scheduling)
    pthread_mutex_lock(gws->burst_state_mutex);
    bs=gws->burst_state;
    pthread_mutex_unlock(gws->burst_state_mutex);
    if (bs==OUTOFBURST) { //the scheduler allow secondary threads to work
      //looking for a packet to treat
      if (active_descriptor->id!=ws->myid) { //nothing to do
        if (ws->myid!=0) {
          write(gws->consumers[ws->myid-1]->cons_pipe[1],"1",1);
          //printf("unlocked %s\n",gws->consumers[ws->myid-1]->name);
        }
        FD_ZERO(&wake_pipe);
        FD_SET(ws->cons_pipe[0],&wake_pipe);
	timeout.tv_sec=0;
	timeout.tv_usec=4000;
        //printf("waiting for data on %s\n",ws->name);
        dres=select(ws->cons_pipe[0]+1,&wake_pipe,NULL,NULL,&timeout);
        //printf("got data on %s\n",ws->name);
        if (dres>0)
	  read(ws->cons_pipe[0],buf,1);
        //printf("read data on %s\n",ws->name);
      } else {

        if (active_descriptor->corrupted==0) {
          //printf("%s is treating packet %d\n",ws->name,active_descriptor->acqid);
          //treating the packet
          ws->mytreatment(active_descriptor,ws);

        }

        //pass to next packet
        active_descriptor->id--;
        active_descriptor=active_descriptor->next;
      }
    } else {
      usleep(4000);
    } 
  }
}

void destructor_init(struct consumer_workspace *ws) {
  struct acq_workspace *gws=(struct acq_workspace *)ws->gws;
  printf("destructor for %d streams\n",gws->nb_streams);
}

void destructor_deinit(struct consumer_workspace *ws) {
  //struct acq_workspace *gws=(struct acq_workspace *)ws->gws;
  //printf("destructor deinit\n");
}

void destructor_treatment(struct data_descriptor *ad,struct consumer_workspace *ws) {
  struct acq_workspace *gws=(struct acq_workspace *)ws->gws;
  leave_generic_buffer(gws->bpool,ad->generic_buffer);
}



void launch_consumer_chain(struct acq_workspace *ws) {
  int i;
  char *name[MAXID+1]={"destructor","data_sock","shmem","cache","uncap"};
  void (*func_init[MAXID+1])(struct consumer_workspace *)={destructor_init,data_socket_init,shmem_init,cache_init,uncap_init};
  void (*func_deinit[MAXID+1])(struct consumer_workspace *)={destructor_deinit,data_socket_deinit,shmem_deinit,cache_deinit,uncap_deinit};
  void (*func_treatment[MAXID+1])(struct data_descriptor *,struct consumer_workspace *)={destructor_treatment,data_socket_treatment,shmem_treatment,cache_treatment,uncap_treatment};

  ws->consumers=(struct consumer_workspace **)malloc((MAXID+1)*sizeof(struct consumer_workspace*));

  printf("launch_consumer_chain for %d streams\n",ws->nb_streams);

  for(i=0;i<=MAXID;i++) {
    ws->consumers[i]=malloc(sizeof(struct consumer_workspace));
    printf("launching customer %s with id %d\n",name[i],i);
    ws->consumers[i]->name=strdup(name[i]);
    ws->consumers[i]->myid=i;
    ws->consumers[i]->myinit=func_init[i];
    ws->consumers[i]->mydeinit=func_deinit[i];
    ws->consumers[i]->mytreatment=func_treatment[i];
    ws->consumers[i]->init_descriptor=ws->current_data;
    pipe(ws->consumers[i]->cons_pipe);
    ws->consumers[i]->gws=ws;
    ws->endinit=0;
    if (pthread_create(&(ws->consumers[i]->mythread),NULL,generic_consumer,ws->consumers[i])!=0) {
      perror("pthread_create");
      exit(1);
    }
    pthread_detach(ws->consumers[i]->mythread);
    while(!ws->endinit)
      usleep(100);
  }
}

void stop_consumer_chain(struct acq_workspace *ws) {
  int i;
  printf("stop_consumer_chain\n");
  ws->deinit=MAXID+1;
  while(ws->deinit!=0)
    //printf("waiting %d\n",ws->deinit);
    usleep(10000);
  for (i=0;i<=MAXID;i++) {
    close(ws->consumers[i]->cons_pipe[0]);
    close(ws->consumers[i]->cons_pipe[1]);
    free(ws->consumers[i]->name);
    free(ws->consumers[i]);
  }
  free(ws->consumers);
  display_netserv(ws->nw);
  printf("consumer chain stopped\n");
}
