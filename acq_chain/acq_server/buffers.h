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

#ifndef BUFFERS_H
#define BUFFERS_H

//128 kbuffers, 4k by buffer, 512 Mo
#define NB_GENERIC_BUFFERS 131072
#define MAX_PACKET_SIZE 4096

struct data_descriptor {
  //set by acquisition for debugging
  int acqid;

  //structure linking
  struct data_descriptor *next, *prev;
  
  //data container
  struct generic_buffer * generic_buffer;

  //acquisition unit 
  struct acqunit_workspace *auws;

  //uncap fields
  unsigned char *data;
  int data_size;
  int streamid;

  //the following id is used for consumers to know if it is their turn to treat
  //-1 means free
  int id;
  int corrupted;

} data_descriptor;

struct buffer_pool {
  struct generic_buffer *generic_buffer_head;
  pthread_mutex_t generic_buffers_mutex;
} buffer_pool;

struct data_buffer {
  struct data_buffer *next, *prev;
  unsigned char free;
  int size;
  unsigned char data[MAX_PACKET_SIZE];
} data_buffer;


struct generic_buffer {
  struct generic_buffer *next;
  int size;
  unsigned char data[MAX_PACKET_SIZE];
} generic_buffer;


struct buffer_pool *init_buffer_pool(int);
struct generic_buffer *init_generic_buffers(int);
struct generic_buffer *get_generic_buffer(struct buffer_pool * );
void leave_generic_buffer(struct buffer_pool * ,struct generic_buffer *);
struct data_descriptor* init_data_descriptor_list(int);

#endif
