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

import sys,time
import bindpyrame

######################################################

# Connectivity parameters to power supply (ps) and multimeter/picoammeter (mm)
conf_string_ps="ki_6487(bus=gpib(bus=tcp(host=10.220.0.72),dst_addr=24))"
#conf_string_mm="mm_ki_6487(bus=gpib(bus=tcp(host=10.220.0.72),dst_addr=24))"
conf_string_mm="ag_34401a(bus=gpib(bus=tcp(host=10.220.0.72),dst_addr=22))"

# IdV parameters (base units of the SI)
v_start=0 # v_start must be < than v_end
v_end=10
v_step=0.1
stabilization_time=1
current_limit=0.001
Irange=0.01

######################################################

# Helper function
def sendcmd(*params):
    retcode,res=bindpyrame.sendcmd("localhost",*params)
    if retcode==0:
        print(res)
        sys.exit(1)
    return res

# Get ports from Pyrame table
table=bindpyrame.init_ports_table("/opt/pyrame/ports.txt")
ps_port=bindpyrame.get_port("PS_PORT",table)
mm_port=bindpyrame.get_port("MULTIMETER_PORT",table)

# Initialization of module PS and MULTIMETER
ps_id=sendcmd(ps_port,"init_ps",conf_string_ps)
mm_id=sendcmd(mm_port,"init_multimeter",conf_string_mm)

# Configure modules
sendcmd(ps_port,"config_ps",ps_id)
sendcmd(mm_port,"config_multimeter",mm_id)

# Set current limit on PS
sendcmd(ps_port,"set_current_limit_ps",ps_id,str(current_limit))

# Power on PS
sendcmd(ps_port,"power_on_ps",ps_id)

# Main loop
print("# voltage(V)   current(A)")
for v in range(int(v_start/v_step),int(v_end/v_step)+1):
    v=v*v_step
    sendcmd(ps_port,"set_voltage_ps",ps_id,str(v))
    time.sleep(stabilization_time)
    res=sendcmd(mm_port,"get_dc_current_multimeter",mm_id,str(Irange),"max")
    i=float(res)
    print("%.6e %.6e"%(v,i))

# Power off PS
sendcmd(ps_port,"power_off_ps",ps_id)

# Deinitialize modules
sendcmd(ps_port,"deinit_ps",ps_id)
sendcmd(mm_port,"deinit_multimeter",mm_id)

