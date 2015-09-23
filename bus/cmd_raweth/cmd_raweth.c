/*
Copyright 2012-2015 Frédéric Magniette, Miguel Rubio-Roy
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

#include <sys/socket.h>
#include <netpacket/packet.h>
#include <net/ethernet.h>

#include "../../cmdmod/cmdmod_c.h"
#include "cmd_raweth.h"

int get_iface_index(char * name,int socket) {
  struct ifreq ifr;
  strcpy(ifr.ifr_name,name);
  if (ioctl(socket,SIOCGIFINDEX,&ifr)==-1) {
    perror("ioctl");
    return -1;
  }
  return ifr.ifr_ifindex; 
}


#define max(a,b) ((a)>(b)?(a):(b)) 

int create_rawpkt(unsigned char *dstmac,unsigned char *srcmac,unsigned short type,int datasize,unsigned char *data,unsigned char *result) {
  int i=0;
  for(i=0;i<6;i++)
    result[i]=dstmac[i];
  for(i=0;i<6;i++)
    result[i+6]=srcmac[i];
  *((unsigned short *)(result+12))=htons(type);
  for (i=0;i<datasize;i++)
    result[14+i]=data[i];
  for(i=0;i<60-14-datasize;i++)
    result[14+i+datasize]=0;
  return max(60,datasize+14);
}


int sendraw_socket()
{
  int s;
  struct sockaddr_ll mysocket;

  s=socket(AF_PACKET,SOCK_RAW,htons(ETH_P_ALL));
  if (s<0) {
    perror("socket");
    return -1;
  }

  memset(&mysocket,0,sizeof(struct sockaddr));
  mysocket.sll_family=AF_PACKET;
  mysocket.sll_protocol=htons(ETH_P_ALL);
  mysocket.sll_ifindex=0; 

  if (bind(s,(struct sockaddr *)&mysocket,sizeof(mysocket))<0) {
    perror("bind");
    close(s);
    return -1;
  } 

  return s;
  }


void print_packet(unsigned char * data,int datalen) {
  int i;
  for (i=0;i<datalen;i++)
    printf("%x ",data[i]);
  printf("\n");
}


int send_packet(int send_socket,char * interface,unsigned char * data,int datalen)
{
  int result;
  int ifindex;
  struct sockaddr_ll mysocket;

  ifindex=get_iface_index(interface,send_socket);
  if (ifindex<0) {
    printf("bad interface\n");
    return -1;
  }

  memset(&mysocket,'\0',sizeof(struct sockaddr));
  mysocket.sll_family=AF_PACKET;
  mysocket.sll_protocol=htons(ETH_P_ALL);
  mysocket.sll_ifindex=ifindex; 

  //print_packet(data,datalen);
  result=sendto(send_socket,data,datalen,0,(struct sockaddr *)&mysocket,sizeof(mysocket));
  if (result!=datalen) { 
    perror("sendto");
  }
  return result;
}

unsigned char *parse_mac(char *input) {
  int i;
  unsigned char *result=malloc(sizeof(unsigned char)*6);
  unsigned char lp;
  unsigned char hp;
  int ptr=0;

  //printf("input=%s\n",input);

  for(i=0;i<6;i++) {
    //printf("i=%d\n",i);

    //reading ":"
    if (i!=0) {
      if (input[ptr]!=':') {
        printf("no :\n");
        free(result);
        return NULL;
      }
      ptr++;
    }

    //reading the MSB
    hp=0xff;
    if ((input[ptr]>='0') && (input[ptr]<='9'))
      hp=input[ptr]-'0';
    if ((input[ptr]>='a') && (input[ptr]<='f'))
      hp=input[ptr]-'a'+10;
    if ((input[ptr]>='A') && (input[ptr]<='F'))
      hp=input[ptr]-'A'+10;
    if (hp==0xff) {
      printf("unknown character : %c\n",input[ptr]);
      free(result);
      return NULL;
    }
    ptr++;
    
    //reading the LSB
    lp=0xff;
    if ((input[ptr]>='0') && (input[ptr]<='9'))
      lp=input[ptr]-'0';
    if ((input[ptr]>='a') && (input[ptr]<='f'))
      lp=input[ptr]-'a'+10;
    if ((input[ptr]>='A') && (input[ptr]<='F'))
      lp=input[ptr]-'A'+10;
    if (lp==0xff) {
      printf("unknown character : %c (%d)\n",input[ptr],input[ptr]);
      free(result);
      return NULL;
    }
    ptr++;

    //assembling
    //printf("assembling %x and %x\n",hp,lp);
    result[i]=hp*16+lp;
    //printf("result[%d]=%x\n",i,result[i]); 
  }
  return result;
}


//string representation of data : octets are separated by ,
//octets can be represented in decimal, octal (with leading 0) or hexadecimal (with leading 0x)
//example : "0x45,34,056"
unsigned char *decode(char *input,int *size) {
  //bad hack
  int lsize=strlen(input);
  unsigned char *result=malloc(sizeof(unsigned char)*lsize);
  int i;
  char **mots=malloc(sizeof(char *)*lsize);
  int nb_mots=1;
  mots[0]=input;
  i=0;
  while(input[i]!=0) {
    i++;
    if (input[i]==',') {
      mots[nb_mots]=input+i+1;
      input[i]=0;
      nb_mots++;
      i++;
    }
  }

  //printf("fin de parsing : %d mots\n",nb_mots);
  *size=nb_mots;

  for(i=0;i<nb_mots;i++)
    result[i]=iohtoi(mots[i]);
  free(mots);
  return result;
}




unsigned char * get_mac(char *dev)
{
  unsigned char *result=malloc(6*sizeof(unsigned char));
  struct ifreq s;
  int i;
  int fd=socket(PF_INET,SOCK_DGRAM,IPPROTO_IP);
  strcpy(s.ifr_name,dev);
  if (ioctl(fd,SIOCGIFHWADDR,&s)==0) {
    for (i=0;i<6;++i)
      result[i]=(unsigned char)s.ifr_addr.sa_data[i];
  } else {
    free(result);
    close(fd);
    return NULL;
  }
  close(fd);
  return result;
}

void send_packet_raweth(struct cmd *command,void *workspace) {
  //param0 : pc_device
  //param1 : destination mac adress
  //param2 : ethernet type 
  //param3 : data

  struct raweth_ws *ws=(struct raweth_ws *)workspace;

  unsigned char packet[4096];
  unsigned short type;
  unsigned char *srcmac;
  unsigned char *dstmac;
  unsigned char *data;
  char *interface;
  int datasize;
  int size;
  int dres;
  struct cmd_result *res=malloc(sizeof(struct cmd_result));
  char *msg=malloc(4096*sizeof(char));

  //check the parameters
  if (command->nb_params<4) {
      sprintf(msg,"cant send raw packet :  %d arguments given, 4 needed",command->nb_params-1);
      submod_setres(0,msg);
    }

  //get the mac adress of the pc network interface
  interface=command->params[0];
  srcmac=get_mac(command->params[0]);
  if (srcmac==NULL) {
    sprintf(msg,"unknown network device %s",interface);
    submod_setres(0,msg);
  }

  //analyse the string of the destination mac adress 
  dstmac=parse_mac(command->params[1]);
  if (dstmac==NULL) {
    sprintf(msg,"cant send raw packet : destination mac adress %s is not in valid format",command->params[1]);
    submod_setres(0,msg);
  }

  //this is the type of the ethernet packet (formally ethernet protocol) 
  type=iohtoi(command->params[2]);

  //decode the string packet into a buffer
  data=decode(command->params[3],&datasize);
  if (data==NULL) {
    sprintf(msg,"Invalid character in data");
    submod_setres(0,msg);
  }

  //prepare the packet
  bzero(packet,4096);
  size=create_rawpkt(dstmac,srcmac,type,datasize,data,packet);
  
  //send the packet
  dres=send_packet(ws->send_socket,interface,packet,size);
  if (dres!=size) {
    sprintf(msg,res->str,"Sendto failed (%d bytes transmit)",dres);
    submod_setres(0,msg);
  }

  //if everything is ok, send the good result
  sprintf(msg,"ok");
  submod_setres(1,msg);
}

void *init() {
  struct raweth_ws *ws=malloc(sizeof(struct raweth_ws));
  ws->send_socket=sendraw_socket();
  return ws;
}
