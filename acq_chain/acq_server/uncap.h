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

#ifndef UNCAP_H
#define UNCAP_H

#define PREF_JUNK 0
#define PREF_DATA 1
#define PREF_CTRL 2

void uncap_init(struct consumer_workspace *);
void uncap_deinit(struct consumer_workspace *);
void uncap_treatment(struct data_descriptor *,struct consumer_workspace *);

#endif
