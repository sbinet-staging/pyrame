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

#include "uncap_dummy.h"
#include <arpa/inet.h>

//allocate memory structure
void* init(int nb_streams,int pfid,char *pname) {
  struct uncdum_workspace *ws=malloc(sizeof(struct uncdum_workspace));
  ws->name=strdup(pname);
  ws->fid=pfid;
  printf("init uncap %s with id %d\n",ws->name,ws->fid);
  return (void *)ws;
}

//free memory structure
void deinit(void *workspace) {
  struct uncdum_workspace *ws=(struct uncdum_workspace *)workspace;
  printf("deinit %s uncap\n",ws->name);
  free(ws->name);
  free(ws);
}

//used by the acquisition to know if the packet has to be kept or not
//be careful this function is called in the critical path so be parcimonic
int prefilter(void *workspace,char * packet,int size) {
  unsigned short protocol=ntohs(*(unsigned short*)packet);
  //printf("prefilter: protocol=%d\n",protocol);
  if ((protocol==0x809) || (protocol==0x810)) {
    //printf("prefilter: control packet\n");
    return PREF_CTRL;
  }
  if (protocol==0x811) {
    //printf("prefilter: data packet\n");
    return PREF_DATA;
  }
  //printf("prefilter: junk packet\n");
  return PREF_JUNK;
}


//uncap a packet
//packet is the buffer and packet_size its size
//result is the resulting buffer and result_size its size
//loss should be set to 1 if a loss of packet has been detected
//data should be set to 1 if a data packet is detected (0 for a control packet)
//corrupted should be set to 1 if the packet is corrupted
//stream should contain the number of the stream, i.e. the dif localid
int uncap(void *workspace,char *packet,int packet_size,char ** result,int *result_size,unsigned char *loss,unsigned char *data,unsigned char *corrupted,int *stream,char *refclock) {
  struct uncdum_workspace *ws=(struct uncdum_workspace *)workspace;
  unsigned short protocol=ntohs(*(unsigned short*)packet);
  //initialization
  *corrupted=0;
  *loss=0;
  *stream=ws->fid;
  //control packet
  if ((protocol==0x809) || (protocol==0x810)) {
    *data=0;
  }  
  //data packet
  if (protocol==0x811) {
    *data=1;
  }
  *result=packet+2;
  *result_size=packet_size-2;
  //printf("uncap %s : obtain id %d\n",ws->name,ws->fid);
  return 1;
}


//this funtion decide if a packet is coherent with a set of ids 
int select_packet(void *workspace,unsigned char *packet,int id1,int id2,int id3,int id4) {
  int pkid;
  pkid=ntohs(*(unsigned short*)(packet+2));
  //printf("pkid:%d\n",pkid);
  if (pkid==id1) {
    return 1;
  } else {
    return 0;
  }
}
