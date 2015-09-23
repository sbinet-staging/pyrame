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

int iohtoi(char * string) {
  if (string[0]=='0') { //zero, octal or hexa
    if (string[1]==0) //zero
      return 0;
    if (string[1]=='x') //hexa
      return strtol(string,NULL,16);
    else //octal
      return strtol(string,NULL,8);
  } else { //decimal
    return atoi(string);
  }
}

void free_cmd(struct cmd *tofree) {
  int i;
  for (i=0;i<tofree->nb_params;i++) 
    free(tofree->params[i]);
  free(tofree->params);
  free(tofree->name);
  free(tofree);
}

void print_cmd(struct cmd *command) {
  int i;
  if (command==NULL) {
    printf("null command\n");
    return;
  }
  if (command->name==NULL) {
    printf("command with no name\n");
    return;
  }
  printf("command %s with %d params : ",command->name,command->nb_params);
  if (command->nb_params==0)
    printf("\n");
  for (i=0;i<command->nb_params;i++) {
    if (i==command->nb_params-1)
      printf("%s\n",command->params[i]);
    else
      printf("%s,",command->params[i]);
  }
}

void cmd_handler_start(void *data, const char *el, const char **attr) {
  struct cmd *toparse=(struct cmd*)data;
  if (!strcmp(el,"cmd")) {
    strncpy(toparse->name,attr[1],1024);
    toparse->nb_params=0;
  }
  if (!strcmp(el,"param")) {
    toparse->nb_params++;
  }
}

void cmd_handler_end(void *data, const char *el) {
  struct cmd *toparse=(struct cmd*)data;
  if (!strcmp(el,"param")) {
    if (toparse->params[toparse->nb_params-1]==NULL) {
      toparse->params[toparse->nb_params-1]=strdup("");
    }
  }
}

void cmd_handler_data(void *data,const char *value,int len) {
  struct cmd *toparse=(struct cmd*)data;
  toparse->params[toparse->nb_params-1]=malloc((len+1)*sizeof(char));
  strncpy(toparse->params[toparse->nb_params-1],value,len);
  toparse->params[toparse->nb_params-1][len]=0;
}


struct cmd_result *parse_command(char * buf,struct cmd_result *(*treat_func)(),void *sdata) {

  //allocate the command structure to fill with data from xml
  struct cmd *toparse=malloc(sizeof(struct cmd));
  toparse->name=malloc(1024*sizeof(char));
  bzero(toparse->name,1024);
  toparse->nb_params=0;
  toparse->params=malloc(MAX_PARAMS*sizeof(char *));
  memset(toparse->params,0,MAX_PARAMS*sizeof(char*));
  struct cmd_result *result;
  
  XML_Parser parser = XML_ParserCreate(NULL);
  XML_SetUserData(parser,toparse);
  XML_SetElementHandler(parser,cmd_handler_start,cmd_handler_end);
  XML_SetCharacterDataHandler(parser,cmd_handler_data);

  if (!XML_Parse(parser,buf,strlen(buf),1)) {
    printf("error in command XML_Parse : error=%d\n",XML_GetErrorCode(parser));
    printf("%s\n",XML_ErrorString(XML_GetErrorCode(parser)));
    printf("buffer=%s\n",buf);
    result=malloc(sizeof(struct cmd_result));
    result->retcode=0;
    result->str=NULL;
  } else {
    result=treat_func(toparse,sdata);
  }
  free_cmd(toparse);
  XML_ParserFree(parser);
  if (result->str==NULL)
    result->str=strdup("Malformed command");
  return result;
}



void wait_for_cmd(struct netserv_client * clients,struct cmd_result *(*treat_func)(),void *sdata) {

  fd_set readfds;
  int highest;
  struct timeval tv;
  long unsigned int command_s = 4096;
  char * command = malloc(command_s);
  int res;
  int size;
  int i;
  long unsigned int j;
  int end_found=0;
  int k;

  struct cmd_result *cmdres;
 

  FD_ZERO(&readfds);
  if (clients->control_socket != NULL) {
    FD_SET(clients->control_socket[0],&readfds);
    highest=clients->control_socket[0];
  } else { highest = 0; }
  for(i=0;i<clients->nb_sock_client;i++) {
    if (clients->sock_client[i]!=-1) {
      FD_SET(clients->sock_client[i],&readfds);
      if (highest<=clients->sock_client[i])
        highest=clients->sock_client[i];
    }
  }
  tv.tv_sec=0;
  tv.tv_usec=UCMD_DELAY;
  if (select(highest+1,&readfds, NULL, NULL, &tv)>=0 ) {
    //gettimeofday(&tv,NULL);
    //printf("end of select in wait_for_cmd micros=%d\n",(int)tv.tv_usec);
    if (clients->control_socket != NULL) {
      if (FD_ISSET(clients->control_socket[0],&readfds)) {
        read(clients->control_socket[0],command,4096); // flush pipe
      }
    }
    for (i=0;i<clients->nb_sock_client;i++)
      if (clients->sock_client[i]!=-1) {
        if (FD_ISSET(clients->sock_client[i],&readfds)) {
          //gettimeofday(&tv,NULL);
          //printf("socket opened\n");// s=%d.%d\n",(int)tv.tv_sec,(int)tv.tv_usec);
          j=0;
          do {
            if (j+1024>=command_s) {
              command_s+=4096;
              command=realloc(command,command_s);
            }
            size=read(clients->sock_client[i],command+j,1024);
            if (size<=0) {
              close(clients->sock_client[i]);
              clients->sock_client[i]=-1;
              break;
            } else {
              for (k=j;k<j+size;k++)
                if (command[k]=='\n') {
                  end_found=1;
                  command[k+1]=0;
                }
              j+=size;
            }
          } while(end_found==0);
          command[j]=0;
          //gettimeofday(&tv,NULL);
          //printf("command obtained s=%d.%d\n",(int)tv.tv_sec,(int)tv.tv_usec);
          //printf("command : %s, size=%lu\n",command,j);
          if (size!=0) {
            cmdres=parse_command(command,treat_func,sdata);
            //gettimeofday(&tv,NULL);
            //printf("result computed s=%d.%d\n",(int)tv.tv_sec,(int)tv.tv_usec);
            res=send_result(clients->sock_client[i],cmdres);
            //gettimeofday(&tv,NULL);
            //printf("result sent s=%d.%d\n",(int)tv.tv_sec,(int)tv.tv_usec);
            if (res<=0) {
              printf("cmd socket lost (send) %d\n",i);
              perror("write");
              close(clients->sock_client[i]);
              clients->sock_client[i]=-1;
            }
            if (cmdres->str)
              free(cmdres->str);
            free(cmdres);
          }
        }
      }
    free(command);
  } else {
    perror("select");
    exit(1);
  }
}

