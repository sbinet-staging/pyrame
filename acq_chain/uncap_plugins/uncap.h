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

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef UNCAP_H
#define UNCAP_H

//called once by the initialization of the acquisition chain
//params are : nb_streams
void* init(int nb_streams,int fid,char * plugin_name); 

void deinit(void * workspace);

#define PREF_JUNK 0
#define PREF_DATA 1
#define PREF_CTRL 2
//used by the acquisition to know if the packet has to be kept or not
//be careful this function is called in the critical path so be parcimonic
//params are : packet,packet_size
//return is the constant of the type of the packet (junk,data or control)
int prefilter(void * workspace,char *packet,int size); 


//called for uncapping every data or control packet
//this function is called outside critical path
int uncap(void * workspace,char * packet,int packet_size,char ** result,int * result_size,unsigned char *loss,unsigned char *data,unsigned char *corrupted,int *stream,char *refclock); 

//called for selecting packets on five arbitrary ids
//the first param is the packet itself
//all other params are the ids
//any implementation use the id has it wants
int select_packet(void *workspace,unsigned char *packet,int id1,int id2,int id3,int id4);

#endif
