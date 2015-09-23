// Example1.cpp : Simple example for CVICPClient
//

#include <stdio.h>
#include <string.h>
#include "../vicp.h"
#include <unistd.h>

int main(int argc, char* argv[])
{
  char* command;
  char replyBuf[16];
  int count = 0;
  int i;
  printf("LeCroyVICP: Example1\n");

  struct CVICPClient * dso;
  dso = initCVICPClient();
  strcpy(dso->m_deviceAddress, "10.220.0.140");
  connectToDevice(dso);

  // send a query
  command = strdup("*CLS ; INE 1 ; *SRE 1");
  sendDataToDevice(dso, command, strlen(command), true, false, false);

  while(serialPoll(dso)) {
    command = strdup("C1:WF?");
    sendDataToDevice(dso, command, strlen(command), true, false, false);
    while (1) {
      memset(replyBuf, 0, sizeof(replyBuf));
      int bytesRead = readDataFromDevice(dso, replyBuf, sizeof(replyBuf), false);
      count += bytesRead;
      fprintf(stdout,"%6d -> %6d:  ", count-bytesRead, count-1);
      for (i=0;i<bytesRead;i++) {
        if ((unsigned char)replyBuf[i]<32 || (unsigned char)replyBuf[i]>127)
          fprintf(stdout," %02x ",(unsigned char)replyBuf[i]);
        else
          fprintf(stdout," %2c ",(unsigned char)replyBuf[i]);
      }
      fprintf(stdout,"\n");
      if (dso->m_readState != NetWaitingForData) break;
    }
    command = strdup("*CLS ; INE 1 ; *SRE 1");
    sendDataToDevice(dso, command, strlen(command), true, false, false);
  }

  return 0;
}

