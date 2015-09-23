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

class ag_34401a_class(scpi.scpi):
    # Available channels
    channels = ["1"] # one channel

    Vranges = [0.1,1,10,100,1000]
    Iranges = [10e-3,100e-3,1,3]
    Rranges = [100,1e3,10e3,100e3,1e6,10e6,100e6]

    def __init__(self):
        super(ag_34401a_class,self).__init__("ag_34401a")

    def check_range(self,range,ranges):
        retcode,res=super(ag_34401a_class,self).check_range(range,ranges)
        if retcode==0:
            return 0,res
        if retcode==1:
            return 1,":AUTO ON"
        if retcode==2:
            return 1," "+res

    def get_dc_voltage(self,ag_34401a_id,range="undef",resolution="undef"):
        conf_cmd = r"CONF:VOLT:DC\n"
        #range
        retcode,res=self.check_range(range,self.Vranges)
        if retcode==0:
            return 0,res
        range=res
        conf_cmd += r"VOLT:DC:RANG{range}"
        #resolution
        retcode,res=self.check_resolution(resolution,"plc")
        if retcode==0:
            return 0,res
        resolution=res
        if retcode==2:
            conf_cmd += r"\nVOLT:DC:NPLC {resolution}"
        if retcode==3:
            conf_cmd += r"\nVOLT:DC:RES {resolution}"
        measure_query = r"READ?"
        return self.measure(ag_34401a_id,range,resolution,self.channels[0],conf_cmd,measure_query)

    def get_ac_voltage(self,ag_34401a_id,range="undef",resolution="undef"):
        conf_cmd = r"CONF:VOLT:AC\n"
        #range
        retcode,res=self.check_range(range,self.Vranges)
        if retcode==0:
            return 0,res
        range=res
        conf_cmd += r"VOLT:AC:RANG{range}"
        #resolution
        retcode,res=self.check_resolution(resolution,"plc")
        if retcode==0:
            return 0,res
        resolution=res
        if retcode==2:
            conf_cmd += r"\nVOLT:AC:NPLC {resolution}"
        if retcode==3:
            conf_cmd += r"\nVOLT:AC:RES {resolution}"
        measure_query = r"READ?"
        return self.measure(ag_34401a_id,range,resolution,self.channels[0],conf_cmd,measure_query)

    def get_dc_current(self,ag_34401a_id,range="undef",resolution="undef"):
        conf_cmd = r"CONF:CURR:DC\n"
        #range
        retcode,res=self.check_range(range,self.Iranges)
        if retcode==0:
            return 0,res
        range=res
        conf_cmd += r"CURR:DC:RANG{range}"
        #resolution
        retcode,res=self.check_resolution(resolution,"plc")
        if retcode==0:
            return 0,res
        resolution=res
        if retcode==2:
            conf_cmd += r"\nCURR:DC:NPLC {resolution}"
        if retcode==3:
            conf_cmd += r"\nCURR:DC:RES {resolution}"
        measure_query = r"READ?"
        return self.measure(ag_34401a_id,range,resolution,self.channels[0],conf_cmd,measure_query)

    def get_ac_current(self,ag_34401a_id,range="undef",resolution="undef"):
        conf_cmd = r"CONF:CURR:AC\n"
        #range
        retcode,res=self.check_range(range,self.Iranges)
        if retcode==0:
            return 0,res
        range=res
        conf_cmd += r"CURR:AC:RANG{range}"
        #resolution
        retcode,res=self.check_resolution(resolution,"plc")
        if retcode==0:
            return 0,res
        resolution=res
        if retcode==2:
            conf_cmd += r"\nCURR:AC:NPLC {resolution}"
        if retcode==3:
            conf_cmd += r"\nCURR:AC:RES {resolution}"
        measure_query = r"READ?"
        return self.measure(ag_34401a_id,range,resolution,self.channels[0],conf_cmd,measure_query)

    def get_2w_resistance(self,ag_34401a_id,range="undef",resolution="undef"):
        conf_cmd = r"CONF:RES\n"
        #range
        retcode,res=self.check_range(range,self.Rranges)
        if retcode==0:
            return 0,res
        range=res
        conf_cmd += r"RES:RANG{range}"
        #resolution
        retcode,res=self.check_resolution(resolution,"plc")
        if retcode==0:
            return 0,res
        resolution=res
        if retcode==2:
            conf_cmd += r"\nRES:NPLC {resolution}"
        if retcode==3:
            conf_cmd += r"\nRES:RES {resolution}"
        measure_query = r"READ?"
        return self.measure(ag_34401a_id,range,resolution,self.channels[0],conf_cmd,measure_query)

    def get_4w_resistance(self,ag_34401a_id,range="undef",resolution="undef"):
        conf_cmd = r"CONF:FRES\n"
        #range
        retcode,res=self.check_range(range,self.Rranges)
        if retcode==0:
            return 0,res
        range=res
        conf_cmd += r"FRES:RANG{range}"
        #resolution
        retcode,res=self.check_resolution(resolution,"plc")
        if retcode==0:
            return 0,res
        resolution=res
        if retcode==2:
            conf_cmd += r"\nFRES:NPLC {resolution}"
        if retcode==3:
            conf_cmd += r"\nFRES:RES {resolution}"
        measure_query = r"READ?"
        return self.measure(ag_34401a_id,range,resolution,self.channels[0],conf_cmd,measure_query)

    def get_frequency(self,ag_34401a_id,resolution="undef"):
        conf_cmd = r"CONF:FREQ"
        #resolution
        retcode,res=self.check_resolution(resolution,"s")
        if retcode==0:
            return 0,res
        resolution=res
        if retcode==2:
            conf_cmd += r"\nFREQ:APER {resolution}"
        if retcode==3:
            conf_cmd += r"\nFREQ:RES {resolution}"
        measure_query = r"READ?"
        return self.measure(ag_34401a_id,"undef",resolution,self.channels[0],conf_cmd,measure_query)

    def get_period(self,ag_34401a_id,resolution="undef"):
        conf_cmd = r"CONF:PER"
        #resolution
        retcode,res=self.check_resolution(resolution,"s")
        if retcode==0:
            return 0,res
        resolution=res
        if retcode==2:
            conf_cmd += r"\nPER:APER {resolution}"
        if retcode==3:
            conf_cmd += r"\nPER:RES {resolution}"
        measure_query = r"READ?"
        return self.measure(ag_34401a_id,"undef",resolution,self.channels[0],conf_cmd,measure_query)

# CREATE POOL ####################################################

me = ag_34401a_class()

# COMMANDS #######################################################

# Put serialized API in memory if not called via import
if __name__=='__main__':
    global api; api = getapi.load_api(__file__)
    scpi.submod = submod

# Functions
def getapi_ag_34401a():
    submod.setres(1,api)

def init_ag_34401a(conf_string):
    """Initialize ag_34401a power supply.

    *conf_string* must include the parameter:
    
    - bus: conf_string of the underlying link module (GPIB, TCP, ...)

    Returns ag_34401a_id"""
    retcode,res = me.init(conf_string)
    if retcode==0:
        submod.setres(retcode,"ag_34401a: %s" % (res))
        return
    submod.setres(retcode,res)

def deinit_ag_34401a(ag_34401a_id):
    "Deinitialize an ag_34401a"
    retcode,res = me.deinit(ag_34401a_id)
    if retcode==0:
        submod.setres(retcode,"ag_34401a: %s" % (res))
        return
    submod.setres(retcode,res)

def config_ag_34401a(ag_34401a_id,error_check="normal"):
    "Configure an ag_34401a"
    retcode,res = me.config(ag_34401a_id,error_check)
    if retcode==0:
        submod.setres(retcode,"ag_34401a: %s" % (res))
        return
    submod.setres(retcode,res)

def inval_ag_34401a(ag_34401a_id):
    "Invalidate an ag_34401a"
    retcode,res = me.inval(ag_34401a_id)
    if retcode==0:
        submod.setres(retcode,"ag_34401a: %s" % (res))
        return
    submod.setres(retcode,res)

def reset_ag_34401a(ag_34401a_id):
    "Send RST signal to PS"
    retcode,res = me.reset(ag_34401a_id)
    if retcode==0:
        submod.setres(retcode,"ag_34401a: %s" % (res))
        return
    submod.setres(retcode,res)

def get_dc_voltage_ag_34401a(ag_34401a_id,range="undef",resolution="undef"):
    """Get DC voltage in Volts.
    The optional *range* can be: auto, 0.1, 1, 10, 100 or 1000 Volts. When *range* is undef or absent, it fallbacks to autorange.
    The optional *resolution* can be expressed either as a tolerance in Volts (e.g. 0.01), or by the number of power-line cycles that will be used to integrate, followed by PLC (e.g. 10PLC). The following values are accepted: 0.02, 0.2, 1, 10, 100. When *resolution* is undef or absent, the default value of the instrument (10PLC) is used.
    MIN or MAX can be used for both parameters (for resolution, MAX means the highest resolution)."""
    retcode,res = me.get_dc_voltage(ag_34401a_id,range,resolution)
    if retcode==0:
        submod.setres(retcode,"ag_34401a: %s" % (res))
        return
    submod.setres(retcode,res)

def get_ac_voltage_ag_34401a(ag_34401a_id,range="undef",resolution="undef"):
    """Get AC voltage in Volts.
    The optional *range* can be: auto, 0.1, 1, 10, 100 or 1000 Volts. When *range* is undef or absent, it fallbacks to autorange.
    The optional *resolution* can be expressed either as a tolerance in Volts (e.g. 0.01), or by the number of power-line cycles that will be used to integrate, followed by PLC (e.g. 10PLC). The following values are accepted: 0.02, 0.2, 1, 10, 100. When *resolution* is undef or absent, the default value of the instrument (10PLC) is used.
    MIN or MAX can be used for both parameters (for resolution, MAX means the highest resolution)."""
    retcode,res = me.get_ac_voltage(ag_34401a_id,range,resolution)
    if retcode==0:
        submod.setres(retcode,"ag_34401a: %s" % (res))
        return
    submod.setres(retcode,res)

def get_dc_current_ag_34401a(ag_34401a_id,range="undef",resolution="undef"):
    """Get DC current in Ampers.
    The optional *range* can be: auto, 0.01, 0.1, 1, 3 Ampers. When *range* is undef or absent, it fallbacks to autorange.
    The optional *resolution* can be expressed either as a tolerance in Ampers (e.g. 0.01), or by the number of power-line cycles that will be used to integrate, followed by PLC (e.g. 10PLC). The following values are accepted: 0.02, 0.2, 1, 10, 100. When *resolution* is undef or absent, the default value of the instrument (10PLC) is used.
    MIN or MAX can be used for both parameters (for resolution, MAX means the highest resolution)."""
    retcode,res = me.get_dc_current(ag_34401a_id,range,resolution)
    if retcode==0:
        submod.setres(retcode,"ag_34401a: %s" % (res))
        return
    submod.setres(retcode,res)

def get_ac_current_ag_34401a(ag_34401a_id,range="undef",resolution="undef"):
    """Get AC current in Ampers.
    The optional *range* can be: auto, 0.01, 0.1, 1, 3 Ampers. When *range* is undef or absent, it fallbacks to autorange.
    The optional *resolution* can be expressed either as a tolerance in Ampers (e.g. 0.01), or by the number of power-line cycles that will be used to integrate, followed by PLC (e.g. 10PLC). The following values are accepted: 0.02, 0.2, 1, 10, 100. When *resolution* is undef or absent, the default value of the instrument (10PLC) is used.
    MIN or MAX can be used for both parameters (for resolution, MAX means the highest resolution)."""
    retcode,res = me.get_ac_current(ag_34401a_id,range,resolution)
    if retcode==0:
        submod.setres(retcode,"ag_34401a: %s" % (res))
        return
    submod.setres(retcode,res)

def get_2w_resistance_ag_34401a(ag_34401a_id,range="undef",resolution="undef"):
    """Get 2-wire resistance in Ohms.
    The optional *range* can be: auto, 100, 1e3, 10e3, 100e3, 1e6, 10e6 or 100e6 Ohms. When *range* is undef or absent, it fallbacks to autorange.
    The optional *resolution* can be expressed either as a tolerance in Ohms (e.g. 0.01), or by the number of power-line cycles that will be used to integrate, followed by PLC (e.g. 10PLC). The following values are accepted: 0.02, 0.2, 1, 10, 100. When *resolution* is undef or absent, the default value of the instrument (10PLC) is used.
    MIN or MAX can be used for both parameters (for resolution, MAX means the highest resolution)."""
    retcode,res = me.get_2w_resistance(ag_34401a_id,range,resolution)
    if retcode==0:
        submod.setres(retcode,"ag_34401a: %s" % (res))
        return
    submod.setres(retcode,res)

def get_4w_resistance_ag_34401a(ag_34401a_id,range="undef",resolution="undef"):
    """Get 4-wire resistance in Ohms.
    The optional *range* can be: auto, 100, 1e3, 10e3, 100e3, 1e6, 10e6 or 100e6 Ohms. When *range* is undef or absent, it fallbacks to autorange.
    The optional *resolution* can be expressed either as a tolerance in Ohms (e.g. 0.01), or by the number of power-line cycles that will be used to integrate, followed by PLC (e.g. 10PLC). The following values are accepted: 0.02, 0.2, 1, 10, 100. When *resolution* is undef or absent, the default value of the instrument (10PLC) is used.
    MIN or MAX can be used for both parameters (for resolution, MAX means the highest resolution)."""
    retcode,res = me.get_4w_resistance(ag_34401a_id,range,resolution)
    if retcode==0:
        submod.setres(retcode,"ag_34401a: %s" % (res))
        return
    submod.setres(retcode,res)

def get_frequency_ag_34401a(ag_34401a_id,resolution="undef"):
    """Get frequency in Hertzs.
    The optional *resolution* can be expressed either as a tolerance in Hertzs (e.g. 0.01), or by the time aperture that will be used to integrate, followed by s (e.g. 0.1s for 100 milliseconds). The following values are accepted: 0.01, 0.1, 1. When *resolution* is undef or absent, the default value of the instrument (10PLC) is used.
    MIN or MAX can be used for both parameters (for resolution, MAX means the highest resolution)."""
    retcode,res = me.get_frequency(ag_34401a_id,resolution)
    if retcode==0:
        submod.setres(retcode,"ag_34401a: %s" % (res))
        return
    submod.setres(retcode,res)

def get_period_ag_34401a(ag_34401a_id,resolution="undef"):
    """Get frequency in seconds.
    The optional *resolution* can be expressed either as a tolerance in seconds (e.g. 0.01), or by the time aperture that will be used to integrate, followed by s (e.g. 0.1s for 100 milliseconds). The following values are accepted: 0.01, 0.1, 1. When *resolution* is undef or absent, the default value of the instrument (10PLC) is used.
    MIN or MAX can be used for both parameters (for resolution, MAX means the highest resolution)."""
    retcode,res = me.get_period(ag_34401a_id,resolution)
    if retcode==0:
        submod.setres(retcode,"ag_34401a: %s" % (res))
        return
    submod.setres(retcode,res)

def free_command_ag_34401a(ag_34401a_id,command):
    "Send a raw command to the PS"
    retcode,res = me.free_command(ag_34401a_id,command)
    if retcode==0:
        submod.setres(retcode,"ag_34401a: %s" % (res))
        return
    submod.setres(retcode,res)

def get_error_queue_ag_34401a(ag_34401a_id):
    "Read error queue until the end (code 0)"
    retcode,res = me.get_error_queue(ag_34401a_id)
    if retcode==0:
        submod.setres(retcode,"ag_34401a: %s" % (res))
        return
    submod.setres(retcode,res)
    
