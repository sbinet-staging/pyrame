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

class mm_ki_6487_class(scpi.scpi):
    # Available channels
    channels = ["1"]

    Iranges = [2e-2,2e-3,2e-4,2e-5,2e-6,2e-7,2e-8,2e-9]

    def __init__(self):
        super(mm_ki_6487_class,self).__init__("mm_ki_6487")

    def check_range(self,range,ranges):
        retcode,res=super(mm_ki_6487_class,self).check_range(range,ranges)
        if retcode==0:
            return 0,res
        if retcode==1:
            return 1,":AUTO ON"
        if retcode==2:
            return 1," "+res

    def config(self,mm_ki_6487_id,error_check="normal"):
        command =  r"SYST:CLE\n"
        command += r"SENS:CURR:OHMS OFF\n"
        command += r"FORM:DATA ASC\n"
        command += r"FORM:ELEM ALL"
        return super(mm_ki_6487_class,self).config(mm_ki_6487_id,error_check,command)

    def reset(self,mm_ki_6487_id):
        command =  r"*RST\n"
        command += r"SYST:ZCH OFF\n"
        command += r"FORM:DATA ASC\n"
        command += r"FORM:ELEM ALL"
        return self.free_command(mm_ki_6487_id,command)
    
    def get_dc_current(self,mm_ki_6487_id,range="undef",resolution="undef"):
        #range
        retcode,res=self.check_range(range,self.Iranges)
        if retcode==0:
            return 0,res
        range=res
        conf_cmd = r"CURR:RANG{range}"
        #resolution
        retcode,res=self.check_resolution(resolution,"plc")
        if retcode in [0,3]:
            return 0,"Invalid resolution"
        resolution=res
        if retcode==1:
            resolution=5
        if retcode in [1,2]:
            conf_cmd += r"\nCURR:NPLC {resolution}"
        measure_query = r"READ?"
        retcode,res = self.measure(mm_ki_6487_id,range,resolution,self.channels[0],conf_cmd,measure_query)
        if retcode==0:
            return 0,res
        return 1,str(float(res.split(",")[0][:-1]))

# CREATE POOL ####################################################

me = mm_ki_6487_class()

# COMMANDS #######################################################

# Put serialized API in memory if not called via import
if __name__=='__main__':
    global api; api = getapi.load_api(__file__)
    scpi.submod = submod

# Functions
def getapi_mm_ki_6487():
    submod.setres(1,api)

def init_mm_ki_6487(conf_string):
    """Initialize mm_ki_6487 power supply.

    *conf_string* must include the parameter:
    
    - bus: conf_string of the underlying link module (GPIB, TCP, ...)

    Returns mm_ki_6487_id"""
    retcode,res = me.init(conf_string)
    if retcode==0:
        submod.setres(retcode,"mm_ki_6487: %s" % (res))
        return
    submod.setres(retcode,res)

def deinit_mm_ki_6487(mm_ki_6487_id):
    "Deinitialize an mm_ki_6487"
    retcode,res = me.deinit(mm_ki_6487_id)
    if retcode==0:
        submod.setres(retcode,"mm_ki_6487: %s" % (res))
        return
    submod.setres(retcode,res)

def config_mm_ki_6487(mm_ki_6487_id,error_check="normal"):
    "Configure an mm_ki_6487"
    retcode,res = me.config(mm_ki_6487_id,error_check)
    if retcode==0:
        submod.setres(retcode,"mm_ki_6487: %s" % (res))
        return
    submod.setres(retcode,res)

def inval_mm_ki_6487(mm_ki_6487_id):
    "Invalidate an mm_ki_6487"
    retcode,res = me.inval(mm_ki_6487_id)
    if retcode==0:
        submod.setres(retcode,"mm_ki_6487: %s" % (res))
        return
    submod.setres(retcode,res)

def reset_mm_ki_6487(mm_ki_6487_id):
    "Send RST signal to PS"
    retcode,res = me.reset(mm_ki_6487_id)
    if retcode==0:
        submod.setres(retcode,"mm_ki_6487: %s" % (res))
        return
    submod.setres(retcode,res)

def get_dc_current_mm_ki_6487(mm_ki_6487_id,range="undef",resolution="undef"):
    """Get DC current in Ampers.
    The optional *range* can be: auto, 2e-2, 2e-3, 2e-4, 2e-5, 2e-6, 2e-7, 2e-8 or 2e-9 Ampers. When *range* is undef or absent, it fallbacks to autorange.
    The optional *resolution* is the number of power-line cycles that will be used to integrate, followed by PLC (e.g. 10PLC). Any value comprised between 0.01 and 50 (or 60 if mains at 60Hz) is accepted. When *resolution* is undef or absent, the default value of the instrument (5 or 6) is used.
    MIN or MAX can be used for both parameters (for resolution, MAX means the highest resolution)."""
    retcode,res = me.get_dc_current(mm_ki_6487_id,range,resolution)
    if retcode==0:
        submod.setres(retcode,"mm_ki_6487: %s" % (res))
        return
    submod.setres(retcode,res)

def free_command_mm_ki_6487(mm_ki_6487_id,command):
    "Send a raw command to the PS"
    retcode,res = me.free_command(mm_ki_6487_id,command)
    if retcode==0:
        submod.setres(retcode,"mm_ki_6487: %s" % (res))
        return
    submod.setres(retcode,res)

def get_error_queue_mm_ki_6487(mm_ki_6487_id):
    "Read error queue until the end (code 0)"
    retcode,res = me.get_error_queue(mm_ki_6487_id)
    if retcode==0:
        submod.setres(retcode,"mm_ki_6487: %s" % (res))
        return
    submod.setres(retcode,res)
    
