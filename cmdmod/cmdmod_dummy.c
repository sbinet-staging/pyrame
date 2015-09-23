#include "cmdmod_dummy.h"

//global variable workspace for external functions
struct cmdmod_ws *ws;

void *init_dummy(struct cmdmod_ws *cws) {
  /* this function is called by cmdmod if language is NULL or dummy
     cws is the cmdmod workspace
  */

  //printf("dummy init\n");
  ws=cws;

  //create the language specific workspace
  struct dummy_ws *dws=malloc(sizeof(struct dummy_ws));
  memset(dws,0,sizeof(struct dummy_ws));
  dws->id=1234;
  
  return (void *)dws;
}


int exec_command_dummy(struct cmd *command,struct function *func) {
  /* This function is called any time a pyrame command is received by cmdmod.
     command contains the name of the pyrame command and the parameters
     func contains the description of the function including its func name.
  */
  if (ws->ret_store->str != NULL)
    free(ws->ret_store->str);
  ws->ret_store->str=strdup("ok");
  ws->ret_store->retcode=1;
  return 1;
}

