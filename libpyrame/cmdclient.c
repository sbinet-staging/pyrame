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


struct cmdcontext * init_cmdcontext(char * host,int port) {
  struct cmdcontext *result=malloc(sizeof(struct cmdcontext));
  result->socket=open_socket(host,port);
  result->host=host;
  result->port=port;
  return result;
}

int send_result(int socket,struct cmd_result *result) {
  char *sres;
  int res;

  if (result==NULL) {
    sres=malloc(50);
    sprintf(sres,"<res retcode=\"0\">No result</res>\n");
  } else { 
    if (result->str==NULL) {
      sres=malloc(50);
      sprintf(sres,"<res retcode=\"%d\">No result</res>\n",result->retcode);
    } else { 
      sres=malloc(50+strlen(result->str));
      sprintf(sres,"<res retcode=\"%d\"><![CDATA[%s]]></res>\n",result->retcode,result->str);
    }
  }
  signal(SIGPIPE,SIG_IGN);
  res=write(socket,sres,strlen(sres));
  if (res!=strlen(sres)) {
    printf("Error : transmission incomplete : %d instead of %d : sres=%s\n",res,(int)strlen(sres),sres);
  }
  free(sres);
  return res;
}

void check_for_cmd(struct cmdcontext *context,struct cmd_result *(*treat_func)(),void *sdata) {

  fd_set readfds;
  struct timeval tv;
    //TODO dynamic allocation
  char command[4096];
  int res;
  int size;
  struct cmd_result *cmdres;

  if (context->socket==-1) {
    //printf("socket closed, trying to open it again\n");
    context->socket=open_socket(context->host,context->port);
  }

  FD_ZERO(&readfds);
  FD_SET(context->socket,&readfds);
  tv.tv_sec = 0;
  tv.tv_usec = 1;
  if (select(context->socket+1,&readfds, NULL, NULL, &tv) >=0 ) {
    if (FD_ISSET(context->socket,&readfds)) {
      size=read(context->socket,command,4096);
      if (size<=0) {
	context->socket=-1;
      } else { 
	command[size]=0;
	//printf("command : %s, size=%d\n",command,size);
	cmdres=parse_command(command,treat_func,sdata);
	res=send_result(context->socket,cmdres);
	if (res<=0) {
	  context->socket=-1;
	}
	free(cmdres);
      }
    }
  }
}
