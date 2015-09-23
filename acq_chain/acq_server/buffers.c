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



struct generic_buffer * init_generic_buffers(int nb_buffers) {
  int i;
  struct generic_buffer *gb;
  struct generic_buffer *next;
  gb=malloc(sizeof(struct generic_buffer));
  memset(gb,0,sizeof(struct generic_buffer));
  next=gb;
  for (i=0;i<nb_buffers-1;i++) {
    gb=malloc(sizeof(struct generic_buffer));
    memset(gb,0,sizeof(struct generic_buffer));
    gb->next=next;
    next=gb;
  }
  return gb;
}

struct generic_buffer *get_generic_buffer(struct buffer_pool * pool) {
  struct generic_buffer *result;
  pthread_mutex_lock(&pool->generic_buffers_mutex);
  if (pool->generic_buffer_head!=NULL) {
    result=pool->generic_buffer_head;
    pool->generic_buffer_head=result->next;
    pthread_mutex_unlock(&pool->generic_buffers_mutex);
    return result;
  } else {
    pthread_mutex_unlock(&pool->generic_buffers_mutex);
    return NULL;
  }
}


void leave_generic_buffer(struct buffer_pool * pool,struct generic_buffer *gb) {
  pthread_mutex_lock(&pool->generic_buffers_mutex);
  gb->next=pool->generic_buffer_head;
  pool->generic_buffer_head=gb;
  pthread_mutex_unlock(&pool->generic_buffers_mutex);
}

struct buffer_pool *init_buffer_pool(int nb_bufs) {
  struct buffer_pool *result=malloc(sizeof(struct buffer_pool));
  pthread_mutex_init(&result->generic_buffers_mutex, NULL);
  result->generic_buffer_head=init_generic_buffers(nb_bufs);
  return result;
}

struct data_descriptor* init_data_descriptor_list(int nb_buffers) {
  int i;
  struct data_descriptor *result;
  struct data_descriptor *dd;
  struct data_descriptor *prev;
  result=malloc(sizeof(struct data_descriptor));
  memset(result,0,sizeof(struct data_descriptor));
  result->id=-1;
  prev=result;
  for (i=0;i<nb_buffers-1;i++) {
    dd=malloc(sizeof(struct data_descriptor));
    memset(dd,0,sizeof(struct data_descriptor));
    dd->id=-1;
    prev->next=dd;
    dd->prev=prev;
    prev=dd;
  }
  result->prev=dd;
  dd->next=result;
  return result;		
}
