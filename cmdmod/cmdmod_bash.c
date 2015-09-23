#include "cmdmod_bash.h"

//global variable workspace for external functions
struct cmdmod_ws *ws;

void *init_bash(struct cmdmod_ws *cws) {
  /* this function is called by cmdmod if language is bash
     cws is the cmdmod workspace
  */
  char cmd[1024];
  ws=cws;

  //create the language specific workspace
  struct bash_ws *bws=malloc(sizeof(struct bash_ws));
  memset(bws,0,sizeof(struct bash_ws));

  //creating pipes to communicate with bash
  if (pipe(bws->fds_tbash)<0) {
    printf("cant open t_pipe...exiting\n");
    exit(1);
  }
  if (pipe(bws->fds_fbash)<0) {
    printf("cant open f_pipe...exiting\n");
    exit(1);
  }

  //fork
  bws->pid=fork();
  if (bws->pid==(pid_t)0) {
    //connect standard input/output to pipes
    dup2(bws->fds_tbash[0],STDIN_FILENO);
    close(bws->fds_tbash[1]);
    dup2(bws->fds_fbash[1],STDOUT_FILENO);
    close(bws->fds_fbash[0]);
    //exec bash
    execlp ("bash", "bash", (char *)NULL);
  } else {
    //close the unnecessary pipes
    close(bws->fds_tbash[0]);
    close(bws->fds_fbash[1]);
    sprintf(cmd,". %s\n",ws->code_file_name);
    write(bws->fds_tbash[1],cmd,strlen(cmd));
  }

  return (void *)bws;
}

int exec_command_bash(struct cmd *command,struct function *func) {
  /* This function is called any time a pyrame command is received by cmdmod.
     command contains the name of the pyrame command and the parameters
     func contains the description of the function including its func name.
  */
  struct bash_ws *bws=(struct bash_ws *)(ws->lang_spec_ws);
  
  int i,j;
  char *cmd;
  int cmdsize;
  size_t buf_s = 1024;
  char *buf = malloc(sizeof(char)*buf_s);
  FILE *rfb = fdopen(bws->fds_fbash[0],"r");
  int retcode;
  char *retstr;
  int nbargs;
  struct cmd *subcommand;
  char *nextparam;
  struct cmd_result *cres;
  int treated;

  //format the command for bash
  cmdsize=strlen(command->name)+20;
  for (i=0;i<command->nb_params;i++) {
    cmdsize+=strlen(command->params[i])+5;
  }
  cmd=malloc(cmdsize);
  sprintf(cmd,"internal_execcmd %s",command->name);
  for (i=0;i<command->nb_params;i++) {
    sprintf(cmd,"%s \"%s\"",cmd,command->params[i]);
  }
  sprintf(cmd,"%s\n",cmd);
  
  //write command to bash
  write(bws->fds_tbash[1],cmd,strlen(cmd));
  free(cmd);
  
  buf[0]=0;
  while (strncmp(buf,"++_++",5)) {
    getline(&buf,&buf_s,rfb);
    treated=0;

    //treating end of transaction
    if (!strncmp(buf,"++_++",5)) {
      treated=1;
    }
    
    //treating setres
    if (!strncmp(buf,"+_+setres+_+",12)) {
      sscanf(buf+13,"%d",&retcode);
      retstr=buf+13;
      while(retstr[0]!='"') {
        retstr++;
      }
      retstr++;
      i=0;
      while(retstr[i]!='"') {
        i++;
      }
      retstr[i]=0;
      ws->ret_store->retcode=retcode;
      if (ws->ret_store->str != NULL) {
        free(ws->ret_store->str);
      }
      ws->ret_store->str=strdup(retstr);
      treated=1;
    }

    //treating execcmd
    if (!strncmp(buf,"+_+execcmd+_+",13)) {
      sscanf(buf+14,"%d",&nbargs);
      subcommand=malloc(sizeof(struct cmd));
      subcommand->nb_params=nbargs-1;
      subcommand->params=malloc((nbargs-1)*sizeof(char *));
      nextparam=buf+14;
      //go to func name
      while(nextparam[0]!=' ') {
        nextparam++;
      }
      nextparam++;
      //read the func name
      i=0;
      while(nextparam[i]!=' ') {
        i++;
      }
      nextparam[i]=0;
      subcommand->name=strdup(nextparam);
      nextparam+=i+1;
      //read arguments
      for(j=0;j<nbargs-1;j++) {
        i=0;
        while(nextparam[i]!=' ') {
          i++;
        }
        nextparam[i]=0;
        subcommand->params[j]=strdup(nextparam);
        nextparam+=i+1;
      }
      //execute the function
      cres=treat_cmd(subcommand,ws);
      //free the command
      for(i=0;i<subcommand->nb_params;i++) {
        free(subcommand->params[i]);
      }
      free(subcommand->params);
      free(subcommand->name);
      free(subcommand);
      //write the result to bash
      sprintf(cmd,"%d,%s\n",cres->retcode,cres->str);
      write(bws->fds_tbash[1],cmd,strlen(cmd));
      free_cmd_result(cres);
      treated=1;
    }

    if (!treated) {
      printf("%s",buf);
    }
    
  }
  if (buf!=NULL) {
    free(buf);
  }
  return 1;
}
