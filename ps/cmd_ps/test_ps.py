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
import sys,select,os,socket
socket.setdefaulttimeout(20)
from time import time,sleep

# If imported by getapi just exit. This is just a benchmarking script, not a module
if __name__ != '__main__': sys.exit(0)

# How-to
if len(sys.argv) < 5:
    print "Usage: %s conf_string voltage current sleep [channel]" % (sys.argv[0])
    print "where everything is in base units of the International System of Units"
    sys.exit(1)
if len(sys.argv) > 5:
    channel = sys.argv[5]
else: channel = ""

# Init
table = bindpyrame.init_ports_table("/opt/pyrame/ports.txt")
port = bindpyrame.get_port("PS_PORT",table)

retcode,res=bindpyrame.sendcmd("localhost",port,"init_ps",sys.argv[1])
if retcode==0:
    print("Error initializing PS")
    sys.exit(1)
psid = res

retcode,res=bindpyrame.sendcmd("localhost",port,"set_current_ps",psid,sys.argv[3],channel)
if retcode==0:
    print("Error setting current with sendcmd")
    retcode,res=bindpyrame.sendcmd("localhost",port,"deinit_ps",psid)
    sys.exit(1)

retcode,res=bindpyrame.sendcmd("localhost",port,"power_on_ps",psid,channel)
if retcode==0:
    print("Error powering on with sendcmd")
    retcode,res=bindpyrame.sendcmd("localhost",port,"deinit_ps",psid)
    sys.exit(1)

# Parameters
errors = 0
attempts = 0
duration = 100
repetitions = 11
sleep_time = float(sys.argv[4])
voltages = map(lambda x:x*float(sys.argv[2])/(repetitions-1),range(repetitions))

# SENDCMD
print("Starting sendcmd loop. Press any key to stop...")
for i in range(duration):
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        raw_input()
        break
    if sleep_time == 0:
        start = time()
    for voltage in voltages:
        sleep(sleep_time)
        retcode,res=bindpyrame.sendcmd("localhost",port,"set_voltage_ps",psid,str(voltage),channel)
        attempts += 1
        if retcode==0:
            print("sendcmd:{0}:{1} Error setting voltage".format(i,voltage))
            errors += 1
    if sleep_time == 0:
        print("sendcmd:{0}: Time per set_voltage_ps: {1:.06f} s".format(i,(time()-start)/repetitions))

# EXECCMD
print("Starting execcmd loop. Press any key to stop...")
sockid=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sockid.connect(('localhost',port))
for i in range(duration):
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        raw_input()
        break
    if sleep_time == 0:
        start = time()
    for voltage in voltages:
        sleep(sleep_time)
        retcode,res=bindpyrame.execcmd(sockid,"set_voltage_ps",psid,str(voltage),channel)
        attempts += 1
        if retcode==0:
            print("execcmd:{0}:{1} Error setting voltage".format(i,voltage))
            errors += 1
    if sleep_time == 0:
        print("execcmd:{0}: Time per set_voltage_ps: {1:.06f} s".format(i,(time()-start)/repetitions))

# Wrap up
print ("Number of errors = {0}/{1} ({2}%)".format(errors,attempts,float(errors)/attempts))
retcode,res=bindpyrame.execcmd(sockid,"deinit_ps",psid)
sockid.close()
if retcode==0:
    print("Error deinitializing PS")
    sys.exit(1)
