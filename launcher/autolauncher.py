#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# 
# Copyright 2012-2015 Frédéric Magniette, Miguel Rubio-Roy
# This file is part of Pyrame.
# 
# Pyrame is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Pyrame is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with Pyrame.  If not, see <http://www.gnu.org/licenses/>

import os,socket,select,time,subprocess,argparse,sys

#unbuffer stdout
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

procs={}
cmds={}
ports={}
sockets={}

#read arguments
parser = argparse.ArgumentParser(description="Auto-launch Pyrame services")
parser.add_argument("services_file",nargs="?",default="/opt/pyrame/services.txt",help="The services file containing name, port and command for all services. Defaults to /opt/pyrame/services.txt")
parser.add_argument("-c",action="store",metavar="cmod_ip",help="IP or hostname of the cmod server")
parser.add_argument("-n",action="store_const",const="1",help="Launch all services at startup")
args = parser.parse_args()

f=open(args.services_file,"r")
l=f.readline()
while l:
    l=l.strip()
    if l=="":
        continue
    tmp=l.split(None,2)
    #fill the structures
    ports[tmp[0]]=tmp[1]
    cmds[tmp[0]]=tmp[2].rstrip()
    l=f.readline()
f.close()

if args.n=="1":
    for key,p in ports.iteritems():
        print("autolauncher: launching service %s"%(key))
        proc_args=cmds[key].split(" ")
        if args.c!=None:
            proc_args=proc_args+["-c",args.c]
        try:
            proc=subprocess.Popen(proc_args,close_fds=True)
        except Exception as e:
            print("autolauncher: error launching service %s: %s"%(key,e))
            sys.exit(1)
        procs[key]=proc
        #remove the service from the list
        cmds.pop(key,None)
        #ports.pop(key,None)
        sockets.pop(key,None)
else:
    all_good=True
    #open the sockets
    for key,p in ports.iteritems():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(("",int(p)))
            s.listen(1)
            sockets[key]=s
            #print("autolauncher: waiting for service %s on port %s"%(key,p))
        except:
            all_good=False
            print("autolauncher: Warning: port %d not available: giving up"%(int(p)))
            sockets[key]=-1
    if all_good:
        print("autolauncher: Successfully listening to all Pyrame ports")

#main loop
while (True):

    #listen the socket
    input=[]
    for key,s in sockets.iteritems():
        if s!=-1:
            input.append(s)
    timeout = 1
    inputready,_,_ = select.select(input,[],[],timeout) 

    if not (inputready):
        #check if our client are still alive
        for key,p in procs.iteritems():
            if p.poll()!=None:
                print("autolauncher: the proc pid %d for service %s is dead"%(p.pid,key))
                #remove the proc from the list
                procs.pop(key,None)
                break
                
        
    #analyse who asked for a service
    for s in inputready:
        for key,refs in sockets.iteritems():
            if refs==s:
                print("autolauncher: incoming connection on service %s"%(key))

        #accept the connection
        client,address = s.accept() 

        #flush the connections
        data = client.recv(1024)
        #print("autolauncher: request=%s"%data.rstrip())
        #sending special wake-up message
        wu_msg="<res retcode=\"2\">wakeup</res>\n"
        client.send(wu_msg)
            
        #closing both socket to release the port
        client.shutdown(socket.SHUT_RDWR)
        client.close()
        s.shutdown(socket.SHUT_RDWR)
        s.close()
        #print("autolauncher: sockets closed")
        time.sleep(1)

        #launch the correponding service
        for key,sock in sockets.iteritems():
            if s==sock:
                print("autolauncher: launching service %s"%(key))
                proc_args=cmds[key].split(" ")
                if args.c!=None:
                    proc_args=proc_args+["-c",args.c]
                try:
                    proc=subprocess.Popen(proc_args,close_fds=True,stderr=sys.stdout.fileno())
                except Exception as e:
                    print("autolauncher: error launching service %s: %s"%(key,e))
                    sys.exit(1)
                procs[key]=proc
                break
       

        #remove the service from the list
        cmds.pop(key,None)
        ports.pop(key,None)
        sockets.pop(key,None)
