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


#include "file_acq.h"

//this function should initialize acquisition
//it should allocate and fill the specific structure
struct fileacq_workspace * init_acq(char * filename,char * tempo, char *param3) {
  struct fileacq_workspace *ws=malloc(sizeof(struct fileacq_workspace));
  //param 1 should be the file name
  ws->filename=strdup(filename);
  //param 2 is a temporization in microseconds
  ws->tempo=atoi(tempo);
  //do whatever needed to initialized
  ws->fd=-1;
  //print a message if you want
  printf("file acquisition initialized with filename=%s\n",ws->filename);
  return ws;
}
 
//deinit the acquisition and destroy the specific structure
int deinit_acq(struct fileacq_workspace *ws) {
  //deinit the acquisition
  if (ws->fd!=-1)
    close(ws->fd);
  ws->fd=-1;
  //destroy the specific structure
  free(ws->filename);
  free(ws);
  //print a message if you want
  printf("file acquisition deinitialized\n");
  //return 1 if success 0 otherwise
  return 1;
}


//this function start the acquisition
//it effectively open the fd 
int start_acq(struct fileacq_workspace *ws) {
  //print a message if you want
  printf("file_start_acq\n");
  //in file we connect the fd to a simple txt file
  ws->fd=open(ws->filename,O_RDONLY);
  if (ws->fd==-1) {
    perror("open");
    return 0;
  } else
    printf("fd_id=%d\n",ws->fd);
  return 1;
}


//this function stop the acquisition*
//it effectively close the fd
int stop_acq(struct fileacq_workspace *ws) {
  //print a message if you want
  printf("file_stop_acq\n");
  //disconnect 
  close(ws->fd);
  ws->fd=-1;
  return 1;
}

int acquire_one_block(struct fileacq_workspace *ws,unsigned char *buffer,int maxsize) {
  int wsize;
  int size;
  char *trash_buf;
  if (ws->fd!=-1) {
    read(ws->fd,&wsize,sizeof(int));
    if (wsize>maxsize) {
      printf("Error : the size from the file %d is bigger than maxsize %d\n",wsize,maxsize);
      trash_buf=(char *)malloc(wsize*sizeof(char));
      size=read(ws->fd,trash_buf,wsize);
      free(trash_buf);
      return -1;
    }
    //printf("reading the fd %d\n",ws->fd);
    size=read(ws->fd,buffer,wsize);
    if (size<=0) {
      printf("size=%d\n",size);
      perror("read");
      return -1;
    }
    usleep(ws->tempo);
    return size;
  } else {
    return -1;
  }
}
