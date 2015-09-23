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


#include "pyrame.h"

char * newstr(char *src) {
  char * result=malloc(strlen(src)+1);
  strcpy(result,src);
  return result;
}


int is_caldata(unsigned char * ethp)
{
  if (ntohs( *(unsigned short*)(ethp+12))==0x0811)
    return 1;
  return 0;
}


int file_open(char * filename) {
  int ddid;
  ddid=open(filename,O_RDONLY);
  if (ddid<0) {
    perror("open");
    exit(1);
  }
  //printf("ddid=%d\n",ddid);
  return ddid;
}

