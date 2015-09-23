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

import socket
import sys
import bindpyrame
  
if len(sys.argv)<4 or (len(sys.argv)<5 and sys.argv[1]=="-mo"):
    print("usage: %s [-mo] host port command [parameters]"%(sys.argv[0]))
    sys.exit(1)

if sys.argv[1]=="-mo":
    offset=0
    mo=True
else:
    offset=1
    mo=False

host=sys.argv[2-offset]
port=sys.argv[3-offset]
command=sys.argv[4-offset]
params=sys.argv[5-offset:len(sys.argv)]

try:
    table = bindpyrame.init_ports_table("/opt/pyrame/ports.txt")
    port = bindpyrame.get_port(port,table)
except Exception as e:
    print e
    sys.exit(1)

retcode,res=bindpyrame.sendcmd(host,port,*([command]+params))
if mo:
    print(res)
else:
    print("retcode=%d   res=%s"%(retcode,res))

if retcode==0:
    sys.exit(1)

sys.exit(0)
