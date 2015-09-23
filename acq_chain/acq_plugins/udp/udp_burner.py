#!/usr/bin/env python2
import socket
import sys

UDPSock1=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
data = ""
for i in range(8992):
    data+="a"


print("send to port 9000")
addr=("localhost",9000)
for _ in range(1000000):
    UDPSock1.sendto(data,addr)
UDPSock1.close()

