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


#include "libacq.h"

void update_stats(struct acq_workspace *ws,int force) {
  int i;
  char value[1024];
  struct cmd_result *result;
  if (ws->stat_socket == -1)
      return;
  for (i=0;i<MAX_STATS_VALUES;i++) {
    pthread_mutex_lock(ws->stat_mutex);
    if (ws->stats[i]==0 && !force) {
      pthread_mutex_unlock(ws->stat_mutex);
      continue;
    }
    sprintf(value,"%llu",ws->stats[i]);
    ws->stats[i]=0;
    pthread_mutex_unlock(ws->stat_mutex);
    result=execcmd(ws->stat_socket,"intopvar_varmod","0",ws->stats_name[i],"+",value,"end");
    if (result->retcode==0) {
      printf("error on setting stat : %s\n",result->str);
    }
    free_cmd_result(result);
  }
}

void init_stats(struct acq_workspace *ws,char *varmod_ip) {
  int i;
  int vport;
  //stats names and values
  char loc_stats_names[][128]={"nb_data_pkts","nb_lost_pkts","nb_corr_pkts","nb_ctrl_pkts","bytes_on_disk","bytes_on_socket","bytes_on_shmem"};
  ws->stats=malloc(MAX_STATS_VALUES*sizeof(unsigned long long));
  ws->stats_name=malloc(MAX_STATS_VALUES*sizeof(char *));
  for (i=0;i<MAX_STATS_VALUES;i++) {
    ws->stats[i]=0;
    ws->stats_name[i]=strdup(loc_stats_names[i]);
  }

  //stats mutex
  ws->stat_mutex=malloc(sizeof(pthread_mutex_t));
  pthread_mutex_init(ws->stat_mutex,NULL);

  //stats socket
  ws->stat_socket=-1;
  if (strcmp(varmod_ip,"undef")) {
    vport=get_port("VARMOD_PORT",ws->ports);
    ws->stat_socket=open_socket(varmod_ip,vport);
    if (ws->stat_socket==-1) {
      printf("Warning: No varmod available\n");
    }
  }
  update_stats(ws,1);
}

void deinit_stats(struct acq_workspace *ws) {
  int i;
  if (ws->stat_socket!=-1)
    close(ws->stat_socket);
  ws->stat_socket=-1;
  for (i=0;i<MAX_STATS_VALUES;i++) 
    free(ws->stats_name[i]);
  free(ws->stats_name);
  free(ws->stats);
  free(ws->stat_mutex);
}

void set_stats(struct acq_workspace *ws,int name,int op,int value) {
  pthread_mutex_lock(ws->stat_mutex);
  switch(op) {
  case SOP_PLUS:
    ws->stats[name]+=value;
    break;
  case SOP_MIN:
    ws->stats[name]-=value;
    break;
  case SOP_SET:
    ws->stats[name]=value;
    break;
  }
  pthread_mutex_unlock(ws->stat_mutex);
  return;
}

char * get_stats(struct acq_workspace *ws) {
  char *res=malloc(4096*sizeof(char));
  strcpy(res,"");
  int i;
  for (i=0;i<MAX_STATS_VALUES;i++) {
    sprintf(res,"%s%s=%llu ",res,ws->stats_name[i],ws->stats[i]);
  }
  return res;

}

void zero_stats(struct acq_workspace *ws) {
  int i;
  struct cmd_result *result;
  if (ws->stat_socket == -1)
      return;
  for (i=0;i<MAX_STATS_VALUES;i++) {
    pthread_mutex_lock(ws->stat_mutex);
     ws->stats[i]=0;
    pthread_mutex_unlock(ws->stat_mutex);
    result=execcmd(ws->stat_socket,"setvar_varmod","0",ws->stats_name[i],"0","end");
    if (result->retcode==0) {
      printf("error on setting stat : %s\n",result->str);
    }
    free_cmd_result(result);

  }
}


void *thread_stats(void *args) {
  struct acq_workspace *ws=(struct acq_workspace *)args;
  //init_stats(ws);
  while(1) {
    if (ws->initialized)
      update_stats(ws,0);
    usleep(1000000);
  }
}

