#!/usr/bin/env python2 
import time
import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clock=0
server_address = ('localhost', 8003)
print >>sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)
while 1==1:
	message="%d"%(clock)
	sock.sendall(message)
	clock=clock+1
	time.sleep(0.2)
