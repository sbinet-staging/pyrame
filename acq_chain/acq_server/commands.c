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

char encode_quartet(char c) {
  if (c<10) 
    return c+'0';
  return c-10+'a';
}

char *encode_packet(unsigned char *packet,int size) {
  int i;
  char * result=malloc(2*size*sizeof(char)+1);
  //printf("encode packet of size %d\n",size);
  memset(result,0,2*size*sizeof(char)+1);
  for(i=0;i<size;i++) {
    result[2*i+1]=encode_quartet(packet[i]&0xf);
    result[2*i]=encode_quartet((packet[i]&0xf0)>>4);
  }
  return result;
}

unsigned char *decode_binary_data(char *input,int *size) {
  int lsize=strlen(input);
  unsigned char *result=malloc(sizeof(unsigned char)*lsize);
  int i;
  char **mots=malloc(sizeof(char *)*lsize);
  int nb_mots=1;
  mots[0]=input;
  i=0;
  while(input[i]!=0) {
    i++;
    if (input[i]==',') {
      mots[nb_mots]=input+i+1;
      input[i]=0;
      nb_mots++;
      i++;
    }
  }
  //printf("fin de parsing : %d mots\n",nb_mots);
  *size=nb_mots;
  for(i=0;i<nb_mots;i++)
    result[i]=iohtoi(mots[i]);
  free(mots);
  return result;
}

struct cmd_result * treat_cmd(struct cmd *command,void *sdata) {
  struct acq_workspace *ws=(struct acq_workspace *)sdata;
  int id1,id2,id3,id4,id5;
  struct data_descriptor *current_ctrl;
  int i;
  char * encoded;
  char *sres;
  int streamid;
  struct generic_buffer *acq_buffer;
  unsigned char *binary_data;

  struct cmd_result *res=malloc(sizeof(struct cmd_result));
  res->retcode=-1;
  res->str=NULL;
  
  printf("********************* NEW COMMAND **********************\n");
  printf("executing local function %s with %d params : \n",command->name,command->nb_params);
  for (i=0;i<command->nb_params;i++) {
    printf("param%d=%s\n",i,command->params[i]);
  }

  if (!strcmp(command->name,"init_acq")) { 
    //param 0 : datadir
    //param 1 : varmod IP (or undef)

    if (ws->initialized!=0) {
    res->str=strdup("acq has been already been initialized");
    res->retcode=1;
    return res;
  }

    if (command->nb_params<2) {
      res->retcode=0;
      res->str=malloc(4096*sizeof(char));
      sprintf(res->str,"init_acq, %d arguments given, 2 needed",command->nb_params-1);
      return res;
    }

    //initializing the stats
    init_stats(ws,command->params[1]);

    //initializing the acquisition
    init_acquisition(ws,command->params[0]);

    //initializing the scheduler
    init_burst_detector(ws);

    //initializing all the other modules
    launch_consumer_chain(ws);

    //initialization is done
    ws->initialized=1;

    res->str=strdup("acquisition initialized");
    res->retcode=1;
    return res;
  }

//********************************************

  if (!strcmp(command->name,"deinit_acq")) { 

    if (ws->initialized!=1) {
      res->str=strdup("ethacq is not initialized");
      res->retcode=1;
      return res;
    }

    //deinit the acquisition
    deinit_acquisition(ws);

    //stopping all the treatment modules
    stop_consumer_chain(ws);

    //deinit the scheduler
    deinit_burst_detector(ws);

    //initializing the stats
    deinit_stats(ws);

    //close and free the streams structures
    ws->nb_streams=0;

    //deinit is done
    ws->initialized=0;

    //return ok
    res->str=strdup("acquisition deinitialized");
    res->retcode=1;
    return res;
  }

  //********************************************    

  //stop any other command until initialize is completed
  if (ws->initialized==0) {
    res->str=strdup("cmd are forbidden while acq not initialized");
    res->retcode=0;
    return res;
  }


 //********************************************
 if (!strcmp(command->name,"newunit_acq")) { 
    //param 0 : nb_streams
    //param 1 : name of the acq library
    //param 2 : name of the uncap library
    //param 3 : stream_suffix
    //param 4 : specific param 1
    //param 5 : specific param 2
    //param 6 : specific param 3

    if (command->nb_params<7) {
      res->retcode=0;
      res->str=malloc(4096*sizeof(char));
      sprintf(res->str,"newunit_acq, %d arguments given, 7 needed",command->nb_params-1);
      return res;
    }

    //get first stream id
    int nbs=iohtoi(command->params[0]);
    int fid=ws->nb_streams;
    printf("nbs=%d fid=%d\n",nbs,fid);

    //create the workspace for the new unit
    printf("creating newunit workspace\n");
    struct acqunit_workspace * newunit=make_acq_unit(nbs,fid,command->params[1],command->params[2],command->params[3],ws);
    if (newunit==NULL) {
      res->retcode=0;
      res->str=malloc(4096*sizeof(char));
      sprintf(res->str,"error loading plugins");
      return res;
    }
    
    //initialize acquisition library
    printf("initializing acquisition library\n");
    newunit->specws=(newunit->init_acq)(command->params[4],command->params[5],command->params[6]);

    //initialize uncap library
    printf("initializing uncap library\n");
    newunit->uncapws=(newunit->init_uncap)(nbs,fid,command->params[1]);

    //we initialize the nb of streams 
    ws->nb_streams+=nbs;

    //initializing the streams
    printf("initializing the streams\n");
    newunit->streams=malloc(nbs*sizeof(struct stream_workspace));
    for(i=0;i<nbs;i++) {
      printf("creating stream %d with id %d\n",i,fid+i);
      newunit->streams[i].id=fid+i;
      newunit->streams[i].output=-1;
      newunit->streams[i].socket=NULL;
      newunit->streams[i].shdata=NULL;
      newunit->streams[i].acqunit=newunit;
      ws->streams[i+fid]=newunit->streams[i];
    }

    //store the newunit in the main ws
    printf("linking the new unit\n");
    newunit->next=ws->acqunits;
    ws->acqunits=newunit;

    //open new files
    printf("open the new files\n");
    opennew_files(ws);

    //open new sockets
    printf("open the new sockets\n");
    opennew_socket(ws);
  
    //open new shared buffers
    printf("open the new shared buffers\n");
    opennew_shmem(ws);

    //start the thread
    printf("Starting the acquisition thread\n");
    if (pthread_create(&(newunit->t_acquisition),NULL,acquisition,newunit)<0) {
      perror("pthread_create");
      exit(1);
    }
    pthread_detach(newunit->t_acquisition);

    //attach an id to the acqunit
    newunit->auid=ws->nb_acqunits;
    ws->nb_acqunits++;

    //return the acqunit id as a result
    res->str=malloc(2048);
    sprintf(res->str,"%d",newunit->auid);
    res->retcode=1;
    return res;
   
 }

  //********************************************
  if (!strcmp(command->name,"get_cpkt_byid_acq")) {
    //the five params are the five generic ids used freely by the uncap library

    //check the number of parameters
    if (command->nb_params<5) {
      res->retcode=0;
      res->str=malloc(4096*sizeof(char));
      sprintf(res->str,"get_cpkt_byid_acq, %d arguments given, 5 needed",command->nb_params-1);
      return res;
    }

    //extract the parameters
    id1=iohtoi(command->params[0]); //this is the auid
    id2=iohtoi(command->params[1]); //this is id1 of uncap plugin
    id3=iohtoi(command->params[2]); //this is id2 of uncap plugin
    id4=iohtoi(command->params[3]); //this is id3 of uncap plugin
    id5=iohtoi(command->params[4]); //this is id4 of uncap plugin
    printf("searching for %x %x %x %x %x :\n",id1,id2,id3,id4,id5);
    
    for(i=1;i<10;i++) { //we try 10 times
      //wait for packet to come - the more chess we have the longer we wait
      usleep(i*50000);

      //search the packet in the ctrl fifo
      current_ctrl=ws->begin_ctrl;
      while(current_ctrl!=ws->end_ctrl) {
	if (current_ctrl->id==-1) {
	  current_ctrl=current_ctrl->next;
	  continue;
	}
	if (id1==current_ctrl->auws->auid) //the auid is good
	  if ((current_ctrl->auws->select_packet_uncap)(current_ctrl->auws->uncapws,current_ctrl->generic_buffer->data,id2,id3,id4,id5)) {
	    //result found, encode and send back
	    encoded=encode_packet(current_ctrl->generic_buffer->data,current_ctrl->generic_buffer->size);
	    res->str=strdup(encoded);
	    free(encoded);
	    res->retcode=1;
	    //remove the found packet
	    current_ctrl->id=-1;
	    return res;
	  } //if found
	current_ctrl=current_ctrl->next;
      }
    }
    //Three chess, we give up
    res->str=strdup("no packet with this id");
    res->retcode=0;
    return res;
  }

  //*************************************
  if (!strcmp(command->name,"zero_stats_acq")) {
    zero_stats(ws);
    res->str=strdup("ok");
    res->retcode=1;
    return res;
  }

  //*************************************
  if (!strcmp(command->name,"start_acq")) {
    
    printf("starting acquisition\n");
    res->str=malloc(2048);
    memset(res->str,0,2048);
    if(ws->transfer_file != -1) {
      start_acquisition(ws);
      res->retcode=1;
      sprintf(res->str,"acquisition started");
    } else {
      sprintf(res->str,"unknown directory : %s",ws->datadir);
      res->retcode=0;
    }
    return res;
  }

  //*************************************
  if (!strcmp(command->name,"stop_acq")) {
    printf("stoping acquisition\n");
    stop_acquisition(ws);
    res->str=strdup("acquisition stopped");
    res->retcode=1;
    return res;
  }

  //*************************************
  if (!strcmp(command->name,"set_refclock_acq")) {
    if (command->nb_params<1) {
      res->retcode=0;
      res->str=malloc(4096*sizeof(char));
      sprintf(res->str,"set_refclock_acq, %d arguments given, 1 needed",command->nb_params-1);
      return res;
    }

    strcpy(ws->refclock,command->params[0]);
    
    //return result
    res->str=strdup("clock set");
    res->retcode=1;
    return res;
  }

  //*************************************
  if (!strcmp(command->name,"inject_data_acq")) {
    printf("injecting data\n");
    
    if (command->nb_params<2) {
      res->retcode=0;
      res->str=malloc(4096*sizeof(char));
      sprintf(res->str,"inject_data_acq, %d arguments given, 2 needed",command->nb_params-1);
      return res;
    }

    //finding the corresponding stream
    streamid=iohtoi(command->params[0]);
    if (streamid>=ws->nb_streams) {
      res->str=strdup("no stream with that id");
      res->retcode=0;
      return res;
    }

    //create a new buffer
    acq_buffer=get_generic_buffer(ws->bpool);

    //copy the data
    binary_data=decode_binary_data(command->params[1],&acq_buffer->size);
    strncpy((char *)acq_buffer->data,(const char *)binary_data,acq_buffer->size);
    free(binary_data);

    //fill a data descriptor with this packet
    insert_new_data_descriptor(ws,acq_buffer,ws->streams[streamid].acqunit,0);

    //return result
    res->str=strdup("data injected");
    res->retcode=1;
    return res;
  }


  //*************************************
  if (!strcmp(command->name,"get_stats_acq")) {
    sres=get_stats(ws);
    res->str=sres;
    res->retcode=1;
    return res;
  }

  //*************************************
  if (!strcmp(command->name,"flush_files_acq")) {
    printf("flushing files\n");
    if (get_acqstate(ws)!=0) {
      res->str=strdup("acquisition is still active, cant flush");
      res->retcode=0;
      return res;
    }
    if (!strcmp(command->params[0],"")) {
      printf("no prefix given : using noname as prefix\n");
      flush_files("noname",ws);
      res->str=strdup("files flushed with prefix noname"); 
    } else {
      flush_files(command->params[0],ws);
      res->str=strdup("files flushed");
    }
    res->retcode=1;
    return res;
  }

  //*************************************
  if (!strcmp(command->name,"start_shmem_acq")) {
    ws->active_shmem=1;
    res->retcode=1;
    res->str=strdup("Shared memory active"); 
    return res;
  }

  //*************************************
  if (!strcmp(command->name,"stop_shmem_acq")) {
    ws->active_shmem=0;
    res->retcode=1;
    res->str=strdup("Shared memory inactive"); 
    return res;
  }

  //*************************************
  if (!strcmp(command->name,"start_bsched_acq")) {
    ws->bsched_active=1;
    res->retcode=1;
    res->str=strdup("Burst scheduler active"); 
    return res;
  }

  //*************************************
  if (!strcmp(command->name,"stop_bsched_acq")) {
    ws->bsched_active=0;
    res->retcode=1;
    res->str=strdup("Burst scheduler inactive"); 
    return res;
  }

  //*************************************
  if (!strcmp(command->name,"allow_autoflush_acq")) {
      if (command->nb_params<1) {
       res->retcode=0;
       res->str=malloc(4096*sizeof(char));
       sprintf(res->str,"allow_autoflush_acq, %d arguments given, 1 needed",command->nb_params-1);
       return res;
     }

    ws->autoflush_limit=iohtoi(command->params[0]);
    ws->autoflush_active=1;
    res->retcode=1;
    res->str=strdup("variable set"); 
    return res;
  }

 //*************************************
 if (!strcmp(command->name,"dis_autoflush_acq")) {
    ws->autoflush_active=0;
    res->retcode=1;
    res->str=strdup("variable set"); 
    return res;
  }

 //*************************************
 if (!strcmp(command->name,"allow_rawoutp_acq")) {
    ws->rawoutp_active=1;
    res->retcode=1;
    res->str=strdup("raw output active"); 
    return res;
  }

//*************************************
 if (!strcmp(command->name,"dis_rawoutp_acq")) {
    ws->rawoutp_active=0;
    res->retcode=1;
    res->str=strdup("raw output inactive"); 
    return res;
  }

 //*************************************
 res->retcode=0;
 res->str=strdup("Unknown command");
 printf("unknown command\n");
 return res; 
}


//the thread that treat the commands
void *commands(void *args) {

  struct acq_workspace *ws=(struct acq_workspace *)args;
  while(1)
    wait_for_cmd(ws->cmd_sockets,treat_cmd,ws);
  return 0;
}
