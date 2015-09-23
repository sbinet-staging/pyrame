struct conv_ws;

//converter plugin data structure
struct convlib_ws {
  struct conv_ws *cws;
  char *name;
};

//the function provided to the plugins
void new_event(struct conv_ws *ws,int block,char *time,char *space,char *data);
int request_new_data(struct conv_ws *ws,char * buffer);
void inc_stat(struct conv_ws *ws,char * stat_name,int value);
void update_clock(struct conv_ws *ws,char * new_clock);
