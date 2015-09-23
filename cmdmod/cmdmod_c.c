#include "cmdmod_c.h"

//global variable workspace for external functions
struct cmdmod_ws *ws;

struct cmd_result *submod_execcmd(char * funcname,...) {
  
  struct cmd_result *cres;
  va_list pa;
  char *param;
  int nbparams=0;

  //fill the command
  struct cmd *command=malloc(sizeof(struct cmd));
  command->name=funcname;

  //get the number of params
  va_start(pa,funcname); 
  while(1) { 
    param=va_arg(pa,char *);
    if (!strcmp(param,"end")) {
      break;
    } else {  
      nbparams++;
    }
  }
  va_end(pa);

  command->nb_params=nbparams;
  command->params=(char **)malloc(nbparams*sizeof(char *));

  nbparams=0;
  //fill the command with params
  va_start(pa,funcname); 
  while(1) { 
    param=va_arg(pa,char *);
    if (!strcmp(param,"end")) {
      break;
    } else {  
      command->params[nbparams]=param;
      nbparams++;
    }
  }
  va_end(pa);
  
  cres=treat_cmd(command,ws);
  free(command->params);
  free(command);
  return cres;
}

void submod_setres(int retcode, char *retstr) {
  ws->ret_store->retcode=retcode;
   if (ws->ret_store->str != NULL)
    free(ws->ret_store->str);
  ws->ret_store->str=strdup(retstr);
}


void *init_c(struct cmdmod_ws *cws) {
  /* this function is called by cmdmod if language is c
     cws is the cmdmod workspace
  */

  void * (*dlfunc)();
  ws=cws;

  //create the language specific workspace
  struct c_ws *lcws=malloc(sizeof(struct c_ws));
  memset(lcws,0,sizeof(struct c_ws));

  //load the code file
  lcws->lib=dlopen(ws->code_file_name,RTLD_NOW|RTLD_GLOBAL);
  if (!lcws->lib) {
    debug("Error with dlopen : %s, unable to open %s\n",dlerror(),ws->code_file_name);
    exit(1);
  }

  //calling the init function if present to initialize the module workspace
  dlfunc=dlsym(lcws->lib,"init");
  if (!dlfunc) {
    debug("No init function found\n");
    lcws->mod_ws=NULL; 
  } else {
    lcws->mod_ws=dlfunc();
  }

  return (void *)lcws;
}


int exec_command_c(struct cmd *command,struct function *func) {
  /* This function is called any time a pyrame command is received by cmdmod.
     command contains the name of the pyrame command and the parameters
     func contains the description of the function including its func name.
  */
  struct c_ws *lcws=(struct c_ws *)(ws->lang_spec_ws);
  int (*dlfunc)();
  dlfunc=dlsym(lcws->lib,func->name);
  if (!dlfunc) {
    debug("Error : unable to load symbol %s : %s\n",func->name,dlerror());
    return 0;
  }
  dlfunc(command,lcws->mod_ws);
  return 1;
}

