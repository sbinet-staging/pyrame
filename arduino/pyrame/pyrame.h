

//pyrame tcp server
 EthernetServer server=EthernetServer(local_port);

//variables for command extraction 
//string read from ethernet
char command[300];
//name of the command extracted from xml
char cmd[50];
//parameters of the command extracted from xml
char *params[30];
//number of parameters extracted from xml
int nb_parameters=0;
//return string
char *retstr;
//return value
int retval;



void setup(){
  //init serial link
  Serial.begin(115200);
  Serial.println("serial initialized");
  
  // initialize the network
  Ethernet.begin(mac,iplocal,ldns,gateway,netmask);
  Serial.println(Ethernet.localIP());
  Serial.println(Ethernet.subnetMask());
  Serial.println(Ethernet.gatewayIP());

 //init ethernet server
  server.begin();
  
  //specific part init
  cli_init();
}
 

void AnalyzeTrame() {
  int cmdptr=0;
  int state=1;
  int j=0;
  int trameCar=-1;
  char c;
  int nbp=-1;
  char param[255];
  nb_parameters=-1;

  Serial.println("analysetrame");
  Serial.print(strlen(command));
  Serial.println("bytes");
  Serial.println(command);
  
  memset(cmd,0,50);

  do {
    // Read character by character
    trameCar+=1;
    c=command[trameCar];

    //check for malformed commands
    if ((state<5) && (c=='\n')) {
      nb_parameters=-1;
      Serial.println("malformed command");
      return;
    }

    //state 1 : reading : <cmd name="
    if ((state==1) && (c=='"')) {
      //Serial.println("state 2");
      state=2; //beginning reading the name of the command
      cmdptr=0;
      continue;
    }

    //state 2 : reading the name of the cmd
    if ((state==2) && (c!='"')) {
      cmd[cmdptr] = c;
      cmdptr++;
      continue;
    }
    if ((state==2) && (c=='"') && (cmdptr!=0)) {
      command[cmdptr]=0;
      //Serial.print("cmd=");
      //Serial.println(cmd);
      //Serial.println("state 3");
      state=3;
      continue;
    }

    //state 3 : reading : ">	
    if ((state==3) && (c=='>')) {
      state=4;
      //Serial.println("State 4");
      nbp=0;
      continue;
    }


    //state 4 : reading <param> or </cmd>
    if ((state==4) && (c=='>')) {
      cmdptr=0;
      state=5;
      //Serial.println("State 5");
      continue;
    }

    //state 5 : check if new params and read its value
    if ((state==5) && (c=='\n')) { //no param
      //Serial.println("no more param");
      state=7;
    }
    if ((state==5) && (c!='<')) {
      param[cmdptr]=c; 
      cmdptr++;
      continue;
    }
    if ((state==5) && (c=='<')) {
      param[cmdptr]=0;
      //Serial.print("new parameter=");
      //Serial.println(param);
      params[nbp]=strdup(param);
      memset(param,0,255);
      nbp+=1;
      state=6;
      //Serial.println("State 6");
      continue;
    }

    //state 6 : check for new param
    if ((state==6) && (c=='\n')) {
      state=7; 
      continue;
    }
    if ((state==6) && (c=='<')) {
      //Serial.println("new parameter : goto state 4");
      state=4;
      continue;
    }
  } 
  while(state < 7);

  // state 7 : end of parsing
  //Serial.println("end of parsing");
  nb_parameters=nbp;
}


//acquire command from ethernet, call the analyse of string and then analyse of command 
void get_cmd() {
  char c;
  int cmdptr=0;
  char answer[200];

  memset(command,0,300);
  //wait for a pyrame client
  EthernetClient client = server.available();
  if (client) {
    if (client.connected()) { 
      //reading the command
      while (client.available()) {
        do {
          c = client.read();
          command[cmdptr]=c;
          cmdptr++;
          delay(10);
        } 
        while(c != '\n');
        command[cmdptr]=0;

        //analyse of the xml command
        AnalyzeTrame();

        //Serial.println("nb_params=");
        //Serial.println(nb_parameters);
        if (nb_parameters == -1) {
          //Serial.println("malformed command");
          client.println("<res retcode=\"0\">Malformed command</res>\n"); 
        } 
        else {
          treat_cmd();
          if (retstr==NULL)
            retstr=strdup("");
          sprintf(answer,"<res retcode=\"%d\">%s</res>\n",retval,retstr);
          client.print(answer);
          //freeing the answer and the parameters
          free(retstr);
          retstr=NULL;
          for (int i=0;i<nb_parameters;i++)
            free(params[i]);
        }
      }
    }
  }
}





void loop(){
  
  // Carry data throw Ethernet.
  get_cmd();
  
  //specific part loop
  cli_loop();
}

