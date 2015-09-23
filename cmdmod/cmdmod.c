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


#include "cmdmod.h"

//global variable workspace for external functions
struct cmdmod_ws *ws;

char msg_no_result[] = "no result available from script";
char msg_error_script[] = "error from script";
char msg_unknown_command[] = "unknown command and no cmod available";
char msg_unknown_in_cmod[] = "unknown command in db and cmod";


//*************************** DB FUNCTIONS ******************************

void init_func_db(struct cmdmod_ws *ws) {
  ws->db=NULL;
}


void add_new_func_db(struct cmdmod_ws *ws,struct function *new_func) {
  struct func_db *new_elem=malloc(sizeof(struct func_db));
  new_elem->func=new_func;
  new_elem->next=ws->db;
  ws->db=new_elem;
}

struct function *search_function_in_db(struct cmdmod_ws *ws,struct cmd *command) {
  struct func_db *it=ws->db;
  if (it==NULL) {
    printf("Error: function %s not found in db (db empty)\n",command->name);
    return NULL;
  }
  while(it!=NULL) {
    if (!strcmp(it->func->name,command->name))
      return it->func;
    it=it->next;
  }
  printf("Error: function %s not found in db\n",command->name);
  return NULL;
}

void debug_func(struct cmdmod_ws *ws,struct function *func) {
  debug("\n");
  if (func->name==NULL) 
    debug("function has no name\n");
  else
    debug("function name=%s\n",func->name);
  
  if (func->type==SUBMOD_TYPE_NONE) {
    debug("type=none\n");
  }
  if (func->type==SUBMOD_TYPE_HOST) {
    debug("type=host\n");
    debug("host=%s port=%d\n",func->host,func->port);
  }
  if (func->type==SUBMOD_TYPE_SCRIPT) {
   debug("type=script\n");
   debug("function=%s\n",func->funcname);
  }
  debug("\n");
}

void debug_db(struct cmdmod_ws *ws) {
  struct func_db *it=ws->db;
  while(it!=NULL) {
    debug_func(ws,it->func);
    it=it->next;
  }
}

//**************************** CMOD FUNCTIONS ***************************

struct cmod_obj *search_function_in_cmod(struct cmdmod_ws *ws,struct cmd *command) {
  struct cmod_obj *tmp;

  //searching in the cache
  tmp=ws->cmod_cache;
  while(tmp!=NULL) {
    if (!strcmp(command->name,tmp->command) && atoi(command->params[0])==tmp->id) {
      debug("found cached cmod command name=%s\n",command->name);
      return tmp;
    }
    tmp=tmp->next;
  }

  //if not found in cache -> ask the cmod
  debug("%s not found -> asking cmod\n",command->name);
  tmp=ask_cmod(ws,command);

  //cmod found nothing
  if (tmp==NULL) {
    debug("Error: cmod does not know this function\n");
    return NULL;
  }

  //chaining the new object in the cache
  tmp->next=ws->cmod_cache;
  ws->cmod_cache=tmp;
  return tmp;
}


struct cmod_obj *ask_cmod(struct cmdmod_ws *ws,struct cmd *command) {
  struct cmod_obj *res=(struct cmod_obj*)malloc(sizeof(struct cmod_obj));
  struct cmd_result *dres;
  
  //find the port of the object
  char *portname=extract_port_name(command->name);

  //if the port is cmod we return the cmod ip as cmod is unique in the system
  if (!strcmp(portname,"CMOD_PORT")) {
    res->host=ws->cmod_ip;
    res->port=ws->cmod_port;
    res->command=strdup(command->name);
    res->id=atoi(command->params[0]);
    return res;
  } else {
    res->port=get_port(portname,ws->pt);
  }

  //free the portname
  free(portname);

  //check that there is an id parameter
  if (command->nb_params==0) {
    debug("Error: no id parameter for cmod\n");
    free(res);
    return NULL;
  }

  //really ask the cmod for ip
  dres=sendcmd(ws->cmod_ip,ws->cmod_port,"get_ip_byid_cmod",command->params[0],"end");

  //not found
  if (dres->retcode==0) {
    debug("Error cant find in cmod <- %s\n",dres->str);
    free(dres->str);
    free(dres);
    free(res);
    return NULL;
  }

  //found
  res->host=strdup(dres->str);
  res->command=strdup(command->name);
  res->id=atoi(command->params[0]);
  free(dres->str);
  free(dres);
  return res;
}
  


//****************************** XML FUNCTIONS ****************************


void config_handler_start(void *data, const char *el, const char **attr) {
  /* this function is called when a begin tag is found.
     The corresponding field in the workspace is initialized.
     data is the cmdmod workspace
     el is the name of the tag
     attr is an array of the tag attributes
     We expect the first attribute to be the name.
  */
  
  struct cmdmod_ws *ws=(struct cmdmod_ws *)data;
  ws->next_data=NEXT_IGNORE;
  
  //new cmd start
  if (!strcmp(el,"cmd")) {
    ws->current_function=(struct function *)malloc(sizeof(struct function));
    memset(ws->current_function,0,sizeof(struct function));
    ws->current_function->type=SUBMOD_TYPE_NONE;
    //the first attribute should be the name of the function
    ws->current_function->name=strdup(attr[1]);
    if (!strcmp(attr[3],"host"))
      ws->current_function->type=SUBMOD_TYPE_HOST;
    if (!strcmp(attr[3],"script"))
      ws->current_function->type=SUBMOD_TYPE_SCRIPT;
  }
  
  //name start found
  if (!strcmp(el,"name")) { 
    ws->next_data=NEXT_NAME;
    free( ws->mod_name);
     ws->mod_name=malloc(1);
    * ws->mod_name=0;
  }

  //host start found
  if (!strcmp(el,"host")) { 
    ws->next_data=NEXT_HOST;
    ws->current_function->host=malloc(1);
    *ws->current_function->host=0;
  }

   //host start found
  if (!strcmp(el,"language")) { 
    ws->next_data=NEXT_LANG;
    ws->language=malloc(1);
    *ws->language=0;
  }

  //detecting deprecated port_base tag: TODO remove in the future
  if (!strcmp(el,"port_base")) {
    printf("port_base tag is deprecated: please remove it from your xml file\n");
  }

  //begin port start found
  if (!strcmp(el,"port")) {
    ws->next_data=NEXT_PORT;
    ws->current_function->portstring=malloc(1);
    *ws->current_function->portstring=0;
  }

  //begin of listen_port found
  if (!strcmp(el,"listen_port")) {
    ws->next_data=NEXT_LPORT;
     ws->listen_port=malloc(1);
    * ws->listen_port=0;
  }
  
  //begin of port_base found: deprecated -> ignore corresponding data
  if (!strcmp(el,"port_base")) {
    ws->next_data=NEXT_IGNORE;
  }

  //begin of code file found
  if (!strcmp(el,"file")) {
    ws->next_data=NEXT_FILE;
    ws->code_file_name=malloc(1);
    *ws->code_file_name=0;
  }

  //begin of function found
  if (!strcmp(el,"function")) {
    ws->next_data=NEXT_FUNC;
    ws->current_function->funcname=malloc(1);
    *ws->current_function->funcname=0;
  }
}

void config_handler_end(void *data, const char *el) {
  /* this function is called when an end tag is found
     data is the cmdmod workspace
     el is the name of the tag
  */
  
  struct cmdmod_ws *ws=(struct cmdmod_ws *)data;
  
  //next data has to be ignored until a new start is discovered
  ws->next_data=NEXT_IGNORE;

  //end of cmd found ->registering in db
  if (!strcmp(el,"cmd")) {
    if (ws->current_function->type==SUBMOD_TYPE_HOST) {
      ws->current_function->port = get_port(ws->current_function->portstring,ws->pt);
    }
    if (ws->current_function->type==SUBMOD_TYPE_SCRIPT && ws->current_function->funcname==NULL) {
      ws->current_function->funcname=ws->current_function->name;
    }
    //current function is copied in the db
    add_new_func_db(ws,ws->current_function);
  }

  //end of name found
  if (!strcmp(el,"name")) {
    output(ws,"module name: %s\n",ws->mod_name);
  }

  //end of language found
  if (!strcmp(el,"language")) {
    output(ws,"found language: %s\n",ws->language);
  }

  //end of code file found
  if (!strcmp(el,"file")) {
    output(ws,"found file: %s\n",ws->code_file_name);
  }

  return;
}

void config_handler_data(void *data,const char *value,int len) {
  /* this function is called when a data between tags is found
     the ws->next_data variable store the nature of this data
     to store it in the good place.
     data is the cmdmod workspace
     value is the data string or a part of it (if total data > 4096 bytes)
     len is the size of value
  */
  
  struct cmdmod_ws *ws=(struct cmdmod_ws *)data;
  int len0=0;
  
  switch(ws->next_data) {
    
    //module name found
  case NEXT_NAME:
    len0=strlen(ws->mod_name);
    ws->mod_name=realloc(ws->mod_name,len0+len+1);
    strncat(ws->mod_name,value,len);
    break;
    
    //host name found
  case NEXT_HOST:
    len0=strlen(ws->current_function->host);
    ws->current_function->host=realloc(ws->current_function->host,len0+len+1);
    strncat(ws->current_function->host,value,len);
    break;

    //language name found
  case NEXT_LANG:
    len0=strlen(ws->language);
    ws->language=realloc(ws->language,len0+len+1);
    strncat(ws->language,value,len);
    break;
    
    //port number found
  case NEXT_PORT:
    len0=strlen(ws->current_function->portstring);
    ws->current_function->portstring=realloc(ws->current_function->portstring,len0+len+1);
    strncat(ws->current_function->portstring,value,len);
    break;
    
    //code file found
  case NEXT_FILE:
    len0=strlen(ws->code_file_name);
    ws->code_file_name=realloc(ws->code_file_name,len0+len+1);
    strncat(ws->code_file_name,value,len);
    break;
    
    //function found
  case NEXT_FUNC:
    len0=strlen(ws->current_function->funcname);
    ws->current_function->funcname=realloc(ws->current_function->funcname,len0+len+1);
    strncat(ws->current_function->funcname,value,len);
    break;
    
    //listening port found
  case NEXT_LPORT:
    len0=strlen(ws->listen_port);
    ws->listen_port=realloc(ws->listen_port,len0+len+1);
    strncat(ws->listen_port,value,len);
    break;
  }
}

void parse_config(char * filename,struct cmdmod_ws *ws) {
  XML_Parser parser = XML_ParserCreate(NULL);
  FILE *f;
  char buf[4096]; 
  int len;
  int res;


  //preparing the parser
  ws->current_function=(struct function *)malloc(sizeof(struct function));
  memset(ws->current_function,0,sizeof(struct function));
  XML_SetUserData(parser,ws);
  XML_SetElementHandler(parser,config_handler_start,config_handler_end);
  XML_SetCharacterDataHandler(parser,config_handler_data);

  //open the xml file to parse
  f=fopen(filename,"r");
  if (f==NULL) {
    perror("fopen");
    exit(1);
  }
  
  //parsing the file
  while(!feof(f)) {
    len=fread(buf,1,4095,f);
    buf[len]=0;
    if (feof(f))
      res=XML_Parse(parser,buf,len,1);
    else
      res=XML_Parse(parser,buf,len,0);
    if (!res) {
      printf("Error %d in XML_Parse\n",XML_GetErrorCode(parser));
      printf("Error msg: %s\n",XML_ErrorString(XML_GetErrorCode(parser)));
      printf("Error buffer: %s\n",buf);
    }
  }
  XML_Parse(parser,buf,0,1);

  //freeing the parser and the file
  XML_ParserFree(parser);
  fclose(f);
}

//****************************** COMMAND FUNCTIONS ************************

struct cmd_result * treat_cmd(struct cmd *command,void *data) {
  /* this function is called any time a pyrame command is received by cmdmod or submod.execcmd is fired.
     command is the corresponding pyrame command structure
     data is the cmdmod workspace
  */
  struct cmdmod_ws* ws=(struct cmdmod_ws*)data;
  struct cmd_result *res=NULL;

  //objects for functions lookup
  struct cmod_obj* cobj;
  struct function* func;
  int funcres;
  int i;

  //search the function in the db
  func=search_function_in_db(ws,command);

  //if no func is found an no cmod is available: error message
  if (func==NULL && ws->cmod_ip==NULL) {
    debug("%s: %s\n",msg_unknown_command,command->name);
    res=malloc(sizeof(struct cmd_result));
    res->retcode=0;
    res->str=malloc(strlen(msg_unknown_command)+strlen(ws->mod_name)+strlen(command->name)+10);
    sprintf(res->str,"%s: %s: %s",ws->mod_name,msg_unknown_command,command->name);
    return res;
  }

  //searching in cmod
  if (func==NULL) {
    cobj=search_function_in_cmod(ws,command);

    //not found in cmod: error message
    if (cobj==NULL) {
      debug("%s: %s\n",msg_unknown_in_cmod,command->name);
      res=malloc(sizeof(struct cmd_result));
      res->retcode=0;
      res->str=malloc(strlen(msg_unknown_in_cmod)+strlen(ws->mod_name)+strlen(command->name)+10);
      sprintf(res->str,"%s: %s: %s",ws->mod_name,msg_unknown_in_cmod,command->name);
      return res;
    }

    //found in cmod: executing
    res=send_cmd(cobj->host,cobj->port,command);
    return res;
  }  //end of cmod
    
  //print_submod(func);
  if (func->type==SUBMOD_TYPE_SCRIPT) {
    funcres=-123456;
    ws->ret_store->retcode=0;
    ws->ret_store->str=malloc(strlen(msg_no_result)+strlen(ws->mod_name)+10);
    sprintf(ws->ret_store->str,"%s: %s",ws->mod_name,msg_no_result);

    debug("********************** NEW COMMAND *******************\n");
    debug("executing local function %s with %d params: \n",command->name,command->nb_params);
    for (i=0;i<command->nb_params;i++) {
      debug("param%d=%s \n",i,command->params[i]);
    }
      
    //execute the function in embedded language
    if (ws->language==NULL) {
      funcres=exec_command_python(command,func);
    } else {
      if (!strcmp(ws->language,"python"))
        funcres=exec_command_python(command,func);
      if (!strcmp(ws->language,"dummy"))
        funcres=exec_command_dummy(command,func);
      if (!strcmp(ws->language,"lua"))
        funcres=exec_command_lua(command,func);
      if (!strcmp(ws->language,"bash"))
        funcres=exec_command_bash(command,func);
      if (!strcmp(ws->language,"c"))
        funcres=exec_command_c(command,func);
      //unknown language detected
      if (funcres==-123456) {
        printf("unknown language %s...exiting\n",ws->language);
        exit(1);
      }
    }

    //return a result 
    res=malloc(sizeof(struct cmd_result));
    
    if (funcres<0) { //error in execution of function: error message
      res->retcode=0;
      res->str=malloc(strlen(msg_error_script)+strlen(ws->mod_name)+10);
      sprintf(res->str,"%s: %s",ws->mod_name,msg_error_script);
    } else { //funcres is fine just returning the result
      res->str=ws->ret_store->str;
      ws->ret_store->str=NULL;
      res->retcode=ws->ret_store->retcode;
    }
    debug("retcode=%d   res=%s\n",res->retcode,res->str);
    return res;
  } //end of SCRIPT COMMAND

  
  if (func->type==SUBMOD_TYPE_HOST) {
    debug("calling external function %s\n",command->name);
    res=send_cmd(func->host,func->port,command);
    //debug("retcode=%d   res=%s\n",res->retcode,res->str);
    return res;
  } //end of HOST COMMAND

  //gettimeofday(&tv,NULL);
  //printf("all finished micros=%d\n",(int)tv.tv_usec);
  if (res==NULL) {
    printf("Error: should never happen: unknown type of function\n");
    res=malloc(sizeof(struct cmd_result));
    res->retcode=0;
    res->str=strdup("unknown error");
    return res;
  } else {
    printf("Error: handled res not sent... should never happen\n");
    return res;
  }
}

//************************** OUTPUT FUNCTIONS *******************************

void output(struct cmdmod_ws *ws,const char *format, ...) {
  char timebuf[100];
  //time_t now=time(0);
  struct timeval now;
  gettimeofday(&now,NULL);
  va_list args;
  va_start(args,format);
  strftime(timebuf,100,"%H:%M:%S",localtime(&now.tv_sec));
  //sprintf(timebuf,"%s:%06d",timebuf,(int)now.tv_usec);
  if (ws->mod_name==NULL) {
    fprintf(stderr,"unknown module: %s : ",timebuf);
  } else {
    fprintf(stderr,"%s: %s : ",ws->mod_name,timebuf);
  }
  vfprintf(stderr,format,args);
  va_end(args);
}

void debug(const char *format, ...) {
#ifdef DEBUG
  va_list args;
  va_start(args,format);
  vprintf(format,args);
  va_end(args);
#endif
}

void *thread_output(void *workspace) {
  size_t tmp_s;
  char *tmp=NULL;
  struct cmdmod_ws *ws=(struct cmdmod_ws *)workspace;
  FILE *fp=fdopen(ws->pipe_out[0],"r");
  while(1) {
    while(getline(&tmp,&tmp_s,fp)!=-1) {
      output(ws,"%s",tmp);
    }
    if (tmp!=NULL) {
      free(tmp);
    }
  }
}


//************************** MAIN FUNCTION **********************************

int main(int argc,char **argv) {

  //local variables
  struct netserv_client *clients;
  unsigned short listen_port;
  pthread_t t_output; 

  //creating workspace
  ws=(struct cmdmod_ws *)malloc(sizeof(struct cmdmod_ws));
  memset(ws,0,sizeof(struct cmdmod_ws));
  ws->mod_name=strdup("unnamed module");

  //parsing arguments: TODO to be replaced by a specific args library
  if (argc<2) {
    printf("usage: %s config_file [-c cmod_ip]\n",argv[0]);
    exit(1);
  }
  if (argc>2) {
    if (strcmp(argv[2],"-c")) {
      printf("usage: %s config_file [-c cmod_ip]\n",argv[0]);
      exit(1);
    }
    if (argc>3) {
      ws->cmod_ip=strdup(argv[3]);
    } else {
      printf("usage: %s config_file [-c cmod_ip]\n",argv[0]);
      exit(1);
    }
  }


  //create a db for variables names
  init_func_db(ws);

  //init ports table
  ws->pt=init_ports_table("/opt/pyrame/ports.txt");

  //cmod port
  if (ws->cmod_ip!=NULL) {
    ws->cmod_port=get_port("CMOD_PORT",ws->pt);
  }

  //init return store
  ws->ret_store=malloc(sizeof(struct cmd_result));
  memset(ws->ret_store,0,sizeof(struct cmd_result));

  //load configuration from the xml file
  parse_config(argv[1],ws);

  //initialize the output redirection
  if (pipe(ws->pipe_out)<0) {
    printf("cant open out pipe...exiting\n");
    exit(1);
  }
  dup2(ws->pipe_out[1],STDOUT_FILENO);
  setbuf(stdout, NULL);
  
  //launch the output thread
  if (pthread_create(&t_output,NULL,thread_output,ws)<0) {
    perror("pthread_create");
    exit(1);
  }
  pthread_detach(t_output);
  
  //initialize the language (python if nothing is specified)
  if (ws->language==NULL) {
    ws->lang_spec_ws=(void *)init_python(ws);
  } else {
    if (!strcmp(ws->language,"python"))
      ws->lang_spec_ws=init_python(ws);
    if (!strcmp(ws->language,"dummy"))
      ws->lang_spec_ws=init_dummy(ws);
    if (!strcmp(ws->language,"lua"))
      ws->lang_spec_ws=init_lua(ws);
    if (!strcmp(ws->language,"bash"))
      ws->lang_spec_ws=init_bash(ws);
    if (!strcmp(ws->language,"c"))
      ws->lang_spec_ws=init_c(ws);
    if (ws->lang_spec_ws==NULL) {
      printf("unknown language %s...exiting\n",ws->language);
      exit(1);
    }
  }
  //one can add new languages here: shell or autoit linux alternative could be candidates
    
  //prepare netserv
  if (ws->listen_port!=NULL) {
    listen_port=get_port(ws->listen_port,ws->pt);
    debug("listening on port %d\n",listen_port);
    clients=first_client(start_monoport_netserv(listen_port,10));
  } else {
    printf("Error: a listening port must be defined in xml file...exiting\n");
    exit(1);
  }

  //waiting for commands
  while(1) {
    wait_for_cmd(clients,treat_cmd,(void *)ws);
  }

  return 0;
}
