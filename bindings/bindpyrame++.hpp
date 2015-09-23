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


#include <stdexcept>
#include <iostream>
#include <sstream>
#include <fstream>
#include <vector>
#include <cstring>
#include <cstdarg>
#include <cerrno>
#include <netdb.h>
#include <expat.h>
#include <unistd.h>
#include <signal.h>

using namespace std;

class bindpyrame {
  public:

  const static int MAX_RESPONSE_SIZE = 100000;

  class ports_table {
    public:
    vector<string> names;
    vector<int> values;
    int nb_ports;
    ports_table() {};
    ports_table(const char *filename) { init_ports_table(filename); };
    void init_ports_table(const char *filename);
    int get_port (const char *name);
  };

  class cmd_result {
    public:
    int retcode;
    string str;
    cmd_result () { cmd_result(0,""); };
    cmd_result (int retcode,const char *str) : retcode(retcode), str(str) {};
  };

  int open_socket(const char * host, int port);
  struct cmd_result sendcmd(const char * host,int port,const char * func_name,...);
  struct cmd_result execcmd(int socket,const char * func_name,...);

  private:

  void static result_handler_start(void *data, const char *el, const char **attr);
  void static result_handler_end(void *data, const char *el);
  void static result_handler_data(void *data,const char *value,int len);
  struct cmd_result parse_result(const char * buf);
  struct cmd_result get_cmd_result(int socket);
};
