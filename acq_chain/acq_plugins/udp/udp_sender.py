#!/usr/bin/env python2
import socket
import sys

if len(sys.argv)<3:
    print("usage: %s ports message"%(sys.argv[0]))
    print("  ports is a comma-separated list of ports to send TEST to.")
    sys.exit(1)

data=sys.argv[2]
ports = sys.argv[1].split(",")
for port in ports:
    port=int(port)
    udpsocket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    print("sending '%s\\n' to port %d"%(data,port))
    addr=("localhost",port)
    udpsocket.sendto(data+"\n",addr)
    udpsocket.close()
sys.exit(0)
