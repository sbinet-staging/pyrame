

#include <string.h>
#include "../cmdmod/cmdmod_c.h"

void void_test(struct cmd *command,void *workspace) {
  printf("inside void c code\n");
  submod_setres(1,strdup("void()"));
}

void onearg_test(struct cmd *command,void *workspace) {
  char *msg;
  msg=malloc(strlen(command->params[0])+15);
  if (command->nb_params!=1) {
    sprintf(msg,"1 arg needed : %d provided",command->nb_params);
    submod_setres(0,msg);
  } else {
    sprintf(msg,"onearg(%s)",command->params[0]);
    submod_setres(1,msg);
  }
  free(msg);
}

void twoargs_test(struct cmd *command,void *workspace) {
  char *msg;
  msg=malloc(strlen(command->params[0])+strlen(command->params[1])+15);
  if (command->nb_params!=2) {
    sprintf(msg,"2 arg needed : %d provided",command->nb_params);
    submod_setres(0,msg);
  } else {
    sprintf(msg,"twoargs(%s,%s)",command->params[0],command->params[1]);
    submod_setres(1,msg);
  }
  free(msg);
}


void fail_test(struct cmd *command,void *workspace) {
  submod_setres(0,strdup("fail()"));
}

void varmod_test(struct cmd *command,void *workspace) {
  struct cmd_result *res;
  res=submod_execcmd("setvar_varmod","0","x","2","end");
  if (res->retcode==0) {
     submod_setres(0,strdup("error"));
  } else {
    submod_setres(1,strdup("ok"));
  }
  free_cmd_result(res);
}
