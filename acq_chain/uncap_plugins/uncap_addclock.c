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
  printf("deinit dummy uncap %s\n",ws->name);
  free(ws);
}

//used by the acquisition to know if the packet has to be kept or not
//be careful this function is called in the critical path so be parcimonic
int prefilter(void *workspace,char * packet,int size) {
  return PREF_DATA;
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
  int i;
  //initialization
  *corrupted=0;
  *loss=0;
  *data=1;
  *stream=ws->fid;
  *result=packet;
  //printf("packet size=%d\n",packet_size);
  packet[packet_size]=0;
  for (i=0;i<packet_size;i++)
    if (packet[i]=='\n') {
      packet[i]=' ';
      strcpy(packet+i+1,refclock);
      packet[i+1+strlen(refclock)]='\n';
      packet[i+2+strlen(refclock)]=0;
      //printf("final packet=%s\n",packet);
      *result_size=packet_size+strlen(refclock)+1;
      //printf("CR detected : inserting clock (size=%d)\n",*result_size);
      return 1;
    }
  //printf("no clock inserted (size=%d)\n",packet_size);
  *result_size=packet_size;
  //printf("uncap %s : obtain id %d\n",ws->name,ws->fid);
  return 1;
}


//this funtion decide if a packet is coherent with a set of ids 
int select_packet(void *workspace,unsigned char *packet,int id1,int id2,int id3,int id4) {
  return 0;
}
