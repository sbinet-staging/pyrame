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


#include "../bindpyrame++.hpp"

using namespace std;

int main() {
  bindpyrame pyrame;
  bindpyrame::cmd_result result;
  int port;
  int sockid;
  int ires;

  try {
    bindpyrame::ports_table table("/opt/pyrame/ports.txt");
    port = table.get_port("TEST_PORT");
  } catch (exception& e) {
    cout << e.what() << endl;
    return -1;
  }

// SENDCMD
  try {
    result = pyrame.sendcmd("localhost",port,"twoargs_test","arg1","arg2","end");
  } catch (exception& e) {
    cout << e.what() << endl;
    return 1;
  }
  cout << "sendcmd: retcode=" << result.retcode << " res=" << result.str << endl;
  if (!result.retcode) {
    return 1;
  }

  cout << endl;

// EXECCMD
  sockid = pyrame.open_socket("localhost",port);
  try {
    result = pyrame.execcmd(sockid,"twoargs_test","arg1","arg2","end");
  } catch (exception& e) {
    cout << e.what() << endl;
    return 1;
  }
  cout << "execcmd: retcode=" << result.retcode << " res=" << result.str << endl;
  if (!result.retcode) return -1;

  close(sockid);
  return 0;
}
