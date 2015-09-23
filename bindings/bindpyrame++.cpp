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


#include "bindpyrame++.hpp"

void bindpyrame::ports_table::init_ports_table(const char * filename) {
  fstream f(filename,ios::in);
  string line,item1,item2;
  if (!f.is_open()) throw invalid_argument(string("No ports file with name ") + filename);
  f.seekg(0);
  while(getline(f,line)) {
    stringstream tmp(line);
    getline(tmp,item1,'=');
    if (!tmp.eof()) { 
      getline(tmp,item2);
      names.push_back(item1);
      values.push_back(atoi(item2.c_str()));
      nb_ports++;
    } else {
      throw runtime_error(string("Line not properly formated : ") + line);
    }
  }
  f.close();
}

int bindpyrame::ports_table::get_port(const char * name) {
  int onlydigits=1;
  char *tmp;
  if (name==NULL) throw invalid_argument("Invalid port name");
  for (tmp=(char*)name;*tmp != 0 && onlydigits;tmp++)
    if (*tmp < 48 || *tmp > 57) onlydigits = 0;
  if (!onlydigits) {
    for (vector<int>::size_type i=0;i!=names.size();i++)
      if (!names[i].compare(name)) return values[i];
    throw out_of_range("Port not found");
  } else return atoi(name);
}

int bindpyrame::open_socket(const char * host, int port) {
  int ddid;
  addrinfo hints={0,AF_UNSPEC,SOCK_STREAM},*res,*rp;
  stringstream ss_port;
  ss_port << port;
  int s = getaddrinfo(host,ss_port.str().c_str(),&hints,&res);
  if (s != 0) throw runtime_error("Error getting host by name");
  for (rp=res;rp!=NULL;rp=rp->ai_next) {
    ddid=socket(rp->ai_family,rp->ai_socktype,rp->ai_protocol);
    if (connect(ddid,rp->ai_addr,rp->ai_addrlen) != -1)
      break;
    close(ddid);
  }
  freeaddrinfo(res);
  if (rp == NULL) throw runtime_error(string("Error connecting to socket: ") + strerror(errno));
  return ddid;
}

void bindpyrame::result_handler_start(void *data, const char *el, const char **attr) {
  cmd_result *toparse = (cmd_result*)data;
  if (!strcmp(el,"res")) {
    toparse->retcode=atoi(attr[1]);   
  }
}

void bindpyrame::result_handler_end(void *data, const char *el) {
}

void bindpyrame::result_handler_data(void *data,const char *value,int len) {
  cmd_result *toparse=(cmd_result*) data;
  toparse->str = value;
  toparse->str.resize(len);
}

bindpyrame::cmd_result bindpyrame::parse_result(const char * buf) {
  cmd_result result;
  XML_Parser parser = XML_ParserCreate(NULL);
  XML_SetUserData(parser,&result);
  XML_SetElementHandler(parser,result_handler_start,result_handler_end);
  XML_SetCharacterDataHandler(parser,&result_handler_data);
  if (!XML_Parse(parser,buf,strlen(buf),1)) {
    cerr << "error in result XML_Parse : error=" << XML_GetErrorCode(parser) << endl;
    cerr << XML_ErrorString(XML_GetErrorCode(parser)) << endl;
    cerr << "buffer=" << buf << endl;
    result.str="Malformed command";
    result.retcode=0;
  }
  XML_ParserFree(parser);
  return result;
}

bindpyrame::cmd_result bindpyrame::get_cmd_result(int socket){
  char msg[MAX_RESPONSE_SIZE];
  int j;
  int size;
  memset(msg,0,sizeof(msg));
  j=0;
  fd_set read_fds;
  FD_ZERO(&read_fds);
  FD_SET(socket,&read_fds);
  int res;
  do {
    if ((res = select(socket+1,&read_fds,NULL,NULL,NULL))) {
      if (res == -1) {
        throw runtime_error ("Error while checking data with select()");
      } else {
        size=read(socket,msg+j,1);
        if (size<=0) {
          throw runtime_error("result socket closed (read)");
        } else {
          j++;
          if (j==MAX_RESPONSE_SIZE) {
            throw runtime_error("maximal buffer size reached");
          }
        }
      }
    } else {
      throw runtime_error("Timeout waiting for data");
    }
  } while(msg[j-1]!='\n'); 
  //cout << "obtained result : " << msg;
  return parse_result(msg);
}

bindpyrame::cmd_result bindpyrame::sendcmd(const char * host,int port,const char * func_name,...) {
  int socket;
  va_list pa;
  int size;
  string param;
  stringstream cmd;
  
  socket=open_socket(host,port);
  cmd << "<cmd name=\"" << func_name << "\">";
  va_start(pa,func_name);
  while(1) { 
    param=va_arg(pa,char *);
    if (!strcmp(param.c_str(),"end")) {
      break;
    } else {  
      cmd << "<param>" << param << "</param>";
    }
  }
  va_end(pa);
  cmd << "</cmd>" << endl;
  //cout << "cmd=" << cmd.str();
  signal(SIGPIPE,SIG_IGN);
  size=write(socket,cmd.str().c_str(),cmd.tellp());
  if (size<=0) {
    close(socket);
    throw runtime_error("Error sending command");
  }
  cmd_result result = get_cmd_result(socket);
  if (result.retcode==2) { //wakeup
    cout<<"wakeup"<<endl;
    close(socket);
    usleep(50000);
    socket=open_socket(host,port);
    size=write(socket,cmd.str().c_str(),cmd.tellp());
    result=get_cmd_result(socket);
  }
  close(socket);
  return result;
}


bindpyrame::cmd_result bindpyrame::execcmd(int socket,const char * func_name,...) {
  int size;
  va_list pa;
  string param;
  ostringstream cmd;
  cmd << "<cmd name=\"" << func_name << "\">";
  va_start(pa,func_name);
  while(1) { 
    param=va_arg(pa,char *);
    if (!strcmp(param.c_str(),"end")) {
      break;
    } else {  
      cmd << "<param>" << param << "</param>";
    }
  }
  va_end(pa);
  cmd << "</cmd>" << endl;
  //cout << "cmd=" << cmd.str();
  signal(SIGPIPE,SIG_IGN);
  size=write(socket,cmd.str().c_str(),cmd.tellp());
  if (size<=0) {
    close(socket);
    throw runtime_error("Error sending command");
  }
  return get_cmd_result(socket);
}
