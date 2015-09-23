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


#include "noacq_acq.h"



//this function should initialize acquisition
//it should allocate and fill the specific structure
struct noacq_workspace* init_acq(char * param1,char *param2, char *param3) {
  
  //allocate and fill the workspace
  struct noacq_workspace *ws=malloc(sizeof(struct noacq_workspace));
  //print a message if you want
  printf("noacq acquisition initialized \n");
  //return the workspace
  return ws;
}
 
//deinit the acquisition and destroy the specific structure
int deinit_acq(struct noacq_workspace *ws) {
  //destroy the specific structure
  free(ws);
  //print a message if you want
  printf("noacq server acquisition deinitialized\n");
  //return 1 if success 0 otherwise
  return 1;
}


//this function start the acquisition
int start_acq(struct noacq_workspace *ws) {
  //print a message if you want
  printf("noacq_start_acq\n");
  return 1;
}


//this function stop the acquisition*
//it effectively close the socket
int stop_acq(struct noacq_workspace *ws) {
  //print a message if you want
  printf("noacq_stop_acq\n");
  return 1;
}

int acquire_one_block(struct noacq_workspace *ws,unsigned char *buffer,int maxsize) {
    return 0;
}
