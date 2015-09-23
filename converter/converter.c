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

#include "converter.h"

struct conv_ws * init_ws() {
  int i;
  struct event *e_tmp;
  struct event *e_prev;
  struct event *e_first;
  struct conv_ws * res;

  //allocate the circular buffer
  for (i=0;i<1000000;i++) {
    e_tmp=malloc(sizeof(struct event));
    bzero(e_tmp,sizeof(struct event));
    e_tmp->used=1;
    e_tmp->block=-1;
    if (i==0) {
      e_first=e_tmp;
      e_prev=e_tmp;
    } else {
      e_prev->next=e_tmp;
      e_prev=e_tmp;
    }
    e_tmp->next=e_first;
  }

  res=malloc(sizeof(struct conv_ws));
  bzero(res,sizeof(struct conv_ws));
  res->current=e_first;
  res->evt_mutex=malloc(sizeof(pthread_mutex_t));
  pthread_mutex_init(res->evt_mutex,NULL);
  return res;
}


void  new_event(struct conv_ws *ws,int block,char *time,char *space,char *data) {

  //aquire the mutex
  pthread_mutex_lock(ws->evt_mutex);

  //increase stats if current event is not used
  if (ws->current->used==0) {
    ws->nbtbnu++;
  }

  //fill the event
  if (ws->current->time!=NULL)
    free(ws->current->time);
  ws->current->time=time;
  if (ws->current->space!=NULL)
    free(ws->current->space);
  ws->current->space=space;
  if (ws->current->data!=NULL)
    free(ws->current->data);
  ws->current->data=data;
  ws->current->used=0;
  ws->current->block=block;
  ws->current=ws->current->next;

  //release the mutex
   pthread_mutex_unlock(ws->evt_mutex);

}


int request_new_data(struct conv_ws *ws,char * buffer) {

  read_shbuffer(ws->shbuf,buffer);
  //size=read(ws->data_socket,buffer,rsize);
  return 1;
}


void inc_stat(struct conv_ws *ws,char * stat_name,int value) {
  /*struct cmd_result *result;
  char svalue[1024];
  sprintf(svalue,"%d",value);
  result=execcmd(ws->varmod_socket,"intopvar",stat_name,"+",svalue,"end");
  if (result->retcode==0) {
    printf("error in varmod : %s",result->str);
  }
  free_cmd_result(result);*/
}


void update_clock(struct conv_ws *ws,char * new_clock) {
  if (ws->clock!=NULL) {
    free(ws->clock);
  }
  ws->clock=new_clock;
  if (ws->clock_socket!=-1) {
    write(ws->clock_socket,ws->clock,strlen(ws->clock));
  }
}

struct cmd_result * treat_cmd(struct cmd*command,void *sdata) {
  int rblock;
  struct event*eptr;
  struct incr_string* blcres;
  int curblock;
  int blclim;
  char tmp[1024];
  struct timeval tv;

  struct conv_ws *ws=(struct conv_ws *)sdata;
  struct cmd_result *res=malloc(sizeof(struct cmd_result));
  res->retcode=-1;
  res->str=NULL;

  //*************************************
  if (!strcmp(command->name,"get_block_list")) {

    if (command->nb_params!=1) {
      res->retcode=0;
      res->str=malloc(4096*sizeof(char));
      sprintf(res->str,"get_block_list, %d arguments given, 1 needed",command->nb_params-1);
      return res;
    }

    blclim=atoi(command->params[0]);

    //aquire the mutex
    pthread_mutex_lock(ws->evt_mutex);

    //contruct the block list
    eptr=ws->current->next;
    curblock=-2;
    blcres=new_incr_string();
    while(eptr!=ws->current) {
      if (eptr->block!=curblock && eptr->block!=-1 && eptr->block>blclim) {
	printf("new block : %d \n",eptr->block);
	if (curblock==-2) {
	  sprintf(tmp,"%d",eptr->block);
	  suffix_incr_string(blcres,tmp);
	} else {
	  sprintf(tmp,",%d",eptr->block);
	  suffix_incr_string(blcres,tmp);
	}
	curblock=eptr->block;
      }
      eptr=eptr->next;
    }
    
    //release the mutex
    pthread_mutex_unlock(ws->evt_mutex);

    //return the result
    res->retcode=1;
    res->str=blcres->str;
    //CAUTION : tricky do not free the string of the incr string
    free(blcres);
    return res;

  }

  //*************************************
  if (!strcmp(command->name,"get_block")) {
    
    if (command->nb_params!=1) {
      res->retcode=0;
      res->str=malloc(4096*sizeof(char));
      sprintf(res->str,"get_block, %d arguments given, 1 needed",command->nb_params-1);
      return res;
    }

    //The argument is the requested block
    rblock=atoi(command->params[0]);

    gettimeofday(&tv,NULL);
    printf("acquire mutex micros=%d\n",(int)tv.tv_usec);

    //aquire the mutex
    pthread_mutex_lock(ws->evt_mutex);


    gettimeofday(&tv,NULL);
    printf("build packet micros=%d\n",(int)tv.tv_usec);
    //fill the result
    blcres=new_incr_string();
    eptr=ws->current->next;
    while(eptr!=ws->current) {
      if (eptr->block==rblock) {
	//printf("select that event : %s %s %s\n",eptr->time,eptr->space,eptr->data);
	sprintf(tmp,"!%s|%s|%s",eptr->time,eptr->space,eptr->data);
	suffix_incr_string(blcres,tmp);
      }
      eptr=eptr->next;
    }
    gettimeofday(&tv,NULL);
    printf("end build packet micros=%d\n",(int)tv.tv_usec);

    //release the mutex
    pthread_mutex_unlock(ws->evt_mutex);

    //return the result
    res->retcode=1;
    res->str=blcres->str;
    //CAUTION : tricky do not free the string of the incr string
    free(blcres);
    return res;

  }

  //*************************************
  res->retcode=0;
  res->str=strdup("Unknown command");
  printf("unknown command\n");
  return res;
} 


//the thread that treat the commands
void *dispatcher(void *args) {
  struct conv_ws *ws=(struct conv_ws *)args;
  //wait indefinitely for commands
  while(1)
    wait_for_cmd(ws->cmd_sockets,treat_cmd,ws);
  return 0;
}


int main(int argc,char **argv) {

  pthread_t t_dispatcher;
  struct ports_table *table;
  int vport;

  //init the workspace
  struct conv_ws * ws=init_ws();

  //extract parameters from command line
  if (argc<4) {
    printf("usage : %s streamid convert_plugin clock_port\n",argv[0]);
    exit(1);
  }

  ws->streamid=atoi(argv[1]);
  ws->plugin_name=strdup(argv[2]);
  ws->cport=atoi(argv[3]);

  /*
  //init the input socket
  ws->data_socket=open_socket(ws->host,ws->iport);
  if (ws->data_socket==-1) {
    printf("unable to open data connection\n");
    exit(1);
    }*/

  //open the shared buffer
  ws->shbuf=open_shbuffer(ws->streamid,NO_CREATE);
  ready_shbuffer(ws->shbuf);

  //init the netserv
  ws->cmd_sockets=first_client(start_monoport_netserv(9110+ws->streamid,10));

  //load the convert plugin
  ws->lib=dlopen(ws->plugin_name,RTLD_NOW|RTLD_GLOBAL);
  if (ws->lib==NULL) {
    printf("plugin dlopen error : %s\n",dlerror()); 
    exit(1);
  }
  ws->convert=dlsym(ws->lib,"convert");
  if (ws->convert==NULL) {
    perror("dlsym");
    printf("cant find symbol convert\n");
    exit(1);
  }

  //init the varmod socket
  table=init_ports_table("/opt/pyrame/ports.txt");
  vport=get_port("VARMOD_PORT",table);
  free_ports_table(table);
  ws->varmod_socket=open_socket("localhost",vport);
  if (ws->varmod_socket==-1) {
    printf("cant open varmod socket\n");
  }
  
  //init the clock socket
  if (ws->cport!=-1) {
    ws->clock_socket=open_socket("localhost",ws->cport);
  } else 
    ws->clock_socket=-1;
  
  //launching disptching thread
  if (pthread_create(&t_dispatcher,NULL,dispatcher,ws)<0) {
    perror("pthread_create");
    exit(1);
  }
  pthread_detach(t_dispatcher);

  //init the converter plugin workspace
  ws->lws=(struct convlib_ws *)malloc(sizeof(struct convlib_ws));
  bzero(ws->lws,sizeof(struct convlib_ws));
  ws->lws->cws=ws;
  ws->lws->name=strdup(argv[1]);

  //begin conversion
  ws->convert(ws->lws);
  return 0; 
}
