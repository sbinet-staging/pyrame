#include "cmdmod_python.h"

//global variable workspace for external functions
struct cmdmod_ws *ws;

static PyObject* submod_exec_python(PyObject *self,  PyObject *args) {
  PyObject* result;
  
  int i;
  struct cmd *command=malloc(sizeof(struct cmd));
  struct cmd_result *cres;
  int ok;

  //create a command from python args
  command->params=malloc(MAX_ARGS*sizeof(char *));
  for(i=0;i<MAX_ARGS;i++) {
    command->params[i]=NULL;
  }
  ok=PyArg_ParseTuple(args,"s|ssssssssssssssssssssssssssssss",&(command->name),&(command->params[0]),&(command->params[1]),&(command->params[2]),&(command->params[3]),&(command->params[4]),&(command->params[5]),&(command->params[6]),&(command->params[7]),&(command->params[8]),&(command->params[9]),&(command->params[10]),&(command->params[11]),&(command->params[12]),&(command->params[13]),&(command->params[14]),&(command->params[15]),&(command->params[16]),&(command->params[17]),&(command->params[18]),&(command->params[19]),&(command->params[20]),&(command->params[21]),&(command->params[22]),&(command->params[23]),&(command->params[24]),&(command->params[25]),&(command->params[26]),&(command->params[27]),&(command->params[28]),&(command->params[29]),&(command->params[30]));
  command->nb_params=0;
  for(i=0;i<MAX_ARGS;i++) {
    if (command->params[i]!=NULL) {
       command->nb_params++;
    }
  }
  if (ok==0) {
    printf("Error : cant get python function name\n");
    free(command);
    return NULL;
  } else {
    cres=treat_cmd(command,ws);
    result=Py_BuildValue("is",cres->retcode,cres->str);	
    free(command->params);
    free(command);
    free(cres->str);
    free(cres);
    return result;
  }
}

static PyObject* submod_setres_python(PyObject *self,  PyObject *args) {
  char * tmpstr;
  
  if (ws->ret_store->str != NULL) {
    free(ws->ret_store->str);
  }
  if(!PyArg_ParseTuple(args,"is",&(ws->ret_store->retcode),&(tmpstr))) {
    return NULL;
  }
  ws->ret_store->str=strdup(tmpstr);
  //debug("python result : %d %s\n",ret_store->retcode,ret_store->str);
  return Py_BuildValue("i",1);
}

void exec_file(char *filename) {
  FILE *f;
  int pyres=0;
  //sanity checks on the code file
  if (filename==NULL) {
    printf("Error : empty filename...exiting\n");
    exit(1);
  }
  f=fopen(filename,"r");
  if (f==NULL) {
    printf("Error : unable to open file %s...exiting\n",filename);
    exit(1);
  }
  //execute the code file
  pyres=PyRun_SimpleFile(f,filename);
  if (pyres<0) {
    printf("Error : syntax error in %s...exiting\n",filename);
    fclose(f);
    exit(1);
  }
  fclose(f);
}


void *init_python(struct cmdmod_ws *cws) {
  /* this function is called by cmdmod if language is NULL or python
     cws is the cmdmod workspace to save in python environment for submod.exec usage.
  */
  //saving the cmdmod workspace to global variable
  ws=cws;

  //create the language specific workspace
  struct python_ws *pws=malloc(sizeof(struct python_ws));
  memset(pws,0,sizeof(struct python_ws));
  pws->id=1234;

  //initialize the language virtual machine
  Py_Initialize();

  //register the submod functions
  Py_InitModule("submod",submodmethods);
  pws->pModule = PyImport_AddModule("__main__");
  PyRun_SimpleString("import submod");


#ifdef DEBUG
  PyRun_SimpleString("submod.DEBUG=1");
#else
  PyRun_SimpleString("submod.DEBUG=0");
#endif

  //execute the file to get the code
  exec_file(ws->code_file_name);
  return (void *)pws;
}


int exec_command_python(struct cmd *command,struct function *func) {
  /* This function is called any time a pyrame command is received by cmdmod.
     command contains the name of the pyrame command and the parameters
     func contains the description of the function including its python func name.
  */
  
  int pyres;
  char *pycommand;
  int cmdsize;
  int i;

  //formating the python command
  //TODO: try to do without strdup for pytmp
  cmdsize=strlen(func->name)+10;
  pycommand=malloc(cmdsize);
  sprintf(pycommand,"%s(",func->funcname);
  if (command->nb_params==0) {
    char* pytmp = strdup(pycommand);
    sprintf(pycommand,"%s)",pytmp);
    free(pytmp);
  }
  for(i=0;i<command->nb_params;i++) {
    cmdsize+=strlen(command->params[i])+10;
    pycommand=realloc(pycommand,cmdsize);
    char* pytmp = strdup(pycommand);
    if (i==command->nb_params-1) {
      sprintf(pycommand,"%sr\"%s\")",pytmp,command->params[i]);
    } else {
      sprintf(pycommand,"%sr\"%s\",",pytmp,command->params[i]);
    }
    free(pytmp);
  }
  //debug("final pycommand=%s\n",pycommand);

  //execute the command
  pyres=PyRun_SimpleString(pycommand);
  if (pyres<0) {
    printf("Error : syntax error in %s\n",ws->code_file_name);
  }
  if (pycommand!=NULL) {
    free(pycommand);
  }
  return pyres;
}

