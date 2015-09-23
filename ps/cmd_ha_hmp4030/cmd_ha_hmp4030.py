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

class ha_hmp4030_class(scpi.scpi):
    # Available channels
    channels = ["OUT1","OUT2","OUT3"]

    def __init__(self):
        super(ha_hmp4030_class,self).__init__("ha_hmp4030")

    def set_voltage(self,ha_hmp4030_id,voltage,channel):
        command =  r"INST {channel}\n"
        command += r"SOUR:CURR {current:.3f}\n"
        command += r"SOUR:VOLT {voltage:.3f}"
        return super(ha_hmp4030_class,self).set_voltage(ha_hmp4030_id,voltage,channel,command)

    def set_current(self,ha_hmp4030_id,current,channel):
        command =  r"INST {channel}\n"
        command += r"SOUR:VOLT {voltage:.3f}\n"
        command += r"SOUR:CURR {current:.3f}"
        return super(ha_hmp4030_class,self).set_current(ha_hmp4030_id,current,channel,command)

    def set_voltage_limit(self,ha_hmp4030_id,voltage_limit,channel):
        command =  r"INST {channel}\n"
        command += r"SOUR:VOLT:PROT:LEV {voltage_limit:.3f}\n"
        command += r"SOUR:VOLT {voltage_limit:.3f}"
        return super(ha_hmp4030_class,self).set_voltage_limit(ha_hmp4030_id,voltage_limit,channel,command)

    def set_current_limit(self,ha_hmp4030_id,current_limit,channel):
        command =  r"INST {channel}\n"
        command += r"SOUR:CURR {current_limit:.3f}"
        return super(ha_hmp4030_class,self).set_current_limit(ha_hmp4030_id,current_limit,channel,command)

    def get_voltage(self,ha_hmp4030_id,channel):
        query =  r"INST {channel}\n"
        query += r"MEAS:VOLT?"
        return super(ha_hmp4030_class,self).simple_query(ha_hmp4030_id,channel,query)

    def get_current(self,ha_hmp4030_id,channel):
        query =  r"INST {channel}\n"
        query += r"MEAS:CURR?"
        return super(ha_hmp4030_class,self).simple_query(ha_hmp4030_id,channel,query)

    def power_on(self,ha_hmp4030_id,channel):
        command =  r"INST {channel}\n"
        command += r"OUTP ON"
        return super(ha_hmp4030_class,self).simple_command(ha_hmp4030_id,channel,command)

    def power_off(self,ha_hmp4030_id,channel):
        command =  r"INST {channel}\n"
        command += r"OUTP OFF"
        return super(ha_hmp4030_class,self).simple_command(ha_hmp4030_id,channel,command)

# CREATE POOL ####################################################

me = ha_hmp4030_class()

# COMMANDS #######################################################

# Put serialized API in memory if not called via import
if __name__=='__main__':
    global api; api = getapi.load_api(__file__)
    scpi.submod = submod

# Functions
def getapi_ha_hmp4030():
    submod.setres(1,api)

def init_ha_hmp4030(conf_string):
    """Initialize ha_hmp4030 power supply.

    *conf_string* must include the parameter:
    
    - bus: conf_string of the underlying link module (GPIB, TCP, ...)

    Returns ha_hmp4030_id"""
    retcode,res = me.init(conf_string)
    if retcode==0:
        submod.setres(retcode,"ha_hmp4030: %s" % (res))
        return
    submod.setres(retcode,res)

def deinit_ha_hmp4030(ha_hmp4030_id):
    "Deinitialize an ha_hmp4030"
    retcode,res = me.deinit(ha_hmp4030_id)
    if retcode==0:
        submod.setres(retcode,"ha_hmp4030: %s" % (res))
        return
    submod.setres(retcode,res)

def config_ha_hmp4030(ha_hmp4030_id,error_check="normal"):
    "Configure an ha_hmp4030"
    retcode,res = me.config(ha_hmp4030_id,error_check)
    if retcode==0:
        submod.setres(retcode,"ha_hmp4030: %s" % (res))
        return
    submod.setres(retcode,res)

def inval_ha_hmp4030(ha_hmp4030_id):
    "Invalidate an ha_hmp4030"
    retcode,res = me.inval(ha_hmp4030_id)
    if retcode==0:
        submod.setres(retcode,"ha_hmp4030: %s" % (res))
        return
    submod.setres(retcode,res)

def reset_ha_hmp4030(ha_hmp4030_id):
    "Send RST signal to PS"
    retcode,res = me.reset(ha_hmp4030_id)
    if retcode==0:
        submod.setres(retcode,"ha_hmp4030: %s" % (res))
        return
    submod.setres(retcode,res)

def set_voltage_ha_hmp4030(ha_hmp4030_id,voltage,channel):
    "Set voltage in Volts. channel can be 1, 2 or 3."
    retcode,res = me.set_voltage(ha_hmp4030_id,voltage,channel)
    if retcode==0:
        submod.setres(retcode,"ha_hmp4030: %s" % (res))
        return
    submod.setres(retcode,res)

def set_current_ha_hmp4030(ha_hmp4030_id,current,channel):
    "Set current in Ampers. channel can be 1, 2 or 3."
    retcode,res = me.set_current(ha_hmp4030_id,current,channel)
    if retcode==0:
        submod.setres(retcode,"ha_hmp4030: %s" % (res))
        return
    submod.setres(retcode,res)

def set_voltage_limit_ha_hmp4030(ha_hmp4030_id,voltage_limit,channel):
    "Set voltage limit in Volts. channel can be 1, 2 or 3. Over Voltage Protection is also set."
    retcode,res = me.set_voltage_limit(ha_hmp4030_id,voltage_limit,channel)
    if retcode==0:
        submod.setres(retcode,"ha_hmp4030: %s" % (res))
        return
    submod.setres(retcode,res)

def set_current_limit_ha_hmp4030(ha_hmp4030_id,current_limit,channel):
    "Set current limit in Ampers. channel can be 1, 2 or 3."
    retcode,res = me.set_current_limit(ha_hmp4030_id,current_limit,channel)
    if retcode==0:
        submod.setres(retcode,"ha_hmp4030: %s" % (res))
        return
    submod.setres(retcode,res)

def get_voltage_ha_hmp4030(ha_hmp4030_id,channel):
    "Get voltage in Volts. channel can be 1, 2 or 3."
    retcode,res = me.get_voltage(ha_hmp4030_id,channel)
    if retcode==0:
        submod.setres(retcode,"ha_hmp4030: %s" % (res))
        return
    submod.setres(retcode,res)

def get_current_ha_hmp4030(ha_hmp4030_id,channel):
    "Get current in Ampers. channel can be 1, 2 or 3."
    retcode,res = me.get_current(ha_hmp4030_id,channel)
    if retcode==0:
        submod.setres(retcode,"ha_hmp4030: %s" % (res))
        return
    submod.setres(retcode,res)

def power_on_ha_hmp4030(ha_hmp4030_id):
    "Turn on all channels."
    retcode,res = me.power_on(ha_hmp4030_id)
    if retcode==0:
        submod.setres(retcode,"ha_hmp4030: %s" % (res))
        return
    submod.setres(retcode,res)

def power_off_ha_hmp4030(ha_hmp4030_id):
    "Turn off all channels"
    retcode,res = me.power_off(ha_hmp4030_id)
    if retcode==0:
        submod.setres(retcode,"ha_hmp4030: %s" % (res))
        return
    submod.setres(retcode,res)

def free_command_ha_hmp4030(ha_hmp4030_id,command):
    "Send a raw command to the PS"
    retcode,res = me.free_command(ha_hmp4030_id,command)
    if retcode==0:
        submod.setres(retcode,"ha_hmp4030: %s" % (res))
        return
    submod.setres(retcode,res)

def get_error_queue_ha_hmp4030(ha_hmp4030_id):
    "Read error queue until the end (code 0)"
    retcode,res = me.get_error_queue(ha_hmp4030_id)
    if retcode==0:
        submod.setres(retcode,"ha_hmp4030: %s" % (res))
        return
    submod.setres(retcode,res)
    
