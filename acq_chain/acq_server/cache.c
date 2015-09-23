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


void open_files(struct acq_workspace *ws) {
  int i;
  char name[4096];
  sprintf(name,"%s/running_data.ethraw",ws->datadir);
  ws->transfer_file=open(name,O_WRONLY|O_CREAT|O_TRUNC,0666);
  if (ws->transfer_file==-1)
      perror("cant open ethraw file");
  sprintf(name,"%s/running_trash_data.raw",ws->datadir);
  ws->trash_file=open(name,O_WRONLY|O_CREAT|O_TRUNC,0666);
  if (ws->trash_file==-1)
      perror("cant open trash file");
  for (i=0;i<ws->nb_streams;i++) {
    sprintf(name,"%s/running_data_%s%d.raw",ws->datadir,ws->streams[i].acqunit->stream_suffix,i);
    ws->streams[i].output=open(name,O_WRONLY|O_CREAT|O_TRUNC,0666);
    if (ws->streams[i].output==-1)
      perror("cant open output");
  }
}

void opennew_files(struct acq_workspace *ws) {
int i;
  char name[4096];
  printf("opennewfiles for nb_streams=%d\n",ws->nb_streams);
  for (i=0;i<ws->nb_streams;i++) {
    sprintf(name,"%s/running_data_%s%d.raw",ws->datadir,ws->streams[i].acqunit->stream_suffix,i);
    if (ws->streams[i].output==-1) {
      printf("open file %s for i=%d\n",name,i);
      ws->streams[i].output=open(name,O_WRONLY|O_CREAT|O_TRUNC,0666);
      if (ws->streams[i].output==-1)
        perror("cant reopen output files");
    } else {
      printf("error : file %d should be closed but is open\n",i);
    }
  }
}


void close_files(struct acq_workspace *ws) {
  int i;
  if (ws->transfer_file!=-1)
    close(ws->transfer_file);
  ws->transfer_file=-1;
  if (ws->trash_file!=-1)
    close(ws->trash_file);
  ws->trash_file=-1;
  for (i=0;i<ws->nb_streams;i++) {
    if (ws->streams[i].output!=-1)
      close(ws->streams[i].output); 
    ws->streams[i].output=-1;
  }
}

void move_files(char *prefix,struct acq_workspace *ws) {
  int i;
  char scommand[8000];
  char name1[4096];
  char name2[4096];
  //moving raw output file
  if (ws->rawoutp_active) {
  sprintf(scommand,"mv %s/running_data.ethraw %s/%s.ethraw",ws->datadir,ws->datadir,prefix);
  system(scommand);
  }
  //moving trash file
  sprintf(scommand,"mv %s/running_trash_data.raw %s/%s_trash.raw",ws->datadir,ws->datadir,prefix);
  system(scommand);
  //moving stream files
  for (i=0;i<ws->nb_streams;i++) {
    sprintf(name1,"%s/running_data_%s%d.raw",ws->datadir,ws->streams[i].acqunit->stream_suffix,i);
    sprintf(name2,"%s/%s_%s%d.raw",ws->datadir,prefix,ws->streams[i].acqunit->stream_suffix,i);
    sprintf(scommand,"mv %s %s",name1,name2);
    system(scommand);
  }
}
  

void flush_files(char * prefix,struct acq_workspace *ws) {

  printf("flushing and renaming cache file\n");
  pthread_mutex_lock(ws->file_mutex);
  close_files(ws);
  move_files(prefix,ws);
  open_files(ws);
  pthread_mutex_unlock(ws->file_mutex);
  printf("end of flush files\n");
}

void cache_init(struct consumer_workspace *ws) {
  struct acq_workspace *gws=(struct acq_workspace *)ws->gws;
  gws->file_mutex=malloc(sizeof(pthread_mutex_t));
  pthread_mutex_init(gws->file_mutex,NULL);
  open_files(gws);
}

void cache_deinit(struct consumer_workspace *ws) {
  struct acq_workspace *gws=(struct acq_workspace *)ws->gws;
  close_files(gws);
  free(gws->file_mutex);
}

//This is the treatment done on every data packet to store data in files
void cache_treatment(struct data_descriptor *ad,struct consumer_workspace *ws) {
  struct acq_workspace *gws=(struct acq_workspace *)ws->gws;
  int stream=ad->streamid;
  int res;
  
  //take the mutex to avoid write while flushing
  pthread_mutex_lock(gws->file_mutex);

  //if necessary save the raw data
  if (gws->rawoutp_active) 
    if (gws->transfer_file>0) {
      //write the size of the packet in the ethraw   
      write(gws->transfer_file,&ad->generic_buffer->size,sizeof(int));
      //write the packet in ethraw
      write(gws->transfer_file,ad->generic_buffer->data,ad->generic_buffer->size);
    }
  
  if (stream==-1) { //goto trash
    if (gws->trash_file>0) {
      write(gws->trash_file,ad->generic_buffer->data,ad->generic_buffer->size);
      set_stats(gws,BYTES_ON_DSK,SOP_PLUS,ad->data_size);
    }

  } else { //normal file writing
    if (gws->streams[stream].output>0) { //write data in specific bystream file
      res=write(gws->streams[stream].output,ad->data,ad->data_size);
      if (res==0)
        printf("nothing written\n");
      if (res==-1) {
        perror("write");
      }
      if (res>0) {
        set_stats(gws,BYTES_ON_DSK,SOP_PLUS,ad->data_size);
      }
    } else {
        printf("Data should be written but file is closed\n");
    }
  }
  
  pthread_mutex_unlock(gws->file_mutex);

  //autoflush
  if ((gws->autoflush_active) && (gws->rawsize>gws->autoflush_limit*1024*1024)) {
    printf("autoflush\n");
    flush_files("auto_flush",gws);
    set_stats(gws,BYTES_ON_DSK,SOP_SET,0);
  }

}

