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

from buses import *
from pools import *
import conf_strings, getapi

import socket
socket.setdefaulttimeout(60)

# TCP_BUS ########################################################

class tcp_bus(buses):
    def __init__(self):
        self.tcp_pool = pool()

    def init(self,conf_string):
        try:
            conf = conf_strings.parse(conf_string)
        except Exception as e:
            return 0,str(e)
        if conf.name!="tcp":
            return 0,"Invalid module name %s in conf_string. Should be tcp" % (conf.name)
        if not conf.has("host","port"):
            return 0,"A required parameter in conf_string is not present"
        host = conf.params["host"]
        port = int(conf.params["port"])
        if conf.has("timeout") and conf.params["timeout"]!="undef":
            timeout = float(conf.params["timeout"])
        else:
            timeout = socket.getdefaulttimeout()
        # Validate parameters
        if (port < 0 or port > 65535):
            return 0,"Invalid destination port: %d" % (port)
        # Add to the pool
        tcp_id = self.tcp_pool.new({"host": host, "port": port, "timeout": timeout})
        return 1,tcp_id

    def deinit(self,tcp_id):
        try:
            link = self.tcp_pool.get(tcp_id)
        except Exception as e:
            return 1,"link_%s" % (str(e))
        # Check status
        if "socket" in link:
            self.inval(tcp_id)
        try:
            self.tcp_pool.remove(tcp_id)
        except Exception as e:
            return 0,str(e)
        return 1,"ok"

    def config(self,tcp_id):
        try:
            link = self.tcp_pool.get(tcp_id)
        except Exception as e:
            return 0,"link_%s" % (str(e))
        # Check status
        if "socket" in link:
            return 0,"already configured"
        # IP address and port cannot be repeated in the pool
        found = False
        for _,l in self.tcp_pool.get_all():
            if not "canonical" in l:
                try:
                    l["canonical"] = "%s,%s"%(socket.gethostbyname(l["host"]),link["port"])
                except socket.error as e:
                    return 0,"Error resolving hostname: %s" % (str(e))
        for _,l in self.tcp_pool.get_all():
            if "socket" in l and l["canonical"] == link["canonical"]:
                if l["timeout"]!=link["timeout"]:
                    return 0,"Existing socket found but with different timeout setting"
                found = True
                break
        if found:
            link["socket"] = l["socket"]
        else:
            # Initialize TCP socket
            link["socket"] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                link["socket"].connect((link["host"],link["port"]))
            except:
                del link["socket"]
                return 0,"Error connecting to %s:%s" % (link["host"],link["port"])
        return 1,link["canonical"]

    def inval(self,tcp_id):
        try:
            link = self.tcp_pool.get(tcp_id)
        except Exception as e:
            return 0,"link_%s" % (str(e))
        # Check status
        if "socket" not in link:
            return 1,"not configured"
        # IP address and port cannot be repeated in the pool
        found = False
        for _,l in self.tcp_pool.get_all():
            if "socket" in l and l["socket"]==link["socket"]:
                found = True
                break
        if not found:
            link["socket"].close()
        del link["socket"]
        return 1,"ok"

    def write(self,tcp_id,mode,data):
        try:
            link = self.tcp_pool.get(tcp_id)
        except Exception as e:
            return 0,"link_%s" % (str(e))
        return super(tcp_bus,self).write(link,mode,data)

    def read(self,tcp_id,mode,bytes_to_read,timeout="undef"):
        try:
            link = self.tcp_pool.get(tcp_id)
        except Exception as e:
            return 0,"link_%s" % (str(e))
        return super(tcp_bus,self).read(link,mode,bytes_to_read,timeout)

    def read_until(self,tcp_id,mode,eot,timeout="undef"):
        try:
            link = self.tcp_pool.get(tcp_id)
        except Exception as e:
            return 0,"link_%s" % (str(e))
        return super(tcp_bus,self).read_until(link,mode,eot,timeout)

    def expect(self,tcp_id,pattern,timeout="undef"):
        try:
            link = self.tcp_pool.get(tcp_id)
        except Exception as e:
            return 0,"link_%s" % (str(e))
        return super(tcp_bus,self).expect(link,pattern,timeout)

    def get_timeout(self,link):
        return link["timeout"]

    def ll_send(self,link,data):
        if not "socket" in link:
            return 0,"not configured"
        try:
            if link["socket"].sendall(data) != None:
                return 0,"Error sending data %s to %s:%s" % (data,link["socket"].getpeername()[0],link["socket"].getpeername()[1])
        except Exception as e:
            return 0,"Error sending data %s to %s:%s <- %s" % (data,link["socket"].getpeername()[0],link["socket"].getpeername()[1],str(e))
        return 1,"ok"

    def ll_receive(self,link,bytes_to_read,timeout="undef"):
        if not "socket" in link:
            return 0,"not configured"
        # Set timeout
        if timeout=="" or timeout=="undef":
            link["socket"].settimeout(self.get_timeout(link))
        else:
            link["socket"].settimeout(float(timeout))
        # Read
        bytes_read = 0
        try:
            response = ""
            while bytes_read<int(bytes_to_read):
                response += link["socket"].recv(int(bytes_to_read)-bytes_read)
                bytes_read = len(response)
                #print("read so far (%d bytes): %s"%(bytes_read,response.encode("hex")))
        except socket.timeout as e:
            return 0,"TCP link at %s:%s is not responding <- %s" % (link["socket"].getpeername()[0],link["socket"].getpeername()[1],e)
        except Exception as e:
            return 0,"error at TCP link to %s:%s <- %s" % (link["socket"].getpeername()[0],link["socket"].getpeername()[1],e)
        return 1,response

# CREATE BUS POOL ################################################

bus = tcp_bus()

# COMMANDS #######################################################

# Put serialized API in memory if not called via import
if __name__ == '__main__':
    global api; api = getapi.load_api(__file__)

def getapi_tcp():
    submod.setres(1,api)

def init_tcp(conf_string):
    """Initialize a TCP link.

    *conf_string* must include:

    - host: hostname or IP address of the remote device
    - port: port on the remote device

    optionally:

    - timeout: default timeout in seconds for this link. Can be float

    Returns id of the TCP link, *tcp_id*."""
    retcode,res = bus.init(conf_string)
    if retcode==0:
        submod.setres(retcode,"tcp: %s" % (res))
        return
    submod.setres(retcode,res)

def deinit_tcp(tcp_id):
    "Deinitialize and deregister TCP link *tcp_id*."
    retcode,res = bus.deinit(tcp_id)
    if retcode==0:
        submod.setres(retcode,"tcp: %s" % (res))
        return
    submod.setres(retcode,res)

def config_tcp(tcp_id):
    "Configure tcp link *tcp_id*."
    retcode,res = bus.config(tcp_id)
    if retcode==0:
        submod.setres(retcode,"tcp: %s" % (res))
        return
    submod.setres(retcode,res)

def inval_tcp(tcp_id):
    "Invalidate configuration of tcp link *tcp_id*."
    retcode,res = bus.inval(tcp_id)
    if retcode==0:
        submod.setres(retcode,"tcp: %s" % (res))
        return
    submod.setres(retcode,res)

# WRITE ##########################################################

def write_tcp(tcp_id,data):
    "Write *data* to TCP link *tcp_id*."
    retcode,res = bus.write(tcp_id,"escaped",data)
    if retcode==0:
        submod.setres(retcode,"tcp: %s" % (res))
        return
    submod.setres(retcode,res)

def write_bin_tcp(tcp_id,data):
    "Write binary *data* to TCP link *tcp_id*. *data* is a string where each character represents 4 bits in hexadecimal base. Little endian for each group of 8 bits."
    retcode,res = bus.write(tcp_id,"bin",data)
    if retcode==0:
        submod.setres(retcode,"tcp: %s" % (res))
        return
    submod.setres(retcode,res)

# READ ###########################################################

def read_tcp(tcp_id,bytes_to_read,timeout="undef"):
    "Read up to *bytes_to_read* bytes from TCP link *tcp_id*"
    retcode,res = bus.read(tcp_id,"ignore_chars",bytes_to_read,timeout)
    if retcode==0:
        submod.setres(retcode,"tcp: %s" % (res))
        return
    submod.setres(retcode,res)

def read_bin_tcp(tcp_id,bytes_to_read,timeout="undef"):
    "Read up to *bytes_to_read* bytes from TCP link *tcp_id* in binary format. The data read is encoded by blocks of 8 bits with two hexadecimal characters little endian."
    retcode,res = bus.read(tcp_id,"bin",bytes_to_read,timeout)
    if retcode==0:
        submod.setres(retcode,"tcp: %s" % (res))
        return
    submod.setres(retcode,res)

# READ UNTIL #####################################################

def read_until_tcp(tcp_id,eot,timeout="undef"):
    "Read from TCP link *tcp_id* until a character from *eot* comma-separated list is found"
    retcode,res = bus.read_until(tcp_id,"ignore_chars",eot,timeout)
    if retcode==0:
        submod.setres(retcode,"tcp: %s" % (res))
        return
    submod.setres(retcode,res)

def read_bin_until_tcp(tcp_id,eot,timeout="undef"):
    "Read from TCP link *tcp_id* until a character from *eot* comma-separated list is found. The data read is encoded by blocks of 8 bits with two hexadecimal characters little endian."
    retcode,res = bus.read_until(tcp_id,"bin",eot,timeout)
    if retcode==0:
        submod.setres(retcode,"tcp: %s" % (res))
        return
    submod.setres(retcode,res)

# WRNRD ##########################################################

def wrnrd_tcp(tcp_id,data,bytes_to_read,timeout="undef"):
    "Write and read *data* to and from TCP link *tcp_id*"
    retcode,res = bus.write(tcp_id,"escaped",data)
    if retcode==0:
        submod.setres(retcode,"tcp: %s" % (res))
        return
    retcode,res = bus.read(tcp_id,"ignore_chars",bytes_to_read,timeout)
    if retcode==0:
        submod.setres(retcode,"tcp: %s" % (res))
        return
    submod.setres(retcode,res)

def wrnrd_bin_tcp(tcp_id,data,bytes_to_read,timeout="undef"):
    "Write and read binary *data* to and from TCP link *tcp_id*. *data* is a string where each character represents 4 bits in hexadecimal base. Little endian for each group of 8 bits."
    retcode,res = bus.write(tcp_id,"bin",data)
    if retcode==0:
        submod.setres(retcode,"tcp: %s" % (res))
        return
    retcode,res = bus.read(tcp_id,"bin",bytes_to_read,timeout)
    if retcode==0:
        submod.setres(retcode,"tcp: %s" % (res))
        return
    submod.setres(retcode,res)

# WRNRD_UNTIL ####################################################

def wrnrd_until_tcp(tcp_id,data,eot,timeout="undef"):
    "Write and read *data* to and from TCP link *tcp_id* until a character from comma-separated list *eot* is found"
    retcode,res = bus.write(tcp_id,"escaped",data)
    if retcode==0:
        submod.setres(retcode,"tcp: %s" % (res))
        return
    retcode,res = bus.read_until(tcp_id,"ignore_chars",eot,timeout)
    if retcode==0:
        submod.setres(retcode,"tcp: %s" % (res))
        return
    submod.setres(retcode,res)

def wrnrd_bin_until_tcp(tcp_id,data,eot,timeout="undef"):
    "Write and read *data* to and from TCP link *tcp_id* until a character from comma-separated list *eot* is found. *data* is a string where each character represents 4 bits in hexadecimal base. Little endian for each group of 8 bits. Read data is return in the same format."
    retcode,res = bus.write(tcp_id,"bin",data)
    if retcode==0:
        submod.setres(retcode,"tcp: %s" % (res))
        return
    retcode,res = bus.read_until(tcp_id,"bin",eot,timeout)
    if retcode==0:
        submod.setres(retcode,"tcp: %s" % (res))
        return
    submod.setres(retcode,res)

# EXPECT #########################################################

def expect_tcp(tcp_id,pattern,timeout="undef"):
    "Read data from TCP link *tcp_id* until *pattern* is found or timeout."
    retcode,res = bus.expect(tcp_id,pattern,timeout)
    if retcode==0:
        submod.setres(retcode,"tcp: %s" % (res))
        return
    submod.setres(retcode,res)


