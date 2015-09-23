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

#ifndef ACQ_H
#define ACQ_H

void *acquisition(void *);
void init_acquisition(struct acq_workspace *,char *);
void deinit_acquisition(struct acq_workspace *);
struct acqunit_workspace * make_acq_unit(int,int,char *,char *,char *,struct acq_workspace *);
void free_acq_unit(struct acqunit_workspace *);
void start_acquisition(struct acq_workspace *);
void stop_acquisition(struct acq_workspace *);
int get_acqstate(struct acq_workspace *);
int insert_new_data_descriptor(struct acq_workspace *,struct generic_buffer *,struct acqunit_workspace *,int);

#endif
