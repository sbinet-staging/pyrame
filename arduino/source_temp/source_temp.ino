#include <SPI.h>
#include <Ethernet.h>
byte mac[]={0xDE,0xAD,0xBE,0xEF,0xFE,0xED};
IPAddress iplocal(10,220,0,97);
IPAddress netmask(255,255,252,0);
IPAddress ldns(10,220,0,1);
IPAddress gateway(10,220,0,1);
EthernetServer tcpserver=EthernetServer(8001);
EthernetClient client;

void setup(){
  Serial.begin(115200);
  Ethernet.begin(mac,iplocal,ldns,gateway,netmask);
  Serial.println(Ethernet.localIP());
  tcpserver.begin();
  client=tcpserver.available();
}

void loop() {
  Serial.println("loop");
  if (!client.connected()) {
   Serial.println("getting new client");
   client=tcpserver.available();
  } else {
    Serial.print("writing to client : ");
    Serial.println(client);
    int pinvalue=analogRead(0);
    float Rthermistor=10000.0*((1023.0/(float)pinvalue)-1.0);
    float tempK=3950.0/(log(Rthermistor*120.6685)) ;
    float tempC=tempK-273.15;
    client.print(tempC);
    client.print("\n");
    Serial.println(tempC);
  }
  delay(1000);
}
