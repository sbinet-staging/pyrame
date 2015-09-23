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

class la_gen8_90_class(scpi.scpi):
    # Available channels
    channels = ["1"] # one channel

    def __init__(self):
        super(la_gen8_90_class,self).__init__("la_gen8_90")

    def config(self,la_gen8_90_id,error_check="normal"):
        command = "SYST:ERR:ENAB"
        return super(la_gen8_90_class,self).config(la_gen8_90_id,error_check,command)

    def set_voltage(self,la_gen8_90_id,voltage):
        command =  r"SOUR:CURR {current:.4f}\n"
        command += r"SOUR:VOLT {voltage:.4f}"
        return super(la_gen8_90_class,self).set_voltage(la_gen8_90_id,voltage,self.channels[0],command)

    def set_current(self,la_gen8_90_id,current):
        command =  r"SOUR:VOLT {voltage:.4f}\n"
        command += r"SOUR:CURR {current:.4f}"
        return super(la_gen8_90_class,self).set_current(la_gen8_90_id,current,self.channels[0],command)

    def set_voltage_limit(self,la_gen8_90_id,voltage_limit):
        command =  r"SOUR:VOLT:PROT:LEV {ovp:.4f}\n".format(ovp=voltage_limit*1.05)
        command += r"SOUR:VOLT {voltage_limit:.4f}"
        return super(la_gen8_90_class,self).set_voltage_limit(la_gen8_90_id,voltage_limit,self.channels[0],command)

    def set_current_limit(self,la_gen8_90_id,current_limit):
        command = r"SOUR:CURR {current_limit:.4f}"
        return super(la_gen8_90_class,self).set_current_limit(la_gen8_90_id,current_limit,self.channels[0],command)

    def get_voltage(self,la_gen8_90_id):
        query = r"MEAS:VOLT?"
        return super(la_gen8_90_class,self).simple_query(la_gen8_90_id,self.channels[0],query)

    def get_current(self,la_gen8_90_id):
        query = r"MEAS:CURR?"
        return super(la_gen8_90_class,self).simple_query(la_gen8_90_id,self.channels[0],query)

    def power_on(self,la_gen8_90_id):
        command = "OUTP:STAT ON"
        return super(la_gen8_90_class,self).simple_command(la_gen8_90_id,self.channels[0],command)

    def power_off(self,la_gen8_90_id):
        command = "OUTP:STAT OFF"
        return super(la_gen8_90_class,self).simple_command(la_gen8_90_id,self.channels[0],command)

# CREATE POOL ####################################################

me = la_gen8_90_class()

# COMMANDS #######################################################

# Put serialized API in memory if not called via import
if __name__=='__main__':
    global api; api = getapi.load_api(__file__)
    scpi.submod = submod

# Functions
def getapi_la_gen8_90():
    submod.setres(1,api)

def init_la_gen8_90(conf_string):
    """Initialize la_gen8_90 power supply.

    *conf_string* must include the parameter:
    
    - bus: conf_string of the underlying link module (GPIB, TCP, ...)

    Returns la_gen8_90_id"""
    retcode,res = me.init(conf_string)
    if retcode==0:
        submod.setres(retcode,"la_gen8_90: %s" % (res))
        return
    submod.setres(retcode,res)

def deinit_la_gen8_90(la_gen8_90_id):
    "Deinitialize an la_gen8_90"
    retcode,res = me.deinit(la_gen8_90_id)
    if retcode==0:
        submod.setres(retcode,"la_gen8_90: %s" % (res))
        return
    submod.setres(retcode,res)

def config_la_gen8_90(la_gen8_90_id,error_check="normal"):
    "Configure an la_gen8_90"
    retcode,res = me.config(la_gen8_90_id,error_check)
    if retcode==0:
        submod.setres(retcode,"la_gen8_90: %s" % (res))
        return
    submod.setres(retcode,res)

def inval_la_gen8_90(la_gen8_90_id):
    "Invalidate an la_gen8_90"
    retcode,res = me.inval(la_gen8_90_id)
    if retcode==0:
        submod.setres(retcode,"la_gen8_90: %s" % (res))
        return
    submod.setres(retcode,res)

def reset_la_gen8_90(la_gen8_90_id):
    "Send RST signal to PS"
    retcode,res = me.reset(la_gen8_90_id)
    if retcode==0:
        submod.setres(retcode,"la_gen8_90: %s" % (res))
        return
    submod.setres(retcode,res)

def set_voltage_la_gen8_90(la_gen8_90_id,voltage):
    "Set voltage in Volts."
    retcode,res = me.set_voltage(la_gen8_90_id,voltage)
    if retcode==0:
        submod.setres(retcode,"la_gen8_90: %s" % (res))
        return
    submod.setres(retcode,res)

def set_current_la_gen8_90(la_gen8_90_id,current):
    "Set current in Ampers."
    retcode,res = me.set_current(la_gen8_90_id,current)
    if retcode==0:
        submod.setres(retcode,"la_gen8_90: %s" % (res))
        return
    submod.setres(retcode,res)

def set_voltage_limit_la_gen8_90(la_gen8_90_id,voltage_limit):
    "Set voltage limit in Volts. The Over Voltage Protection will be set to 105% of the supplied value."
    retcode,res = me.set_voltage_limit(la_gen8_90_id,voltage_limit)
    if retcode==0:
        submod.setres(retcode,"la_gen8_90: %s" % (res))
        return
    submod.setres(retcode,res)

def set_current_limit_la_gen8_90(la_gen8_90_id,current_limit):
    "Set current limit in Ampers."
    retcode,res = me.set_current_limit(la_gen8_90_id,current_limit)
    if retcode==0:
        submod.setres(retcode,"la_gen8_90: %s" % (res))
        return
    submod.setres(retcode,res)

def get_voltage_la_gen8_90(la_gen8_90_id):
    "Get voltage in Volts."
    retcode,res = me.get_voltage(la_gen8_90_id)
    if retcode==0:
        submod.setres(retcode,"la_gen8_90: %s" % (res))
        return
    submod.setres(retcode,res)

def get_current_la_gen8_90(la_gen8_90_id):
    "Get current in Ampers."
    retcode,res = me.get_current(la_gen8_90_id)
    if retcode==0:
        submod.setres(retcode,"la_gen8_90: %s" % (res))
        return
    submod.setres(retcode,res)

def power_on_la_gen8_90(la_gen8_90_id):
    "Turn on."
    retcode,res = me.power_on(la_gen8_90_id)
    if retcode==0:
        submod.setres(retcode,"la_gen8_90: %s" % (res))
        return
    submod.setres(retcode,res)

def power_off_la_gen8_90(la_gen8_90_id):
    "Turn off."
    retcode,res = me.power_off(la_gen8_90_id)
    if retcode==0:
        submod.setres(retcode,"la_gen8_90: %s" % (res))
        return
    submod.setres(retcode,res)

def free_command_la_gen8_90(la_gen8_90_id,command):
    "Send a raw command to the PS"
    retcode,res = me.free_command(la_gen8_90_id,command)
    if retcode==0:
        submod.setres(retcode,"la_gen8_90: %s" % (res))
        return
    submod.setres(retcode,res)

def get_error_queue_la_gen8_90(la_gen8_90_id):
    "Read error queue until the end (code 0)"
    retcode,res = me.get_error_queue(la_gen8_90_id)
    if retcode==0:
        submod.setres(retcode,"la_gen8_90: %s" % (res))
        return
    submod.setres(retcode,res)
    
