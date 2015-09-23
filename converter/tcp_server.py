#!/usr/bin/env python2
import socket,time,random
   
TCP_IP='127.0.0.1'
TCP_PORT=5005
clock=0
  
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)
while True:
    conn, addr = s.accept()
    print 'Connection address:', addr
    while True:
        try:
            expr="%d,%d,%d"%(clock,int(random.random()*10),int(random.random()*10))
            print("send %s"%(expr))
            conn.send(expr)
            clock=clock+1
            time.sleep(3)
        except:
            print("connection is closed")
            conn.close()
            break
s.close()
