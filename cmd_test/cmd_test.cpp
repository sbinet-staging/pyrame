
#include <string>
#include <string.h>
#include <iostream> 
#include <sstream>
#include "../cmdmod/cmdmod_helper.hpp"

extern "C" void void_test(struct cmd *);
void void_test(struct cmd *command) {
  std::cout<<"inside c++ void code"<<std::endl;
  submod_setres(1,strdup("void()"));
}

extern "C" void onearg_test(struct cmd *);
void onearg_test(struct cmd *command) {
  std::stringstream msg;
  if (command->nb_params!=1) {
    msg<<"1 arg needed : "<<command->nb_params<<" provided";
    submod_setres(0,(char *)msg.str().c_str());
  } else {
    
    msg<<"onearg("<<command->params[0]<<")";
    submod_setres(1,(char *)msg.str().c_str());
  }
}

extern "C" void twoargs_test(struct cmd *command);
void twoargs_test(struct cmd *command) {
  std::stringstream msg;
  if (command->nb_params!=2) {
    msg<<"2 arg needed : "<<command->nb_params<<" provided";
    submod_setres(0,(char *)msg.str().c_str());
  } else {
    msg<<"twoargs("<<command->params[0]<<","<<command->params[1]<<")";
    submod_setres(1,(char *)msg.str().c_str());
  }
}


extern "C" void fail_test(struct cmd *command);
void fail_test(struct cmd *command) {
  submod_setres(0,strdup("fail()"));
}

extern "C" void varmod_test(struct cmd *command);
void varmod_test(struct cmd *command) {
  struct cmd_result *res;
  res=submod_execcmd((char*)"setvar_varmod",(char*)"0",(char*)"x",(char*)"2",(char*)"end");
  if (res->retcode==0) {
     submod_setres(0,strdup("error"));
  } else {
    submod_setres(1,strdup("ok"));
  }
  free_cmd_result(res);
}
    
