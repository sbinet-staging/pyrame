#!/usr/bin/python
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

import sys,time
import socket
socket.setdefaulttimeout(None)
import xml.etree.ElementTree as ET

def open_socket(host,port):
    try:
        sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    except Exception as e:
        raise Exception("Error opening socket" + ": " + str(e))
    try:
        sock.connect((host,port))
    except Exception as e:
        raise Exception("Error connecting to %s:%s : %s" % (host, port, str(e)))
    return sock

def init_ports_table(filename):
    table = [[],[],0]
    try:
      with open(filename,"r") as ports_table_file: ports_table = ports_table_file.read().strip().split("\n")
    except Exception as e:
        raise Exception("No ports file with name" + filename + ": " + str(e))
    for line in ports_table:
        port = line.split("=")
        if len(port) != 2:
            raise Exception("Line not properly formatted : " + line)
        table[0].append(port[0])
        table[1].append(int(port[1]))
        table[2] += 1
    return table

def get_port(name,table):
    if name == "":
        return 0
    if name.isdigit(): onlydigits=1
    else: onlydigits=0
    if not onlydigits:
      for i in range(table[2]):
          if name == table[0][i]:
              return table[1][i]
      raise Exception("Port not found %s"%(name))
    else: return int(name)

def parse_result(data):
    try:
        xml = ET.fromstring(data)
    except:
        return 0,"Error parsing XML result"
    return int(xml.get("retcode")),xml.text

def get_cmd_result(sock):
    msg = ""
    buff = ""
    while (buff != '\n'):
        try:
            buff = sock.recv(1)
        except:
            return 0,"Error reading from socket"
        msg += buff
    #print("bindpyrame:obtained result : %s"%msg.rstrip())
    return parse_result(msg)

def execcmd(sock,name,*args):
    message="<cmd name=\""+name+"\">"
    for i in range(len(args)):
        message += "<param>"+args[i]+"</param>"
    message += "</cmd>"
    #print("bindpyrame:cmd=%s"%message)
    sock.sendall(message+"\n")
    retcode,res=get_cmd_result(sock)
    return retcode,res

def sendcmd(host,port,name,*args):
    #print("bindpyrame:open socket")
    sock = open_socket(host,port)
    message="<cmd name=\""+name+"\">"
    for i in range(len(args)):
        message += "<param>"+args[i]+"</param>"
    message += "</cmd>"
    #print("bindpyrame:cmd=%s"%message)
    sock.sendall(message+"\n")
    retcode,res=get_cmd_result(sock)
    if retcode==2: #wakeup case
        sock.close()
        time.sleep(1.2)
        sock = open_socket(host,port)
        sock.sendall(message+"\n")
        retcode,res=get_cmd_result(sock)
    sock.close()
    return retcode,res

__version__ = '2.0'
