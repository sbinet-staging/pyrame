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

import time

DEBUG = 0
if (DEBUG): import sys

def unescape_string(string):
    #return string.replace(r"\e",chr(27)).replace(r"\t",chr(9)).replace(r"\n",chr(10)).replace(r"\r",chr(13))
    return string.decode('string_escape')

def decode_bin_string(string):
    if len(string)%2!=0:
        raise Exception("data must have a length multiple of 2. Current length: %d"%(len(string)))
    result=""
    for i in range(len(string)/2):
        result += chr(int(string[2*i:2*i+2],16))
    return result

def encode_bin_string(string):
    result=""
    for c in string:
        result += "%02x"%(ord(c))
    return result

def ignore_chars(string):
    return string.replace("\0","").replace("\n","").replace("\r","")

class buses(object):
    # PURE VIRTUAL METHODS

    def init(self,conf_string):
        raise NotImplementedError

    def config(self,link_id):
        raise NotImplementedError

    def ll_send(self,link,data):
        raise NotImplementedError

    def ll_receive(self,link,bytes_to_read,timeout="undef"):
        raise NotImplementedError

    # METHODS
    def write(self,link,mode,data):
        if mode=="escaped":
            data = unescape_string(data)
        elif mode=="bin":
            try:
                data = decode_bin_string(data)
            except Exception as e:
                return 0,str(e)
        else:
            return 0,"Wrong write mode: %s" % (mode)
        # Send data
        retcode,res = self.ll_send(link,data)
        if retcode == 0:
            return 0,res
        return 1,"ok"

    def read(self,link,mode,bytes_to_read,timeout="undef"):
        retcode,res = self.ll_receive(link,bytes_to_read,timeout)
        if retcode == 0:
            return 0,res
        if mode=="ignore_chars":
            res = ignore_chars(res)
        if mode=="bin":
            res = encode_bin_string(res)
        return 1,res

    def read_until(self,link,mode,eot,timeout="undef"):
        eot_tab=[]
        if eot=="" or eot=="undef":
            return 0,"End Of Transmission (eot) parameter needed"
        for c in eot.split(","):
            eot_tab.append(unescape_string(c))
        # Set timeout
        oldtime = time.time()
        if timeout=="" or timeout=="undef":
            timeout = float(self.get_timeout(link))
        else:
            timeout = float(timeout)
        # Read until EOT
        response = ""
        found = [False]*len(eot_tab)
        while not any(found) and timeout>0:
            retcode,res = self.ll_receive(link,1)
            if retcode==0:
                return 0,res
            response += res
            timeout -= time.time() - oldtime
            oldtime = time.time()
            found = list((response[-len(c):] in eot_tab) for c in eot_tab)
        if not any(found) and timeout<=0:
            return 0,"Timeout waiting for EOT character"
        detected_eot = eot_tab[found.index(True)]
        response = response[0:-len(detected_eot)]
        if mode=="ignore_chars":
            response = ignore_chars(response)
        if mode=="bin":
            response = encode_bin_string(response)
        return 1,response

    def expect(self,link,pattern,timeout="undef"):
        # Unescape pattern
        pattern = unescape_string(pattern)
        # Set timeout
        oldtime = time.time()
        if timeout=="" or timeout=="undef":
            timeout = float(self.get_timeout(link))
        else:
            timeout = float(timeout)
        # Read until pattern
        buffer = "\x00" * len(pattern)
        while buffer != pattern and timeout >= 0:
            buffer = buffer[1:]
            res = '\x00'
            while res == '\x00' and timeout >= 0:
                try:
                    retcode,res = self.ll_receive(link,1,timeout)
                except Exception as e:
                    return 0,"Pattern not found or %s"%(e)
                if retcode == 0:
                    return 0,res
                timeout -= time.time() - oldtime
                oldtime = time.time()
            buffer += res
            if (DEBUG):
                if ord(res)<32: sys.stdout.write(" "+str(ord(res))+" ")
                else: sys.stdout.write(res)
        if timeout < 0:
            return 0,"Pattern not found"
        return 1,"Pattern found"

