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


#ifndef CONSUMERS_H
#define CONSUMERS_H

struct consumer_workspace {
  struct acq_workspace *gws;
  int myid;
  void (*myinit)();
  void (*mydeinit)();
  void (*mytreatment)();
  struct data_descriptor *init_descriptor;
  char *name;
  pthread_t mythread;
  int cons_pipe[2];
} consumer_workspace;


void *generic_consumer(void *);
void destructor_init(struct consumer_workspace *);
void destructor_deinit(struct consumer_workspace *);
void destructor_treatment(struct data_descriptor *,struct consumer_workspace *);
void launch_consumer_chain(struct acq_workspace *);
void stop_consumer_chain(struct acq_workspace *);

#endif
