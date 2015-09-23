#include <SPI.h>
#include <Ethernet.h>


// Network parameters
byte mac[]={0xDE,0xAD,0xBE,0xEF,0xFE,0xED};
IPAddress iplocal(10,220,0,97);
IPAddress netmask(255,255,252,0);
IPAddress ldns(10,220,0,1);
IPAddress gateway(10,220,0,1);
int local_port=9205; //tcp port for cmds

int stream=0;
EthernetServer tcpserver=EthernetServer(8001);
EthernetClient client;
#include "pyrame.h"


void cli_init() {
 stream=0; 
 tcpserver.begin();
}
 
void cli_loop() {
  //Serial.println("cli_loop");
  if (stream && client) {
    //push temperature to tcp socket
    int pinvalue=analogRead(0);
    float Rthermistor=10000.0*((1023.0/(float)pinvalue)-1.0);
    float tempK=3950.0/(log(Rthermistor*120.6685)) ;
    float tempC=tempK-273.15;
    //tcpserver.println(tempC);
    tcpserver.println(pinvalue);
  }
  delay(1000);
}

void treat_cmd() {
  int target;
  int realtarget;
  Serial.print("nb_parameters=");
  Serial.println(nb_parameters);

  if (!strcmp(cmd,"stop_stream")) {
    stream=0;
    Serial.println("Stream stopped");
    retval=1;
    return;
  }

  if (!strcmp(cmd,"start_stream")) {
    stream=1;
    Serial.println("waiting for a client");
    while(!tcpserver.available()) 
      delay(500);
    client=tcpserver.available();
    Serial.println("client connected");
    retval=1;
  }
}
