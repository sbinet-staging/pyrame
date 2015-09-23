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

#ifndef STATS_H
#define STATS_H

//variables operations
#define SOP_PLUS 1
#define SOP_SET  2
#define SOP_MIN  3

//variables indexes
#define NB_DATA_PKTS 0
#define NB_LOST_PKTS 1
#define NB_CORR_PKTS 2
#define NB_CTRL_PKTS 3
#define BYTES_ON_DSK 4 
#define BYTES_ON_SKT 5
#define BYTES_ON_SHM 6


//variables count
#define MAX_STATS_VALUES 7
void init_stats(struct acq_workspace *,char *);
void deinit_stats(struct acq_workspace *);
void zero_stats(struct acq_workspace *);
void set_stats(struct acq_workspace *,int,int,int);
char *get_stats(struct acq_workspace *);
void *thread_stats(void *);

#endif
