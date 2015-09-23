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

#include "../bindpyrame.h"

int main() {
  struct cmd_result *result;
  struct ports_table *table;
  int port;
  int i;
  int sockid;
  int ires;

  table = init_ports_table("/opt/pyrame/ports.txt");
  if (table->names == NULL || table->values == NULL) { return -1; }
  port = get_port("TEST_PORT",table);
  if (port == -1) {
    printf("Error getting port number\n");
    return -1;
  }
  free_ports_table(table);

// SENDCMD
  result = sendcmd("localhost",port,"twoargs_test","arg1","arg2","end");
  printf("sendcmd: retcode=%d res=%s\n",result->retcode,result->str);
  if (result->retcode==1) {
    ires=0;
  } else {
    ires=1;
  }
  
  //free the result
  free_cmd_result(result);

// EXECCMD
  sockid = open_socket("localhost",port);
  result = execcmd(sockid,"twoargs_test","arg1","arg2","end");
  close(sockid);
  printf("execcmd: retcode=%d res=%s\n",result->retcode,result->str);
  if (result->retcode==1) {
    ires=0|ires;
  } else {
    ires=1;
  }

  //free the result
  free_cmd_result(result);

  close(sockid);
  return ires;
}
