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

void init_burst_detector(struct acq_workspace *ws) {
  ws->sched_clients=malloc((MAXID+1)*sizeof(pthread_mutex_t *));
  ws->sched_nb_clients=0;

  //init the mutex for burst detection
  ws->burst_state_mutex=malloc(sizeof(pthread_mutex_t));
  pthread_mutex_init(ws->burst_state_mutex,NULL);
  pthread_mutex_unlock(ws->burst_state_mutex);

  //init the burst detector
  ws->packet_detector=0;
  ws->burst_state=OUTOFBURST;
}

void deinit_burst_detector(struct acq_workspace *ws) {
  free(ws->sched_clients);
  //free the burst detector mutex
  free(ws->burst_state_mutex); 
  ws->sched_nb_clients=0;
}


void add_sched_client(struct acq_workspace *ws,pthread_mutex_t *mutex) {
  ws->sched_clients[ws->sched_nb_clients]=mutex;
  pthread_mutex_unlock(mutex);
  ws->sched_nb_clients++;
  printf("add sched client : %d\n",ws->sched_nb_clients);
}

void * burst_detector(void *args)
{
  struct acq_workspace *ws=(struct acq_workspace *)args;
  int timeinburst=0;
  int timeoutburst=0;
  int burst_counter=0; 
  //int i;

  while(1) {
    ws->packet_detector=0;
    //sleeping some time to see if a packet arrived in the meantime
    usleep(BURST_TRESHOLD);
    if (ws->bsched_active==0)
      continue;
    pthread_mutex_lock(ws->burst_state_mutex);
    if (ws->packet_detector) { //a packet arrived during my sleep
      if (ws->burst_state==OUTOFBURST) { //if out of burst
        //printf("go in burst\n");
        ws->burst_state=INBURST; //it has began
        burst_counter++;
        timeinburst=0;
        //lock all secondary threads
        /*printf("locking client mutexes\n");
        for (i=0;i<ws->sched_nb_clients;i++)
          pthread_mutex_lock(ws->sched_clients[i]);
        printf("mutexes locked\n");*/
      }
      else
        timeinburst++;
    } else { //no packet arrived during my sleep
      if (ws->burst_state==INBURST) { //if in burst
        //printf("go out burst\n");
        ws->burst_state=OUTOFBURST; // it is finished
        timeoutburst=0;
        //unlock all secondary threads
        /*printf("unlocking client mutexes\n");
        for (i=0;i<ws->sched_nb_clients;i++)
          pthread_mutex_unlock(ws->sched_clients[i]);
        printf("mutexes unlocked\n");*/
      } else {
        timeoutburst++;
        if (timeoutburst==500) { //already one second without packet : creating a false burst for sending stats
          //printf("false burst\n");
          ws->burst_state=INBURST;
        }
      }
      
    }
    pthread_mutex_unlock(ws->burst_state_mutex);
  }
}

