#include <SPI.h>
#include <Ethernet.h>


// Network parameters
byte mac[]={0xDE,0xAD,0xBE,0xEF,0xFE,0xED};
IPAddress iplocal(10,220,0,97);
IPAddress netmask(255,255,252,0);
IPAddress ldns(10,220,0,1);
IPAddress gateway(10,220,0,1);
int local_port=9404; //tcp port for cmds

#include "pyrame.h"

//spill variables
int spill=0;
float frequency;
float duty_cycle;
int delay_high;
int delay_low;
int ledPin = 9;
int configured=0;
 
 
void cli_init() {
 spill=0; 
}
 
void cli_loop() {
  //Serial.println("cli_loop");
  //generating the spill
  if (spill) {
    //Serial.println("go high");
    digitalWrite(ledPin, HIGH);
    delay(delay_high);
    //Serial.println("go low");
    digitalWrite(ledPin, LOW);
    delay(delay_low);
  } else {
    digitalWrite(ledPin, HIGH);
  }
}



//analyse the command and its parameters
void treat_cmd() {
  Serial.print("nb_parameters=");
  Serial.println(nb_parameters);

  if (!strcmp(cmd,"init_ssc")) {
    spill=0;
    retstr=strdup("0");
    retval=1;
    return;
  }

  if (!strcmp(cmd,"deinit_ssc")) {
    spill=0;
    retstr=strdup("ok");
    retval=1;
    return;
  } 

  if (!strcmp(cmd,"configure_square_ssc")) {
    if (nb_parameters<3) {
      Serial.println("not enough arguments (3 needed)");
      retstr=strdup("not enough arguments (3 needed)");
      retval=0;
    }
    frequency=atof(params[1]);
    duty_cycle=atof(params[2]);
    Serial.print("frequency=");
    Serial.println(frequency);
    Serial.print("duty_cycle=");
    Serial.println(duty_cycle);
    delay_high=(int)(1000*(1-duty_cycle/100)*(1/frequency));
    delay_low=(int)(1000*(duty_cycle/100)*(1/frequency));
    Serial.print("delay_high=");
    Serial.println(delay_high);
    Serial.print("delay_low=");
    Serial.println(delay_low);
    spill=0;
    configured=1;
    retstr=strdup("configured");
    retval=1;
    return;
  }

  if (!strcmp(cmd,"power_on_ssc")) {
    if (!configured) {
      retstr=strdup("not configured");
      retval=0;
      return;
    } else {
      spill=1;
      retstr=strdup("ok");
      retval=1;
      return;
    }
  }

  if (!strcmp(cmd,"power_off_ssc")) {
    spill=0;
    retstr=strdup("ok");
    retval=1;
    return;
  }

  if (!strcmp(cmd,"getapi_ssc")) {
    retstr=strdup("power_on_ssc:;power_off_ssc:;configure_square_ssc:frequency,duty_cycle");
    retval=1;
    return;
  }

  Serial.println("unknown command");
  retstr=strdup("unknown command");
  retval=0;
}
