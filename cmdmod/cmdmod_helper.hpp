struct cmd {
  char *name;
  int nb_params;
  char **params;
};

struct cmd_result {
  int retcode;
  char *str;
};

extern "C" struct cmd_result *submod_execcmd(char * funcname,...);
extern "C" void submod_setres(int retcode, char *retstr);
extern "C" void free_cmd_result(struct cmd_result *result);
