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

import scpi, getapi

# CLASS ##########################################################

class ag_e3631a_class(scpi.scpi):
    # Available channels
    channels = ["P6V","P25V","N25V"]

    def __init__(self):
        super(ag_e3631a_class,self).__init__("ag_e3631a")

    def set_voltage(self,ag_e3631a_id,voltage,channel):
        command =  r"INST {channel}\n"
        command += r"CURR {current:.6f}\n"
        command += r"VOLT {voltage:.6f}"
        return super(ag_e3631a_class,self).set_voltage(ag_e3631a_id,voltage,channel,command)

    def set_current(self,ag_e3631a_id,current,channel):
        command =  r"INST {channel}\n"
        command += r"VOLT {voltage:.6f}\n"
        command += r"CURR {current:.6f}"
        return super(ag_e3631a_class,self).set_current(ag_e3631a_id,current,channel,command)

    def set_voltage_limit(self,ag_e3631a_id,voltage_limit,channel):
        command =  r"INST {channel}\n"
        command += r"VOLT {voltage_limit:.6f}"
        return super(ag_e3631a_class,self).set_voltage_limit(ag_e3631a_id,voltage_limit,channel,command)

    def set_current_limit(self,ag_e3631a_id,current_limit,channel):
        command =  r"INST {channel}\n"
        command += r"CURR {current_limit:.6f}"
        return super(ag_e3631a_class,self).set_current_limit(ag_e3631a_id,current_limit,channel,command)

    def get_voltage(self,ag_e3631a_id,channel):
        query =  r"INST {channel}\n"
        query += r"MEAS:VOLT?"
        return super(ag_e3631a_class,self).simple_query(ag_e3631a_id,channel,query)

    def get_current(self,ag_e3631a_id,channel):
        query =  r"INST {channel}\n"
        query += r"MEAS:CURR?"
        return super(ag_e3631a_class,self).simple_query(ag_e3631a_id,channel,query)

    def power_on(self,ag_e3631a_id):
        command = "OUTP ON"
        return super(ag_e3631a_class,self).simple_command(ag_e3631a_id,"1-3",command)

    def power_off(self,ag_e3631a_id):
        command = "OUTP OFF"
        return super(ag_e3631a_class,self).simple_command(ag_e3631a_id,"1-3",command)

# CREATE POOL ####################################################

me = ag_e3631a_class()

# COMMANDS #######################################################

# Put serialized API in memory if not called via import
if __name__=='__main__':
    global api; api = getapi.load_api(__file__)
    scpi.submod = submod

# Functions
def getapi_ag_e3631a():
    submod.setres(1,api)

def init_ag_e3631a(conf_string):
    """Initialize ag_e3631a power supply.

    *conf_string* must include the parameter:
    
    - bus: conf_string of the underlying link module (GPIB, TCP, ...)

    Returns ag_e3631a_id"""
    retcode,res = me.init(conf_string)
    if retcode==0:
        submod.setres(retcode,"ag_e3631a: %s" % (res))
        return
    submod.setres(retcode,res)

def deinit_ag_e3631a(ag_e3631a_id):
    "Deinitialize an ag_e3631a"
    retcode,res = me.deinit(ag_e3631a_id)
    if retcode==0:
        submod.setres(retcode,"ag_e3631a: %s" % (res))
        return
    submod.setres(retcode,res)

def config_ag_e3631a(ag_e3631a_id,error_check="normal"):
    "Configure an ag_e3631a"
    retcode,res = me.config(ag_e3631a_id,error_check)
    if retcode==0:
        submod.setres(retcode,"ag_e3631a: %s" % (res))
        return
    submod.setres(retcode,res)

def inval_ag_e3631a(ag_e3631a_id):
    "Invalidate an ag_e3631a"
    retcode,res = me.inval(ag_e3631a_id)
    if retcode==0:
        submod.setres(retcode,"ag_e3631a: %s" % (res))
        return
    submod.setres(retcode,res)

def reset_ag_e3631a(ag_e3631a_id):
    "Send RST signal to PS"
    retcode,res = me.reset(ag_e3631a_id)
    if retcode==0:
        submod.setres(retcode,"ag_e3631a: %s" % (res))
        return
    submod.setres(retcode,res)

def set_voltage_ag_e3631a(ag_e3631a_id,voltage,channel):
    "Set voltage in Volts. channel can be 1 for P6V, 2 for P25V or 3 for N25V"
    retcode,res = me.set_voltage(ag_e3631a_id,voltage,channel)
    if retcode==0:
        submod.setres(retcode,"ag_e3631a: %s" % (res))
        return
    submod.setres(retcode,res)

def set_current_ag_e3631a(ag_e3631a_id,current,channel):
    "Set current in Ampers. channel can be 1 for P6V, 2 for P25V or 3 for N25"
    retcode,res = me.set_current(ag_e3631a_id,current,channel)
    if retcode==0:
        submod.setres(retcode,"ag_e3631a: %s" % (res))
        return
    submod.setres(retcode,res)

def set_voltage_limit_ag_e3631a(ag_e3631a_id,voltage_limit,channel):
    "Set voltage limit in Volts. channel can be 1 for P6V, 2 for P25V or 3 for N25V"
    retcode,res = me.set_voltage_limit(ag_e3631a_id,voltage_limit,channel)
    if retcode==0:
        submod.setres(retcode,"ag_e3631a: %s" % (res))
        return
    submod.setres(retcode,res)

def set_current_limit_ag_e3631a(ag_e3631a_id,current_limit,channel):
    "Set current limit in Ampers. channel can be 1 for P6V, 2 for P25V or 3 for N25"
    retcode,res = me.set_current_limit(ag_e3631a_id,current_limit,channel)
    if retcode==0:
        submod.setres(retcode,"ag_e3631a: %s" % (res))
        return
    submod.setres(retcode,res)

def get_voltage_ag_e3631a(ag_e3631a_id,channel):
    "Get voltage in Volts. channel can be 1 for P6V, 2 for P25V or 3 for N25"
    retcode,res = me.get_voltage(ag_e3631a_id,channel)
    if retcode==0:
        submod.setres(retcode,"ag_e3631a: %s" % (res))
        return
    submod.setres(retcode,res)

def get_current_ag_e3631a(ag_e3631a_id,channel):
    "Get current in Ampers. channel can be 1 for P6V, 2 for P25V or 3 for N25"
    retcode,res = me.get_current(ag_e3631a_id,channel)
    if retcode==0:
        submod.setres(retcode,"ag_e3631a: %s" % (res))
        return
    submod.setres(retcode,res)

def power_on_ag_e3631a(ag_e3631a_id):
    "Turn on all channels."
    retcode,res = me.power_on(ag_e3631a_id)
    if retcode==0:
        submod.setres(retcode,"ag_e3631a: %s" % (res))
        return
    submod.setres(retcode,res)

def power_off_ag_e3631a(ag_e3631a_id):
    "Turn off all channels"
    retcode,res = me.power_off(ag_e3631a_id)
    if retcode==0:
        submod.setres(retcode,"ag_e3631a: %s" % (res))
        return
    submod.setres(retcode,res)

def free_command_ag_e3631a(ag_e3631a_id,command):
    "Send a raw command to the PS"
    retcode,res = me.free_command(ag_e3631a_id,command)
    if retcode==0:
        submod.setres(retcode,"ag_e3631a: %s" % (res))
        return
    submod.setres(retcode,res)

def get_error_queue_ag_e3631a(ag_e3631a_id):
    "Read error queue until the end (code 0)"
    retcode,res = me.get_error_queue(ag_e3631a_id)
    if retcode==0:
        submod.setres(retcode,"ag_e3631a: %s" % (res))
        return
    submod.setres(retcode,res)
    
