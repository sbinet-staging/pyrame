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
  
try:
  sock = bindpyrame.open_socket(sys.argv[1],int(sys.argv[2]))
except Exception as e:
  sys.stderr.write("[ERROR] %s\n" % e)
  sys.exit(1)

sock.send(sys.argv[3]+"\n")

retcode,res = bindpyrame.get_cmd_result(sock)

print("retcode={0}   res={1}".format(retcode,res))

sock.close()

if retcode==1:
	sys.exit(0)
else:
	sys.exit(1)
