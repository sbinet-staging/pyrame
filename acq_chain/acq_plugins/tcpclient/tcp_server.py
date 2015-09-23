#!/usr/bin/env python2
import socket
   
TCP_IP = '127.0.0.1'
TCP_PORT = 5005
BUFFER_SIZE = 20  # Normally 1024, but we want fast response
  
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
conn, addr = s.accept()
print 'Connection address:', addr
data = conn.recv(BUFFER_SIZE)
print("received : %s"%data)
conn.send("TEST\n")  # echo
conn.close()
s.close()
