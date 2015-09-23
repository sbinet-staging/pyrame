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

class ki_6487_class(scpi.scpi):
    # Available channels
    channels = ["1"]

    def __init__(self):
        super(ki_6487_class,self).__init__("ki_6487")

    def config(self,ki_6487_id,error_check="normal"):
        command =  r"SYST:CLE\n"
        command += r"SENS:CURR:OHMS OFF\n"
        command += r"FORM:DATA ASC\n"
        command += r"FORM:ELEM ALL"
        return super(ki_6487_class,self).config(ki_6487_id,error_check,command)

    def reset(self,ki_6487_id):
        command =  r"*RST\n"
        command += r"SYST:ZCH OFF\n"
        command += r"FORM:DATA ASC\n"
        command += r"FORM:ELEM ALL"
        return super(ki_6487_class,self).free_command(ki_6487_id,command)
    
    def set_voltage(self,ki_6487_id,voltage):
        voltage = float(voltage)
        if abs(voltage) < 10:
            command = r"SOUR:VOLT:RANG 10\n"
        elif abs(voltage) < 50:
            command = r"SOUR:VOLT:RANG 50\n"
        elif abs(voltage) < 505:
            command = r"SOUR:VOLT:RANG 500\n"
        else:
            return 0,"Voltage out of range"
        command += r"SOUR:VOLT:ILIM {current:.5e}\n"
        command += r"SOUR:VOLT {voltage:.5e}"
        return super(ki_6487_class,self).set_voltage(ki_6487_id,voltage,self.channels[0],command)

    def set_current_limit(self,ki_6487_id,current_limit):
        command = r"SOUR:VOLT:ILIM {current_limit:.5e}"
        return super(ki_6487_class,self).set_current_limit(ki_6487_id,current_limit,self.channels[0],command)

    def get_voltage(self,ki_6487_id):
        query = r"SOUR:VOLT:RANG?"
        retcode,res = super(ki_6487_class,self).simple_query(ki_6487_id,self.channels[0],query)
        if retcode==0:
            return 0,res
        factor = float(res)/10
        query =  r"INIT\n"
        query += r"SENS:DATA:LAT?"
        retcode,res = super(ki_6487_class,self).simple_query(ki_6487_id,self.channels[0],query)
        if retcode==0:
            return 0,res
        return 1,str(float(res.split(",")[3])*factor)

    def get_current(self,ki_6487_id):
        query =  r"INIT\n"
        query += r"SENS:DATA:LAT?"
        retcode,res = super(ki_6487_class,self).simple_query(ki_6487_id,self.channels[0],query)
        if retcode==0:
            return 0,res
        return 1,str(float(res.split(",")[0][:-1]))

    def power_on(self,ki_6487_id):
        command = "SOUR:VOLT:STAT ON"
        return super(ki_6487_class,self).free_command(ki_6487_id,command)

    def power_off(self,ki_6487_id):
        command = "SOUR:VOLT:STAT OFF"
        return super(ki_6487_class,self).free_command(ki_6487_id,command)

# CREATE POOL ####################################################

me = ki_6487_class()

# COMMANDS #######################################################

# Put serialized API in memory if not called via import
if __name__=='__main__':
    global api; api = getapi.load_api(__file__)
    scpi.submod = submod

# Functions
def getapi_ki_6487():
    submod.setres(1,api)

def init_ki_6487(conf_string):
    """Initialize ki_6487 power supply.

    *conf_string* must include the parameter:
    
    - bus: conf_string of the underlying link module (GPIB, TCP, ...)

    Returns ki_6487_id"""
    retcode,res = me.init(conf_string)
    if retcode==0:
        submod.setres(retcode,"ki_6487: %s" % (res))
        return
    submod.setres(retcode,res)

def deinit_ki_6487(ki_6487_id):
    "Deinitialize an ki_6487"
    retcode,res = me.deinit(ki_6487_id)
    if retcode==0:
        submod.setres(retcode,"ki_6487: %s" % (res))
        return
    submod.setres(retcode,res)

def config_ki_6487(ki_6487_id,error_check="normal"):
    "Configure an ki_6487"
    retcode,res = me.config(ki_6487_id,error_check)
    if retcode==0:
        submod.setres(retcode,"ki_6487: %s" % (res))
        return
    submod.setres(retcode,res)

def inval_ki_6487(ki_6487_id):
    "Invalidate an ki_6487"
    retcode,res = me.inval(ki_6487_id)
    if retcode==0:
        submod.setres(retcode,"ki_6487: %s" % (res))
        return
    submod.setres(retcode,res)

def reset_ki_6487(ki_6487_id):
    "Send RST signal to PS"
    retcode,res = me.reset(ki_6487_id)
    if retcode==0:
        submod.setres(retcode,"ki_6487: %s" % (res))
        return
    submod.setres(retcode,res)

def set_voltage_ki_6487(ki_6487_id,voltage):
    "Set voltage in Volts."
    retcode,res = me.set_voltage(ki_6487_id,voltage)
    if retcode==0:
        submod.setres(retcode,"ki_6487: %s" % (res))
        return
    submod.setres(retcode,res)

def set_voltage_limit_ki_6487(ki_6487_id,voltage_limit):
    "Set voltage limit in Volts. The Over Voltage Protection will be set to 105% of the supplied value."
    retcode,res = me.set_voltage_limit(ki_6487_id,voltage_limit)
    if retcode==0:
        submod.setres(retcode,"ki_6487: %s" % (res))
        return
    submod.setres(retcode,res)

def set_current_limit_ki_6487(ki_6487_id,current_limit):
    "Set current limit in Ampers."
    retcode,res = me.set_current_limit(ki_6487_id,current_limit)
    if retcode==0:
        submod.setres(retcode,"ki_6487: %s" % (res))
        return
    submod.setres(retcode,res)

def get_voltage_ki_6487(ki_6487_id):
    "Get voltage in Volts."
    retcode,res = me.get_voltage(ki_6487_id)
    if retcode==0:
        submod.setres(retcode,"ki_6487: %s" % (res))
        return
    submod.setres(retcode,res)

def get_current_ki_6487(ki_6487_id):
    "Get current in Ampers."
    retcode,res = me.get_current(ki_6487_id)
    if retcode==0:
        submod.setres(retcode,"ki_6487: %s" % (res))
        return
    submod.setres(retcode,res)

def power_on_ki_6487(ki_6487_id):
    "Turn on."
    retcode,res = me.power_on(ki_6487_id)
    if retcode==0:
        submod.setres(retcode,"ki_6487: %s" % (res))
        return
    submod.setres(retcode,res)

def power_off_ki_6487(ki_6487_id):
    "Turn off."
    retcode,res = me.power_off(ki_6487_id)
    if retcode==0:
        submod.setres(retcode,"ki_6487: %s" % (res))
        return
    submod.setres(retcode,res)

def free_command_ki_6487(ki_6487_id,command):
    "Send a raw command to the PS"
    retcode,res = me.free_command(ki_6487_id,command)
    if retcode==0:
        submod.setres(retcode,"ki_6487: %s" % (res))
        return
    submod.setres(retcode,res)

def get_error_queue_ki_6487(ki_6487_id):
    "Read error queue until the end (code 0)"
    retcode,res = me.get_error_queue(ki_6487_id)
    if retcode==0:
        submod.setres(retcode,"ki_6487: %s" % (res))
        return
    submod.setres(retcode,res)
    
