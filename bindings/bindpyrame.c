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


#include "bindpyrame.h"

int open_socket(char * host, int port) {
  int ddid;
  struct addrinfo hints={0,AF_UNSPEC,SOCK_STREAM},*res,*rp;
  char *s_port = malloc(((int)floor(log10(abs(port))) + 2)*sizeof(char));
  sprintf(s_port,"%d",port);
  int s = getaddrinfo(host,s_port,&hints,&res);
  if (s != 0) {
    //fprintf(stderr,"bindpyrame : Error getting host by name\n");
    return -1;
  }
  for (rp=res;rp!=NULL;rp=rp->ai_next) {
    ddid=socket(rp->ai_family,rp->ai_socktype,rp->ai_protocol);
    if (connect(ddid,rp->ai_addr,rp->ai_addrlen) != -1) 
      break;
    close(ddid);
  }
  freeaddrinfo(res);
  free(s_port);
  if (rp == NULL) {
    //perror("bindpyrame : Error connecting to socket");
    return -1;
  }
  return ddid;
}

//********************** PORTS FUNCTIONS ***************************


struct ports_table *init_ports_table(char * filename) {
  struct ports_table *table =malloc(sizeof(struct ports_table));
  FILE *f;
  int i=0, j;
  //TODO dynamic allocation
  char line[255];
  char *tmp;
  memset(table,0,sizeof(struct ports_table));
  //printf("opening port table file %s\n",filename);
  f=fopen(filename,"r");
  if (f==NULL) {
    perror("fopen");
    return table;
  }
  while(fgets(line,sizeof(line),f)) {
    table->nb_ports++;
  } 
  table->names=malloc(table->nb_ports*sizeof(char *));
  table->values=malloc(table->nb_ports*sizeof(int));
  rewind(f);
  while(fgets(line,sizeof(line),f)) {
    tmp=line;
    while(*tmp!='=') {
      tmp++;
      if (*tmp==0) {
        fprintf(stderr,"Line not properly formatted : %s",line);
        for (j=0;j<i;j++) {
          free(table->names[j]);
        }
        free(table->names);
        free(table->values);
        table->names = NULL;
        table->values = NULL;
        fclose(f);
        return table;
      }
    }
    *tmp=0;
    tmp++;
    table->names[i]=strdup(line);
    table->values[i]=atoi(tmp);
    i++;
  }
  fclose(f);
  return table;
}

void free_ports_table (struct ports_table *table) {
  int i;
  for (i=0;i<table->nb_ports;i++) {
    free(table->names[i]);
  }
  free(table->names);
  free(table->values);
}

int get_port(char *name,struct ports_table *table) {
  int i,onlydigits=1;
  char *tmp;
  if (name==NULL)
    return 0;
  for (tmp=name;*tmp != 0 && onlydigits;tmp++)
    if (*tmp < 48 || *tmp > 57) onlydigits = 0;
  if (!onlydigits) {
    for (i=0;i<table->nb_ports;i++) {
      if (!strcmp(name,table->names[i]))
        return table->values[i];
    }
    return -1;
  } else return atoi(name);
}

char * extract_port_name(char * func_name) {
  int i;
  char *portname=malloc(strlen(func_name)+30);
  char *tmpport=strdup(func_name);
  char * origtmpport=tmpport;
  while(tmpport[0]!=0)
    tmpport++;
  while(tmpport[0]!='_')
    tmpport--;
  tmpport++;
  for(i=0;i<strlen(tmpport);i++)
    tmpport[i]=tmpport[i]-'a'+'A';
  sprintf(portname,"%s_PORT",tmpport);
  free(origtmpport);
  return portname;
}

//********************** RESULT FUNCTIONS ***************************

void result_handler_start(void *data, const char *el, const char **attr) {
  struct cmd_result *toparse=(struct cmd_result*)data;
  if (!strcmp(el,"res")) {
    toparse->retcode=atoi(attr[1]);   
  }
}

void result_handler_end(void *data, const char *el) {
  return;
}

void result_handler_data(void *data,const char *value,int len) {
  struct cmd_result *toparse=(struct cmd_result*)data;
  toparse->str=malloc(sizeof(char)*len+2);
  memset(toparse->str,0,sizeof(char)*len+2);
  strncpy(toparse->str,value,len);
}

struct cmd_result *parse_result(char * buf) {
  struct cmd_result *result=malloc(sizeof(struct cmd_result));
  memset(result,0,sizeof(struct cmd_result));
  XML_Parser parser = XML_ParserCreate(NULL);
  XML_SetUserData(parser,result);
  XML_SetElementHandler(parser,result_handler_start,result_handler_end);
  XML_SetCharacterDataHandler(parser,result_handler_data);

  if (!XML_Parse(parser,buf,strlen(buf),1)) {
    fprintf(stderr,"error in result XML_Parse : error=%d\n",XML_GetErrorCode(parser));
    fprintf(stderr,"%s\n",XML_ErrorString(XML_GetErrorCode(parser)));
    fprintf(stderr,"buffer=%s\n",buf);
    result->str=strdup("Malformed command");
    result->retcode=0;
  }
  XML_ParserFree(parser);
  if (result->str==NULL) {
    result->str=malloc(1);
    result->str[0]=0;
  }
  return result;
}

struct cmd_result *get_cmd_result(int socket){
  int msg_s=4096;
  char *msg=malloc(msg_s*sizeof(char));
  int j=0;
  int i;
  int size;
  struct cmd_result *result;
  int end_found=0;
  fd_set read_fds;
  //struct timeval tv;
  FD_ZERO(&read_fds);
  FD_SET(socket,&read_fds);
  int res;
  res = select(socket+1,&read_fds,NULL,NULL,NULL);

  //error checking
  if (res==-1) {
    perror("select");
    result=malloc(sizeof(struct cmd_result));
    result->retcode=0;
    result->str=strdup("Error in select");
    return result;
  }

  //effective reading of result
  do {
    if (j+1024>=msg_s) {
      msg_s+=4096;
      msg=realloc(msg,msg_s);
    }
    size=read(socket,msg+j,1024);
    if (size<=0) {
      fprintf(stderr,"result socket closed (read)\n");
      break;
    } else {
      for (i=j;i<j+size;i++)
	if (msg[i]=='\n') {
	  end_found=1;
	  msg[i+1]=0;
	}
      j+=size;
    }  
  } while(end_found==0); 

  //parsing result
  //gettimeofday(&tv,NULL);
  //printf("before parse_result micros=%d\n",(int)tv.tv_usec);
  result=parse_result(msg);
  free(msg);
  //gettimeofday(&tv,NULL);
  //printf("after parse_result micros=%d\n",(int)tv.tv_usec);
  return result;
}

void free_cmd_result(struct cmd_result *result) {
  free(result->str);
  free(result);
}

//********************** COMMAND CONVERSION FUNCTIONS ***********************

char * args_2_strcmd(char * func_name,va_list pa) {
  int cmdsize=strlen(func_name)+30;
  char *cmd=malloc(cmdsize);
  char *param;
  sprintf(cmd,"<cmd name=\"%s\">",func_name);
  while(1) { 
    param=va_arg(pa,char *);
    if (!strcmp(param,"end")) {
      break;
    } else {
      cmdsize+=strlen(param)+20;
      cmd=realloc(cmd,cmdsize);
      sprintf(cmd,"%s<param>%s</param>",cmd,param);
    }
  }
  sprintf(cmd,"%s</cmd>\n",cmd);
  return cmd;
}

char * cmd_2_strcmd(struct cmd *command) {
  int cmdsize=strlen(command->name) + 30;
  char *cmd=malloc(cmdsize);
  int i;
  sprintf(cmd,"<cmd name=\"%s\">",command->name);
  for (i=0;i<command->nb_params;i++) {
    cmdsize+=strlen(command->params[i])+20;
    cmd=realloc(cmd,cmdsize);
    sprintf(cmd,"%s<param>%s</param>",cmd,command->params[i]);
  }
  sprintf(cmd,"%s</cmd>\n",cmd);
  return cmd;
}

//********************** SEND COMMAND FUNCTIONS ***************************

struct cmd_result *send_cmd(char * host,int port,struct cmd *command) {
  char *cmd;
  struct cmd_result *result;

  //convert the command in string command
  cmd=cmd_2_strcmd(command);

  //send the command and get the result
  result=send_strcmd(host,port,cmd);

  //free the command
  free(cmd);

  //return the result
  return result;
}

struct cmd_result *sendcmd(char * host,int port,char * func_name,...) {
  char *cmd;
  struct cmd_result *result;

  //converting arguments in string command
  va_list pa;
  va_start(pa,func_name);
  cmd=args_2_strcmd(func_name,pa);
  va_end(pa);

  //send the command and get the result
  result=send_strcmd(host,port,cmd);

  //free the command
  free(cmd);

  //return the result
  return result;
}
  

struct cmd_result *send_strcmd(char * host,int port,char * strcmd) {
  int socket;
  int i;
  struct cmd_result *result;
  
  //open a socket
  socket=open_socket(host,port);
  if (socket==-1) {
    result=malloc(sizeof(struct cmd_result));
    result->retcode=0;
    result->str=strdup("unable to connect TCP socket");
    return result;
  }

  //send the command
  result=exec_strcmd(socket,strcmd);
 
  if (result->retcode==2) { //wakeup

    //free the result
    free_cmd_result(result);
    //close the socket
    close(socket);

    for (i=0;i<10;i++) {
      //wait for the close to be effective 
      usleep(500000);

      //reopen the socket
      socket=open_socket(host,port);
      if ((socket==-1) && (i==9)) {
        result->retcode=0;
        result->str=strdup("unable to connect TCP socket");
        return result;
      }
      if (socket!=-1) {
        break;
      }
    }

    //send the command
    result=exec_strcmd(socket,strcmd);
  }
    
  close(socket);
  return result;
}

//********************** EXEC COMMAND FUNCTIONS ***************************

  
struct cmd_result *execcmd(int socket,char * func_name,...) {
  char *cmd;
  struct cmd_result *result;

  //converting arguments in command_string
  va_list pa;
  va_start(pa,func_name);
  cmd=args_2_strcmd(func_name,pa);
  va_end(pa);
  
  //send the command
  result=exec_strcmd(socket,cmd);

  //free the command
  free(cmd);

  //return the result
  return result;
}
 
struct cmd_result *exec_cmd(int socket,struct cmd *command) {
  char *cmd;
  struct cmd_result *result;
  
  //convert the command in string command
  cmd=cmd_2_strcmd(command);
  
  //send the command
  result=exec_strcmd(socket,cmd);
  
  //free the command
  free(cmd);
  
  //return the result
  return result;
}

struct cmd_result *exec_strcmd(int socket,char * strcmd) {
  int size;
  struct cmd_result *result;
  signal(SIGPIPE,SIG_IGN);
  size=write(socket,strcmd,strlen(strcmd));
  if (size<=0) {
    close(socket);
    result=malloc(sizeof(struct cmd_result));
    result->retcode=0;
    result->str=strdup("Error sending command (socket closed)");
    return result;
  }
  result=get_cmd_result(socket);
  return result;
}


//********************** INCR_STRING FUNCTIONS ***************************

struct incr_string *new_incr_string() {
  struct incr_string *res=malloc(sizeof(struct incr_string));
  res->str=(char *)malloc(1001);
  res->str[0]=0;
  res->size=0;
  res->alloc_size=1000;
  return res;
}

void suffix_incr_string(struct incr_string *res,char * addstr) {
  int addsize=strlen(addstr);
  char * ptr;
  while (res->size+addsize>res->alloc_size) {
    res->str=realloc(res->str,res->alloc_size+1000+1);
    res->alloc_size+=1000;
  }
  ptr=res->str+res->size;
  sprintf(ptr,"%s",addstr);
  res->size+=addsize;
}

void free_incr_string(struct incr_string *res) {
  free(res->str);
  free(res);
}
