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


void init_acquisition(struct acq_workspace *ws,char *datadir) {

  //init the data store folder
  ws->datadir=strdup(datadir);

  //init the reference clock
  ws->refclock=malloc(4096*sizeof(char));
  strcpy(ws->refclock,"noclock");

}


void deinit_acquisition(struct acq_workspace *ws) {
  struct acqunit_workspace *au,*autmp;

  //stop the acquisition if necessary
  if (ws->acq_active==1) {
    printf("stop acquisition\n");
    ws->acq_active=0;
    //wait for data to be treated
    usleep(50000);
  }

  //send the order to exit for every acq threads
  printf("send exit order to acqunit threads\n");
  au=ws->acqunits;
  while(au!=NULL) {
    au->deinit=1;
    au=au->next;
  }

  //wait for threads to exit
  usleep(2000000);
  
  //free the structures
  au=ws->acqunits;
  while(au!=NULL) {
    autmp=au;
    au=au->next;
    free_acq_unit(autmp);
  }
  ws->nb_acqunits=0;
  ws->acqunits=NULL;

  free(ws->datadir);
  free(ws->refclock);
  printf("deinit_acquisition done\n");
}

void start_acquisition(struct acq_workspace *ws) {
  pthread_mutex_lock(ws->acq_active_mutex);
  ws->acq_active=1;
  pthread_mutex_unlock(ws->acq_active_mutex);
}


void stop_acquisition(struct acq_workspace *ws) {
  pthread_mutex_lock(ws->acq_active_mutex);
  ws->acq_active=0;
  ws->packet_detector=0;
  ws->burst_state=OUTOFBURST;
  pthread_mutex_unlock(ws->acq_active_mutex);
}

int get_acqstate(struct acq_workspace *ws) {
  int active;
  pthread_mutex_lock(ws->acq_active_mutex);
  active=ws->acq_active;
  pthread_mutex_unlock(ws->acq_active_mutex);
  return active;
}


void print_packet(struct generic_buffer *acq_buffer) {
  int i;
  for(i=0;i<acq_buffer->size;i++)
    printf("%x ",acq_buffer->data[i]);
  printf("\n");
}

void read_error(struct acq_workspace *ws) {
  printf("read error : stoping acquisition\n");
  pthread_mutex_lock(ws->acq_active_mutex);
  ws->acq_active=0;
  pthread_mutex_unlock(ws->acq_active_mutex);
}

void *load_func(void *lib,const char * name) {
  void (*func)();
  func=dlsym(lib,name);
  if (func==NULL) {
    printf("cant load init func : %s\n",dlerror());
    exit(1);
  }
  return func;
}

struct acqunit_workspace * make_acq_unit(int nb_streams,int first_stream,char * acq_lib,char * uncap_lib,char * stream_suffix,struct acq_workspace *ws) {
  struct acqunit_workspace * result=malloc(sizeof(struct acqunit_workspace));

  result->nb_streams=nb_streams;
  result->first_stream=first_stream;
  result->deinit=0;
  
  //fill the pointer with the acquisition library functions
  result->lib_acq=dlopen(acq_lib,RTLD_NOW|RTLD_LOCAL);
  if (!result->lib_acq) {
    printf("dlopen error : %s\n",dlerror()); 
    free(result);
    return NULL;
  }
  //fill the pointer with the uncap library functions
  result->lib_uncap=dlopen(uncap_lib,RTLD_NOW|RTLD_LOCAL);
  if (!result->lib_uncap) {
    printf("dlopen error : %s\n",dlerror()); 
    dlclose(result->lib_acq);
    free(result);
    return NULL;
  }
  result->init_acq=load_func(result->lib_acq,"init_acq");
  result->deinit_acq=load_func(result->lib_acq,"deinit_acq");
  result->start_acq=load_func(result->lib_acq,"start_acq");
  result->stop_acq=load_func(result->lib_acq,"stop_acq");
  result->acquire_one_block_acq=load_func(result->lib_acq,"acquire_one_block");
 
  result->init_uncap=load_func(result->lib_uncap,"init");
  result->deinit_uncap=load_func(result->lib_uncap,"deinit");
  result->prefilter_uncap=load_func(result->lib_uncap,"prefilter");
  result->uncap_uncap=load_func(result->lib_uncap,"uncap");
  result->select_packet_uncap=load_func(result->lib_uncap,"select_packet");
  
  result->stream_suffix=strdup(stream_suffix);
  result->globalws=ws;
  return result;
}


void free_acq_unit(struct acqunit_workspace * au) {
  dlclose(au->lib_acq);
  dlclose(au->lib_uncap);
  free(au->streams);
  free(au->stream_suffix);
  free(au);
}

int insert_new_data_descriptor(struct acq_workspace *ws,struct generic_buffer *acq_buffer,struct acqunit_workspace *auws,int acqid) {
  pthread_mutex_lock(ws->data_descriptor_mutex);
  if (ws->current_data->id<0) {
    //filling a data descriptor
    ws->current_data->generic_buffer=acq_buffer;
    //assign the acquisition unit workspace to this packet
    ws->current_data->auws=auws;
    ws->current_data->acqid=acqid;
    //set the id to the first consumer
    ws->current_data->id=MAXID;
    //going to the next descriptor
    ws->current_data=ws->current_data->next;
    //set statistics
    set_stats(ws,NB_DATA_PKTS,SOP_PLUS,1);
    pthread_mutex_unlock(ws->data_descriptor_mutex);
    return 1;
  } else {
    printf("no data descriptor available\n");
    leave_generic_buffer(ws->bpool,acq_buffer);
    set_stats(ws,NB_LOST_PKTS,SOP_PLUS,1);
    pthread_mutex_unlock(ws->data_descriptor_mutex);
    return 0;
  }
}


int insert_new_ctrl_descriptor(struct acq_workspace *ws,struct generic_buffer *acq_buffer,struct acqunit_workspace *auws) {
  pthread_mutex_lock(ws->ctrl_descriptor_mutex);
  ws->end_ctrl->generic_buffer=acq_buffer;
  ws->end_ctrl->id=1;
  ws->end_ctrl->auws=auws;
  ws->end_ctrl=ws->end_ctrl->next;
  if (ws->end_ctrl==ws->begin_ctrl) {
    //printf("dropping an old packet\n");
    leave_generic_buffer(ws->bpool,ws->begin_ctrl->generic_buffer);
    ws->begin_ctrl=ws->begin_ctrl->next;
  } 
  set_stats(ws,NB_CTRL_PKTS,SOP_PLUS,1); 
  pthread_mutex_unlock(ws->ctrl_descriptor_mutex);
  return 1;
}


void *acquisition(void *args)
{
  struct acqunit_workspace *auws=(struct acqunit_workspace *)args;
  struct acq_workspace *ws=auws->globalws;
  int active;
  int localactive=0;
  int size;
  int res;
  int acqid=0;
  unsigned char packet[1024];
  struct generic_buffer *acq_buffer;
  
  //infinite loop
  while(1) {

    //if deinit is engaged, stop the thread
    if (auws->deinit==1) {
      printf("acquisition deinit order detected\n");
      break;
    }

    //do nothing until being initialized
    while (ws->initialized!=1) 
      usleep(50000);

    //get the flag to see if the acquisition should be active or not
    pthread_mutex_lock(ws->acq_active_mutex);
    active=ws->acq_active;
    pthread_mutex_unlock(ws->acq_active_mutex);
    //compare with reality
    if (active!=localactive) {
      printf("active=%d localactive=%d\n",active,localactive);
      //if necessary do the action corresponding to the flag
      if (!active) {
        (auws->stop_acq)(auws->specws);
        localactive=0;
        usleep(2000);
        continue;
      } else {
        (auws->start_acq)(auws->specws);
        localactive=1;
      }
    }
    //if not active just wait
    if (!active) {
      usleep(2000);
      continue;
    }

    //acquisition part
    //find a free buffer
    acq_buffer=get_generic_buffer(ws->bpool);
    if (acq_buffer!=NULL) {
      size=(auws->acquire_one_block_acq)(auws->specws,acq_buffer->data,MAX_PACKET_SIZE);
      //printf("size=%d\n",size);
      if (size<0) {
        printf("acquire_one_block returns %d\n",size);
        read_error(ws);
        leave_generic_buffer(ws->bpool,acq_buffer);
        continue;
      }
      if (size==0) {
        leave_generic_buffer(ws->bpool,acq_buffer);
        continue;
      }
      acq_buffer->size=size;
      //the acquisition is done : call prefilter to know if it is junk,data or control
      res=(auws->prefilter_uncap)(auws->uncapws,acq_buffer->data,acq_buffer->size);
      switch (res) {
      case PREF_JUNK: 
        //drop junk packet
        //printf("treating junk packet\n");
        leave_generic_buffer(ws->bpool,acq_buffer);
        break;
      case PREF_DATA: 
        //warn the scheduler that we go into a bunch of acquisition
         ws->packet_detector=1;
        //give the data packet to the consumers chain
        //printf("treating data packet\n");
        insert_new_data_descriptor(ws,acq_buffer,auws,acqid);
        acqid++;
        //awake the first consumer
        write(ws->consumers[MAXID]->cons_pipe[1],"1",1);
        break;
      case PREF_CTRL: 
        //store the control packet in a circular buffer pool
        //printf("treating ctrl packet\n");
        insert_new_ctrl_descriptor(ws,acq_buffer,auws);
        break;
      default: //should never happen
        printf("problem with prefilter : return value = %d\n",res);
        leave_generic_buffer(ws->bpool,acq_buffer);
      }
    } else { //no room left
      printf("bufferpool is full\n");
      size=(auws->acquire_one_block_acq)(auws->specws,packet,4096);
      if (size<0) {
        printf("acquire_one_block returns %d\n",size);
        read_error(ws);
      }
      set_stats(ws,NB_LOST_PKTS,SOP_PLUS,1);
    } 
  }
  usleep(500000);
  auws->deinit_uncap(auws->uncapws);
  auws->deinit_acq(auws->specws);
  printf("exiting the acquisition thread\n");
  return NULL;
}
