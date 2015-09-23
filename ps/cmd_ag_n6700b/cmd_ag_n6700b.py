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

class ag_n6700b_class(scpi.scpi):
    # Available channels
    channels = ["1","2","3","4"]

    def __init__(self):
        super(ag_n6700b_class,self).__init__("ag_n6700b")

    def set_voltage(self,ag_n6700b_id,voltage,channel,slew_rate="undef"):
        if slew_rate!="undef":
            slew_rate = "MAX"
        else:
            slew_rate = "%.4f" % (slew_rate)
        command = r"SOUR:VOLT:SLEW {slew_rate}, (@{channel})\n"
        command += r"SOUR:CURR {current:.4f}, (@{channel})\n"
        command += r"SOUR:VOLT {voltage:.4f}, (@{channel})"
        return super(ag_n6700b_class,self).set_voltage(ag_n6700b_id,voltage,channel,command)

    def set_current(self,ag_n6700b_id,current,channel):
        command =  r"SOUR:VOLT {voltage:.4f}, (@{channel})\n"
        command += r"SOUR:CURR {current:.4f}, (@{channel})"
        return super(ag_n6700b_class,self).set_current(ag_n6700b_id,current,channel,command)

    def set_voltage_limit(self,ag_n6700b_id,voltage_limit,channel):
        command =  r"SOUR:VOLT:PROT:LEV {voltage_limit:.4f}, (@{channel})\n"
        command += r"SOUR:VOLT {voltage_limit:.4f}, (@{channel})"
        return super(ag_n6700b_class,self).set_voltage_limit(ag_n6700b_id,voltage_limit,channel,command)

    def set_current_limit(self,ag_n6700b_id,current_limit,channel):
        command = r"SOUR:CURR {current_limit:.4f}, (@{channel})"
        return super(ag_n6700b_class,self).set_current_limit(ag_n6700b_id,current_limit,channel,command)

    def set_rise_delay_ag_n6700b(self,ag_n6700b_id,rise_delay,channel):
        command = r"OUTP:DEL:RISE %.4f, (@{channel})" % (rise_delay)
        return super(ag_n6700b_class,self).simple_command(ag_n6700b_id,channel,command)

    def get_voltage(self,ag_n6700b_id,channel):
        query = r"MEAS:VOLT? (@{channel})"
        return super(ag_n6700b_class,self).simple_query(ag_n6700b_id,channel,query)

    def get_current(self,ag_n6700b_id,channel):
        query = r"MEAS:CURR? (@{channel})"
        return super(ag_n6700b_class,self).simple_query(ag_n6700b_id,channel,query)

    def power_on(self,ag_n6700b_id,channel):
        command = r"OUTP ON, (@{channel})"
        return super(ag_n6700b_class,self).simple_command(ag_n6700b_id,channel,command)

    def power_off(self,ag_n6700b_id,channel):
        command = r"OUTP OFF, (@{channel})"
        return super(ag_n6700b_class,self).simple_command(ag_n6700b_id,channel,command)

# CREATE POOL ####################################################

me = ag_n6700b_class()

# COMMANDS #######################################################

# Put serialized API in memory if not called via import
if __name__=='__main__':
    global api; api = getapi.load_api(__file__)
    scpi.submod = submod

# Functions
def getapi_ag_n6700b():
    submod.setres(1,api)

def init_ag_n6700b(conf_string):
    """Initialize ag_n6700b power supply.

    *conf_string* must include the parameter:
    
    - bus: conf_string of the underlying link module (GPIB, TCP, ...)

    Returns ag_n6700b_id"""
    retcode,res = me.init(conf_string)
    if retcode==0:
        submod.setres(retcode,"ag_n6700b: %s" % (res))
        return
    submod.setres(retcode,res)

def deinit_ag_n6700b(ag_n6700b_id):
    "Deinitialize an ag_n6700b"
    retcode,res = me.deinit(ag_n6700b_id)
    if retcode==0:
        submod.setres(retcode,"ag_n6700b: %s" % (res))
        return
    submod.setres(retcode,res)

def config_ag_n6700b(ag_n6700b_id,error_check="normal"):
    "Configure an ag_n6700b"
    retcode,res = me.config(ag_n6700b_id,error_check)
    if retcode==0:
        submod.setres(retcode,"ag_n6700b: %s" % (res))
        return
    submod.setres(retcode,res)

def inval_ag_n6700b(ag_n6700b_id):
    "Invalidate an ag_n6700b"
    retcode,res = me.inval(ag_n6700b_id)
    if retcode==0:
        submod.setres(retcode,"ag_n6700b: %s" % (res))
        return
    submod.setres(retcode,res)

def reset_ag_n6700b(ag_n6700b_id):
    "Send RST signal to PS"
    retcode,res = me.reset(ag_n6700b_id)
    if retcode==0:
        submod.setres(retcode,"ag_n6700b: %s" % (res))
        return
    submod.setres(retcode,res)

def set_voltage_ag_n6700b(ag_n6700b_id,voltage,channel):
    "Set voltage in Volts. channel can be 1, 2, 3 or 4."
    retcode,res = me.set_voltage(ag_n6700b_id,voltage,channel)
    if retcode==0:
        submod.setres(retcode,"ag_n6700b: %s" % (res))
        return
    submod.setres(retcode,res)

def set_current_ag_n6700b(ag_n6700b_id,current,channel):
    "Set current in Ampers. channel can be 1, 2, 3 or 4."
    retcode,res = me.set_current(ag_n6700b_id,current,channel)
    if retcode==0:
        submod.setres(retcode,"ag_n6700b: %s" % (res))
        return
    submod.setres(retcode,res)

def set_voltage_limit_ag_n6700b(ag_n6700b_id,voltage_limit,channel):
    "Set voltage limit in Volts. channel can be 1, 2, 3 or 4. Over Voltage Protection is also set."
    retcode,res = me.set_voltage_limit(ag_n6700b_id,voltage_limit,channel)
    if retcode==0:
        submod.setres(retcode,"ag_n6700b: %s" % (res))
        return
    submod.setres(retcode,res)

def set_current_limit_ag_n6700b(ag_n6700b_id,current_limit,channel):
    "Set current limit in Ampers. channel can be 1, 2, 3 or 4."
    retcode,res = me.set_current_limit(ag_n6700b_id,current_limit,channel)
    if retcode==0:
        submod.setres(retcode,"ag_n6700b: %s" % (res))
        return
    submod.setres(retcode,res)

def get_voltage_ag_n6700b(ag_n6700b_id,channel):
    "Get voltage in Volts. channel can be 1, 2, 3 or 4."
    retcode,res = me.get_voltage(ag_n6700b_id,channel)
    if retcode==0:
        submod.setres(retcode,"ag_n6700b: %s" % (res))
        return
    submod.setres(retcode,res)

def get_current_ag_n6700b(ag_n6700b_id,channel):
    "Get current in Ampers. channel can be 1, 2, 3 or 4."
    retcode,res = me.get_current(ag_n6700b_id,channel)
    if retcode==0:
        submod.setres(retcode,"ag_n6700b: %s" % (res))
        return
    submod.setres(retcode,res)

def power_on_ag_n6700b(ag_n6700b_id,channel):
    "Turn on channel. channel can be 1, 2, 3 or 4."
    retcode,res = me.power_on(ag_n6700b_id)
    if retcode==0:
        submod.setres(retcode,"ag_n6700b: %s" % (res))
        return
    submod.setres(retcode,res)

def power_off_ag_n6700b(ag_n6700b_id,channel):
    "Turn off channel. channel can be 1, 2, 3 or 4."
    retcode,res = me.power_off(ag_n6700b_id)
    if retcode==0:
        submod.setres(retcode,"ag_n6700b: %s" % (res))
        return
    submod.setres(retcode,res)

def set_rise_delay_ag_n6700b(ag_n6700_id,rise_delay,channel):
    "Set power-on (rise) delay in seconds. channel can be 1, 2, 3 or 4."
    retcode,res = me.set_rise_delay(ag_n6700b_id,rise_delay,channel)
    if retcode==0:
        submod.setres(retcode,"ag_n6700b: %s" % (res))
        return
    submod.setres(retcode,res)

def free_command_ag_n6700b(ag_n6700b_id,command):
    "Send a raw command to the PS"
    retcode,res = me.free_command(ag_n6700b_id,command)
    if retcode==0:
        submod.setres(retcode,"ag_n6700b: %s" % (res))
        return
    submod.setres(retcode,res)

def get_error_queue_ag_n6700b(ag_n6700b_id):
    "Read error queue until the end (code 0)"
    retcode,res = me.get_error_queue(ag_n6700b_id)
    if retcode==0:
        submod.setres(retcode,"ag_n6700b: %s" % (res))
        return
    submod.setres(retcode,res)
    
