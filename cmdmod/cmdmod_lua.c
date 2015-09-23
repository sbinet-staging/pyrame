/*
Copyright 2012-2014 Frédéric Magniette, Miguel Rubio-Roy
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


#include "cmdmod_lua.h"

//global variable workspace for external functions
struct cmdmod_ws *ws;

static int submod_exec_lua(lua_State *L) {
  int i;
  struct cmd *command=malloc(sizeof(struct cmd));
  struct cmd_result *cres;

  int argc=lua_gettop(L);
  //printf("submod_exec called with %d arguments\n",argc);

  //initialize the command
  command->params=malloc(MAX_ARGS*sizeof(char *));
  for(i=0;i<MAX_ARGS;i++)
    command->params[i]=NULL;

  //extract the command name
  command->name=strdup(lua_tostring(L,1));

  //extract the command params
  command->nb_params=argc-1;
  for (i=0;i<argc-1;i++) {
    command->params[i]=strdup(lua_tostring(L,i+2));
  }

  //treat the command
  cres=treat_cmd(command,ws);

  //push the result in the lua stack
  lua_pushnumber(L,cres->retcode);
  lua_pushstring(L,cres->str);

  //free the structs
  free(command->params);
  free(command);
  free(cres->str);
  free(cres);

  //return to lua
  return 1;
}




static int submod_setres_lua(lua_State *L) {

  //free the store if necessary
  if (ws->ret_store->str != NULL)
    free(ws->ret_store->str);

  //get the values from the lua stack
  ws->ret_store->retcode=luaL_checknumber(L,1);
  ws->ret_store->str=strdup(luaL_checklstring(L,2,NULL));
  lua_pop(L,2);

  //return to lua
  return 1;
}


int exec_command_lua(struct cmd *command,struct function *func) {
  int i;
  int res;
  struct lua_ws *lws=(struct lua_ws *)(ws->lang_spec_ws);

  //find the function in the lua environment
  lua_getglobal(lws->L,func->name);
  
  //pass the arguments
  for (i=0;i<command->nb_params;i++)
    lua_pushstring(lws->L,command->params[i]);
  
  if (lua_isfunction(lws->L,lua_gettop(lws->L)-command->nb_params)) {
    //call the lua function
    res=lua_pcall(lws->L,command->nb_params,0,0);
    if (res==0) {
      return 1;
    } else {
      printf("Error in running  : %s\n",lua_tostring(lws->L,-1));
      return 0;
    }
  } else {
    printf("Error : unknown function %s\n",func->name);
    return 0;
  }
}


void *init_lua(struct cmdmod_ws* workspace) {
  ws=workspace;
  FILE *f;

  //create the language specific workspace
  struct lua_ws *pws=malloc(sizeof(struct lua_ws));
  memset(pws,0,sizeof(struct lua_ws));
  pws->L=luaL_newstate();

  //load libs and submod funcs
  luaL_openlibs(pws->L);
  lua_pushcfunction(pws->L,submod_exec_lua);
  lua_setglobal(pws->L,"submod_execcmd");
  lua_pushcfunction(pws->L,submod_setres_lua);
  lua_setglobal(pws->L,"submod_setres");

  //sanity checks on the code file
  if (ws->code_file_name==NULL) {
    printf("Error : no code file specified in the xml file...exiting\n");
    exit(1);
  }
  f=fopen(ws->code_file_name,"r");
  if (f==NULL) {
    printf("Error : unable to open file %s...exiting\n",ws->code_file_name);
    fclose(f);
    exit(1);
  }
  fclose(f);

  //execute the code file
  if (luaL_loadfile(pws->L,ws->code_file_name)) {
    printf("Error : syntax error in %s...exiting\n",ws->code_file_name);
    exit(1);
  }
  if (lua_pcall(pws->L,0,LUA_MULTRET,0)) {
    printf("Error : cant execute file %s : error %s...exiting\n",ws->code_file_name,lua_tostring(pws->L,-1));
    exit(1);
  }

  return (void *)pws;
}
