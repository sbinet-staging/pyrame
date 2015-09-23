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

import bindpyrame
import socket
socket.setdefaulttimeout(20)
import sys

try:
    table = bindpyrame.init_ports_table("/opt/pyrame/ports.txt")
    port = bindpyrame.get_port("TEST_PORT",table)
except Exception as e:
    print e
    sys.exit(1)

# SENDCMD
try:
    retcode,res=bindpyrame.sendcmd("localhost",port,"twoargs_test","arg1","arg2")
except Exception as e:
    print e
    sys.exit(1)
print("sendcmd: retcode=%d res=%s"%(retcode,res))

print("");

# EXECCMD
try:
    sockid = bindpyrame.open_socket("localhost",port)
    retcode,res=bindpyrame.execcmd(sockid,"twoargs_test","arg1","arg2")
except Exception as e:
    print e
    sys.exit(1)
print("execcmd: retcode=%d res=%s"%(retcode,res))
sys.exit(0)
