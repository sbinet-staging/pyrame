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

import pools, getapi, conf_strings

ag_33500_pool = pools.pool()

from time import sleep

# Put serialized API in memory if not called via import
if __name__ == '__main__':
    global api; api = getapi.load_api(__file__)

# Functions
def getapi_ag_33500():
    submod.setres(1,api)

def init_ag_33500(conf_string):
    """Initialize ag_33500 pattern generator.
    
    *conf_string*: must include a bus parameter with the conf_string of the underlying link module (gpib, tcp, serial, ...)

    Returns ag_33500_id"""

    try:
        conf = conf_strings.parse(conf_string)
    except Exception as e:
        submod.setres(0,str(e))
        return
    if conf.name!="ag_33500":
        submod.setres(0,"ag_33500: Invalid module name %s in conf_string instead of ag_33500"%(conf.name))
        return
    if not conf.has("bus"):
        submod.setres(0,"ag_33500: Error: a required parameter in conf_string is not present")
        return
    try:
        conf_bus = conf_strings.parse(conf.params["bus"])
    except Exception as e:
        submod.setres(0,"ag_33500: %s" % (str(e)))
        return
    retcode,res = submod.execcmd("init_"+conf_bus.name,conf.params["bus"])
    if retcode==0:
        submod.setres(0,"ag_33500: Error initializing link <- %s" % (res))
        return
    ag_33500_id = ag_33500_pool.new({
        "bus": conf_bus.name,
        "bus_id": res,
        "cache_func": ["",""],
        "cache_freq": ["",""],
        "cache_hl": ["",""],
        "cache_ll": ["",""],
        "cache_dc": ["",""],
        "cache_sym": ["",""],
        "cache_pw": ["",""],
        "cache_re": ["",""],
        "cache_fe": ["",""],
        "cache_phase": ["",""],
        "cache_sync": -1,
        "cache_sync_ch": ""})
    submod.setres(1,ag_33500_id)

def deinit_ag_33500(ag_33500_id):
    "Deregister an ag_33500 from the pool"
    try:
        ag_33500 = ag_33500_pool.get(ag_33500_id)
    except Exception as e:
        submod.setres(1,"ag_33500: ag_33500_%s" % (str(e)))
        return
    # Deinitialize link
    retcode,res = submod.execcmd("deinit_"+ag_33500["bus"],ag_33500["bus_id"])
    if retcode==0:
        submod.setres(0,"ag_33500: Error deinitializing link <- %s" % (res))
        return
    # Remove ag_33500 from the pool
    try:
        ag_33500_pool.remove(ag_33500_id)
    except Exception as e:
        submod.setres(0,"ag_33500: %s" % (str(e)))
        return
    submod.setres(1,"ok")

def config_ag_33500(ag_33500_id):
    try:
        ag_33500 = ag_33500_pool.get(ag_33500_id)
    except Exception as e:
        submod.setres(0,"ag_33500: ag_33500_%s" % (str(e)))
        return
    # Configure link
    retcode,res = submod.execcmd("config_"+ag_33500["bus"],ag_33500["bus_id"])
    if retcode==0:
        submod.setres(0,"ag_33500: Error configuring link <- %s" % (res))
        return
    # Cleanup error queue
    retcode,errors = get_error_queue(ag_33500)
    if retcode==0:
        _,_ = submod.execcmd("inval_"+ag_33500["bus"],ag_33500["bus_id"])
        submod.setres(0,"ag_33500: Error cleaning up the error queue : %s" % (errors))
        return
    ag_33500["configured"] = True
    submod.setres(1,"ok")

def inval_ag_33500(ag_33500_id):
    try:
        ag_33500 = ag_33500_pool.get(ag_33500_id)
    except Exception as e:
        submod.setres(0,"ag_33500: ag_33500_%s" % (str(e)))
        return
    if not "configured" in ag_33500:
        submod.setres(1,"ag_33500: not configured")
        return
    # Invalidate link
    retcode,res = submod.execcmd("inval_"+ag_33500["bus"],ag_33500["bus_id"])
    if retcode==0:
        submod.setres(0,"ag_33500: Error configuring link <- %s" % (res))
        return
    del ag_33500["configured"]
    submod.setres(1,"ok")

def reset_ag_33500(ag_33500_id):
    "Send RST signal to PG"
    try:
        ag_33500 = ag_33500_pool.get(ag_33500_id)
    except Exception as e:
        submod.setres(0,"ag_33500: ag_33500_%s" % (str(e)))
        return
    if "configured" not in ag_33500:
        submod.setres(0,"ag_33500: not configured")
        return
    command = "*RST"
    retcode,res = submod.execcmd("write_"+ag_33500["bus"],ag_33500["bus_id"],command+r"\n")
    if retcode==0:
        submod.setres(0,"ag_33500: Error writing to link <- %s" % (res))
    retcode,errors = get_error_queue(ag_33500)
    if errors!="":
        submod.setres(0,"ag_33500: Error(s) returned from the PG : %s" % (errors))
    submod.setres(1,"ok")

def configure_sine_ag_33500(ag_33500_id, frequency, high_level, low_level, channel):
    "Configure ag_33500 to a sine wave with the specified parameters"
    retcode,res = set_function(ag_33500_id, "sine", channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_33500: %s" % (res))
        return
    retcode,res = set_frequency(ag_33500_id, frequency, channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_33500: %s" % (res))
        return
    retcode,res = set_high_level(ag_33500_id, high_level, channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_33500: %s" % (res))
        return
    retcode,res = set_low_level(ag_33500_id, low_level, channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_33500: %s" % (res))
        return
    submod.setres(1,"ok")

def configure_square_ag_33500(ag_33500_id, frequency, high_level, low_level, duty_cycle, channel):
    "Configure ag_33500 to a square wave with the specified parameters"
    retcode,res = set_function(ag_33500_id, "square", channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_33500: %s" % (res))
        return
    retcode,res = set_frequency(ag_33500_id, frequency, channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_33500: %s" % (res))
        return
    retcode,res = set_high_level(ag_33500_id, high_level, channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_33500: %s" % (res))
        return
    retcode,res = set_low_level(ag_33500_id, low_level, channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_33500: %s" % (res))
        return
    retcode,res = set_duty_cycle(ag_33500_id, duty_cycle, channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_33500: %s" % (res))
        return
    submod.setres(1,"ok")

def configure_ramp_ag_33500(ag_33500_id, frequency, high_level, low_level, symmetry, channel):
    "Configure ag_33500 to a ramp wave with the specified parameters"
    retcode,res = set_function(ag_33500_id, "ramp", channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_33500: %s" % (res))
        return
    retcode,res = set_frequency(ag_33500_id, frequency, channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_33500: %s" % (res))
        return
    retcode,res = set_high_level(ag_33500_id, high_level, channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_33500: %s" % (res))
        return
    retcode,res = set_low_level(ag_33500_id, low_level, channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_33500: %s" % (res))
        return
    retcode,res = set_symmetry(ag_33500_id, symmetry, channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_33500: %s" % (res))
        return
    submod.setres(1,"ok")

def configure_pulse_ag_33500(ag_33500_id, frequency, high_level, low_level, pulse_width, rising_edge, falling_edge, channel):
    "Configure ag_33500 to a pulse train with the specified parameters"
    retcode,res = set_function(ag_33500_id, "pulse", channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_33500: %s" % (res))
        return
    retcode,res = set_frequency(ag_33500_id, frequency, channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_33500: %s" % (res))
        return
    retcode,res = set_high_level(ag_33500_id, high_level, channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_33500: %s" % (res))
        return
    retcode,res = set_low_level(ag_33500_id, low_level, channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_33500: %s" % (res))
        return
    retcode,res = set_pulse_width(ag_33500_id, pulse_width, channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_33500: %s" % (res))
        return
    retcode,res = set_edges(ag_33500_id, rising_edge, falling_edge, channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_33500: %s" % (res))
        return
    submod.setres(1,"ok")

def power_on(ag_33500_id, channel):
    try:
        ag_33500 = ag_33500_pool.get(ag_33500_id)
    except Exception as e:
        return 0,"ag_33500_%s" % (str(e))
    if "configured" not in ag_33500:
        return 0,"not configured"
    # Verify channel
    if channel=="undef" or channel=="":
        return 0,"Channel must be specified"
    if int(channel) not in range(1,2+1):
        return 0,"Invalid channel"
    # Send the command
    command = "OUTP{0} ON".format(channel)
    retcode,res = submod.execcmd("write_"+ag_33500["bus"],ag_33500["bus_id"],command+r"\n")
    if retcode==0:
        return 0,"Error writing to link <- %s" % (res)
    retcode,errors = get_error_queue(ag_33500)
    if errors!="":
        return 0,"Error(s) returned from the PG : %s" % (errors)
    return 1,"ok"

def power_on_ag_33500(ag_33500_id,channel):
    "Turn on"
    retcode,res = power_on(ag_33500_id,channel)
    if retcode==0:
        submod.setres(0,"ag_33500: %s" % (res))
    submod.setres(retcode,res)

def power_off(ag_33500_id,channel):
    try:
        ag_33500 = ag_33500_pool.get(ag_33500_id)
    except Exception as e:
        return 0,"ag_33500_%s" % (str(e))
    if "configured" not in ag_33500:
        return 0,"not configured"
    # Verify channel
    if channel=="undef" or channel=="":
        return 0,"Channel must be specified"
    if int(channel) not in range(1,2+1):
        return 0,"Invalid channel"
    # Send the command
    command = "OUTP{0} OFF".format(channel)
    retcode,res = submod.execcmd("write_"+ag_33500["bus"],ag_33500["bus_id"],command+r"\n")
    if retcode==0:
        return 0,"Error writing to link <- %s" % (res)
    retcode,errors = get_error_queue(ag_33500)
    if errors!="":
        return 0,"Error(s) returned from the PG : %s" % (errors)
    return 1,"ok"

def power_off_ag_33500(ag_33500_id,channel):
    "Turn off"
    retcode,res = power_off(ag_33500_id,channel)
    if retcode==0:
        submod.setres(0,"ag_33500: %s" % (res))
    submod.setres(retcode,res)

def set_function(ag_33500_id,function,channel):
    try:
        ag_33500 = ag_33500_pool.get(ag_33500_id)
    except Exception as e:
        return 0,"ag_33500_%s" % (str(e))
    if "configured" not in ag_33500:
        return 0,"not configured"
    # Verify channel
    if channel=="undef" or channel=="":
        return 0,"Channel must be specified"
    if int(channel) not in range(1,2+1):
        return 0,"Invalid channel"
    # Verify consistency of parameters
    if function not in ["sine", "square", "ramp", "pulse"]:
        return 0,"invalid function"
    if ag_33500["cache_func"][int(channel)-1]!=function:
        # Send the command
        value = { "sine":"SIN", "square":"SQU", "ramp":"RAMP", "pulse":"PULS" }.get(function)
        command = "SOUR{0}:FUNC {1}".format(channel,value)
        retcode,res = submod.execcmd("write_"+ag_33500["bus"],ag_33500["bus_id"],command+r"\n")
        if retcode==0:
            return 0,"Error writing to link <- %s" % (res)
        retcode,errors = get_error_queue(ag_33500)
        if errors!="":
            return 0,"Error(s) returned from the PG : %s" % (errors)
        ag_33500["cache_func"][int(channel)-1] = function
    return 1,"ok"

def set_function_ag_33500(ag_33500_id,function,channel):
    "Set function, where function is 'sine', 'square', 'ramp', 'pulse'"
    retcode,res = set_function(ag_33500_id,function,channel)
    if retcode==0:
        submod.setres(0,"ag_33500: %s" % (res))
    submod.setres(retcode,res)

def set_high_level(ag_33500_id,high_level,channel):
    try:
        ag_33500 = ag_33500_pool.get(ag_33500_id)
    except Exception as e:
        return 0,"ag_33500_%s" % (str(e))
    if "configured" not in ag_33500:
        return 0,"not configured"
    # Verify channel
    if channel=="undef" or channel=="":
        return 0,"Channel must be specified"
    if int(channel) not in range(1,2+1):
        return 0,"Invalid channel"
    if ag_33500["cache_hl"][int(channel)-1]!=high_level and high_level!="undef" and high_level!="":
        # Send the command
        value = float(high_level)
        command = "SOUR{0}:VOLT:HIGH {1:.4f}".format(channel,value)
        retcode,res = submod.execcmd("write_"+ag_33500["bus"],ag_33500["bus_id"],command+r"\n")
        if retcode==0:
            return 0,"Error writing to link <- %s" % (res)
        retcode,errors = get_error_queue(ag_33500)
        if errors!="":
            return 0,"Error(s) returned from the PG : %s" % (errors)
        ag_33500["cache_hl"][int(channel)-1] = high_level
    return 1,"ok"

def set_high_level_ag_33500(ag_33500_id,high_level,channel):
    "Set high level value in Volts."
    retcode,res = set_high_level(ag_33500_id,high_level,channel)
    if retcode==0:
        submod.setres(0,"ag_33500: %s" % (res))
    submod.setres(retcode,res)

def set_low_level(ag_33500_id,low_level,channel):
    try:
        ag_33500 = ag_33500_pool.get(ag_33500_id)
    except Exception as e:
        return 0,"ag_33500_%s" % (str(e))
    if "configured" not in ag_33500:
        return 0,"not configured"
    # Verify channel
    if channel=="undef" or channel=="":
        return 0,"Channel must be specified"
    if int(channel) not in range(1,2+1):
        return 0,"Invalid channel"
    if ag_33500["cache_ll"][int(channel)-1]!=low_level and low_level!="undef" and low_level!="":
        # Send the command
        value = float(low_level)
        command = "SOUR{0}:VOLT:LOW {1:.4f}".format(channel,value)
        retcode,res = submod.execcmd("write_"+ag_33500["bus"],ag_33500["bus_id"],command+r"\n")
        if retcode==0:
            return 0,"Error writing to link <- %s" % (res)
        retcode,errors = get_error_queue(ag_33500)
        if errors!="":
            return 0,"Error(s) returned from the PG : %s" % (errors)
        ag_33500["cache_ll"][int(channel)-1] = low_level
    return 1,"ok"

def set_low_level_ag_33500(ag_33500_id,low_level,channel):
    "Set low level value in Volts."
    retcode,res = set_low_level(ag_33500_id,low_level,channel)
    if retcode==0:
        submod.setres(0,"ag_33500: %s" % (res))
    submod.setres(retcode,res)

def set_frequency(ag_33500_id,frequency,channel):
    try:
        ag_33500 = ag_33500_pool.get(ag_33500_id)
    except Exception as e:
        return 0,"ag_33500_%s" % (str(e))
    if "configured" not in ag_33500:
        return 0,"not configured"
    # Verify channel
    if channel=="undef" or channel=="":
        return 0,"Channel must be specified"
    if int(channel) not in range(1,2+1):
        return 0,"Invalid channel"
    if ag_33500["cache_freq"][int(channel)-1]!=frequency and frequency!="undef" and frequency!="":
        # Send the command
        value = float(frequency)
        command = "SOUR{0}:FREQ {1:.6f}".format(channel,value)
        retcode,res = submod.execcmd("write_"+ag_33500["bus"],ag_33500["bus_id"],command+r"\n")
        if retcode==0:
            return 0,"Error writing to link <- %s" % (res)
        retcode,errors = get_error_queue(ag_33500)
        if errors!="":
            return 0,"Error(s) returned from the PG : %s" % (errors)
        ag_33500["cache_freq"][int(channel)-1] = frequency
    return 1,"ok"

def set_frequency_ag_33500(ag_33500_id,frequency,channel):
    "Set frequency in Hertz."
    retcode,res = set_frequency(ag_33500_id,frequency,channel)
    if retcode==0:
        submod.setres(0,"ag_33500: %s" % (res))
    submod.setres(retcode,res)

def get_frequency_ag_33500(ag_33500_id,channel):
    "Get frequency in Hertz."
    try:
        ag_33500 = ag_33500_pool.get(ag_33500_id)
    except Exception as e:
        submod.setres(0,"ag_33500: ag_33500_%s" % (str(e)))
        return
    if "configured" not in ag_33500:
        submod.setres(0,"ag_33500: not configured")
        return
    # Verify channel
    if channel=="undef" or channel=="":
        submod.setres(0,"ag_33200: Channel must be specified")
        return
    if int(channel) not in range(1,2+1):
        submod.setres(0,"ag_33200: Invalid channel")
        return
    # Send the command
    command = "SOUR{0}:FREQ?".format(channel)
    retcode,res = submod.execcmd("wrnrd_until_"+ag_33500["bus"],ag_33500["bus_id"],command+r"\n",r"\n")
    if retcode==0:
        submod.setres(0,"ag_33500: Error writing and reading to link <- %s" % (res))
        return
    retcode,errors = get_error_queue(ag_33500)
    if errors!="":
        submod.setres(0,"ag_33500: Error(s) returned from the PG : %s" % (errors))
        return
    submod.setres(1,res)

def set_duty_cycle(ag_33500_id,duty_cycle,channel):
    try:
        ag_33500 = ag_33500_pool.get(ag_33500_id)
    except Exception as e:
        return 0,"ag_33500_%s" % (str(e))
    if "configured" not in ag_33500:
        return 0,"not configured"
    # Verify channel
    if channel=="undef" or channel=="":
        return 0,"Channel must be specified"
    if int(channel) not in range(1,2+1):
        return 0,"Invalid channel"
    if ag_33500["cache_dc"][int(channel)-1]!=duty_cycle and duty_cycle!="undef" and duty_cycle!="":
        # Send the command
        value = float(duty_cycle)
        command = "SOUR{0}:FUNC:SQU:DCYC {1:.4f}".format(channel,value)
        retcode,res = submod.execcmd("write_"+ag_33500["bus"],ag_33500["bus_id"],command+r"\n")
        if retcode==0:
            return 0,"Error writing to link <- %s" % (res)
        retcode,errors = get_error_queue(ag_33500)
        if errors!="":
            return 0,"Error(s) returned from the PG : %s" % (errors)
        ag_33500["cache_dc"][int(channel)-1] = duty_cycle
    return 1,"ok"

def set_duty_cycle_ag_33500(ag_33500_id,duty_cycle,channel):
    "Set duty cycle of square function. Duty cycle ranges from 0 to 100."
    retcode,res = set_duty_cycle(ag_33500_id,duty_cycle,channel)
    if retcode==0:
        submod.setres(0,"ag_33500: %s" % (res))
    submod.setres(retcode,res)

def set_pulse_width(ag_33500_id,pulse_width,channel):
    try:
        ag_33500 = ag_33500_pool.get(ag_33500_id)
    except Exception as e:
        return 0,"ag_33500_%s" % (str(e))
    if "configured" not in ag_33500:
        return 0,"not configured"
    # Verify channel
    if channel=="undef" or channel=="":
        return 0,"Channel must be specified"
    if int(channel) not in range(1,2+1):
        return 0,"Invalid channel"
    if ag_33500["cache_pw"][int(channel)-1]!=pulse_width and pulse_width!="undef" and pulse_width!="":
        # Send the command
        value = float(pulse_width)
        command = "SOUR{0}:FUNC:PULS:WIDT {1:.9f}".format(channel,value)
        retcode,res = submod.execcmd("write_"+ag_33500["bus"],ag_33500["bus_id"],command+r"\n")
        if retcode==0:
            return 0,"Error writing to link <- %s" % (res)
        retcode,errors = get_error_queue(ag_33500)
        if errors!="":
            return 0,"Error(s) returned from the PG : %s" % (errors)
        ag_33500["cache_pw"][int(channel)-1] = pulse_width
    return 1,"ok"

def set_pulse_width_ag_33500(ag_33500_id,pulse_width,channel):
    "Set pulse width of pulse function in seconds."
    retcode,res = set_pulse_width(ag_33500_id,pulse_width,channel)
    if retcode==0:
        submod.setres(0,"ag_33500: %s" % (res))
    submod.setres(retcode,res)

def set_edges(ag_33500_id,rising_edge,falling_edge,channel):
    try:
        ag_33500 = ag_33500_pool.get(ag_33500_id)
    except Exception as e:
        return 0,"ag_33500_%s" % (str(e))
    if "configured" not in ag_33500:
        return 0,"not configured"
    # Verify channel
    if channel=="undef" or channel=="":
        return 0,"Channel must be specified"
    if int(channel) not in range(1,2+1):
        return 0,"Invalid channel"
    # Rising edge
    if ag_33500["cache_re"][int(channel)-1]!=rising_edge and rising_edge!="undef" and rising_edge!="":
        # Verify edges
        if rising_edge not in ["MIN","min","MAX","max"]:
            value_r = "{0:.9f}".format(float(rising_edge))
        else:
            value_r = rising_edge
        # Send the command
        command = "SOUR{0}:FUNC:PULS:TRAN:LEAD {1}".format(channel,value_r)
        retcode,res = submod.execcmd("write_"+ag_33500["bus"],ag_33500["bus_id"],command+r"\n")
        if retcode==0:
            return 0,"Error writing to link <- %s" % (res)
        retcode,errors = get_error_queue(ag_33500)
        if errors!="":
            return 0,"Error(s) returned from the PG : %s" % (errors)
        ag_33500["cache_re"][int(channel)-1] = rising_edge
    # Falling edge
    if ag_33500["cache_fe"][int(channel)-1]!=falling_edge and falling_edge!="undef" and falling_edge!="":
        # Verify edges
        if falling_edge not in ["MIN","min","MAX","max"]:
            value_f = "{0:.9f}".format(float(falling_edge))
        else:
            value_f = falling_edge
        # Send the command
        command = "SOUR{0}:FUNC:PULS:TRAN:TRA {1}".format(channel,value_f)
        retcode,res = submod.execcmd("write_"+ag_33500["bus"],ag_33500["bus_id"],command+r"\n")
        if retcode==0:
            return 0,"Error writing to link <- %s" % (res)
        retcode,errors = get_error_queue(ag_33500)
        if errors!="":
            return 0,"Error(s) returned from the PG : %s" % (errors)
        ag_33500["cache_fe"][int(channel)-1] = falling_edge
    return 1,"ok"

def set_edges_ag_33500(ag_33500_id,rising_edge,falling_edge,channel):
    "Set raising and falling edges duration in seconds for pulse function."
    retcode,res = set_edges(ag_33500_id,rising_edge,falling_edge,channel)
    if retcode==0:
        submod.setres(0,"ag_33500: %s" % (res))
    submod.setres(retcode,res)

def set_symmetry(ag_33500_id,symmetry,channel):
    try:
        ag_33500 = ag_33500_pool.get(ag_33500_id)
    except Exception as e:
        return 0,"ag_33500_%s" % (str(e))
    if "configured" not in ag_33500:
        return 0,"not configured"
    # Verify channel
    if channel=="undef" or channel=="":
        return 0,"Channel must be specified"
    if int(channel) not in range(1,2+1):
        return 0,"Invalid channel"
    if ag_33500["cache_sym"][int(channel)-1]!=symmetry and symmetry!="undef" and symmetry!="":
        # Send the command
        value = float(symmetry)
        command = "SOUR{0}:FUNC:RAMP:SYMM {1:.4f}".format(channel,value)
        retcode,res = submod.execcmd("write_"+ag_33500["bus"],ag_33500["bus_id"],command+r"\n")
        if retcode==0:
            return 0,"Error writing to link <- %s" % (res)
        retcode,errors = get_error_queue(ag_33500)
        if errors!="":
            return 0,"Error(s) returned from the PG : %s" % (errors)
        ag_33500["cache_sym"][int(channel)-1] = symmetry
    return 1,"ok"

def set_symmetry_ag_33500(ag_33500_id,symmetry,channel):
    "Set symmetry for ramp functions. symmetry ranges from 0 to 100."
    retcode,res = set_symmetry(ag_33500_id,symmetry,channel)
    if retcode==0:
        submod.setres(0,"ag_33500: %s" % (res))
    submod.setres(retcode,res)

def set_phase(ag_33500_id,phase,channel):
    try:
        ag_33500 = ag_33500_pool.get(ag_33500_id)
    except Exception as e:
        return 0,"ag_33500_%s" % (str(e))
    if "configured" not in ag_33500:
        return 0,"not configured"
    # Verify channel
    if channel=="undef" or channel=="":
        return 0,"Channel must be specified"
    if int(channel) not in range(1,2+1):
        return 0,"Invalid channel"
    if ag_33500["cache_phase"][int(channel)-1]!=phase and phase!="undef" and phase!="":
        # Send the command
        value = float(phase)
        command = "SOUR{0}:PHAS {1:.3f}".format(channel,value)
        retcode,res = submod.execcmd("write_"+ag_33500["bus"],ag_33500["bus_id"],command+r"\n")
        if retcode==0:
            return 0,"Error writing to link <- %s" % (res)
        retcode,errors = get_error_queue(ag_33500)
        if errors!="":
            return 0,"Error(s) returned from the PG : %s" % (errors)
        ag_33500["cache_phase"][int(channel)-1] = phase
    return 1,"ok"

def set_phase_ag_33500(ag_33500_id,phase,channel):
    "Set phase of output in degrees. Phase ranges from -360 to +360 degrees."
    retcode,res = set_phase(ag_33500_id,phase,channel)
    if retcode==0:
        submod.setres(0,"ag_33500: %s" % (res))
    submod.setres(retcode,res)

def set_sync(ag_33500_id,sync,channel):
    try:
        ag_33500 = ag_33500_pool.get(ag_33500_id)
    except Exception as e:
        return 0,"ag_33500_%s" % (str(e))
    if "configured" not in ag_33500:
        return 0,"not configured"
    # Verify parameter
    if sync=="undef" or sync=="":
        return 1,"ok"
    if sync not in ["0","1"]:
        return 0,"Invalid sync parameter"
    sync = int(sync)
    # Verify channel
    if channel=="undef" or channel=="":
        return 0,"Channel must be specified"
    if int(channel) not in range(1,2+1):
        return 0,"Invalid channel"
    if ag_33500["cache_sync"]!=sync or ag_33500["cache_sync_ch"]!=channel:
        # Send the command
        command = r"OUTP:SYNC:SOURCE CH{0}\n".format(channel)
        command += "OUTP:SYNC "
        command += "ON" if sync else "OFF"
        retcode,res = submod.execcmd("write_"+ag_33500["bus"],ag_33500["bus_id"],command+r"\n")
        if retcode==0:
            return 0,"Error turning on ag_33500 %d sync <- %s" % (ag_33500.id,res)
        retcode,errors = get_error_queue(ag_33500)
        if errors!="":
            return 0,"Error(s) returned from the PG : %s" % (errors)
        ag_33500["cache_sync"] = sync
        ag_33500["cache_sync_ch"] = channel
    return 1,"ok"

def set_sync_ag_33500(ag_33500_id,sync,channel):
    "Select sync source with channel and turn sync on (1) or off (0)."
    retcode,res = set_sync(ag_33500_id,sync,channel)
    if retcode==0:
        submod.setres(0,"ag_33500: %s" % (res))
    submod.setres(retcode,res)

def get_error_queue_ag_33500(ag_33500_id):
    "Read error queue until the end (code 0)"
    try:
        ag_33500 = ag_33500_pool.get(ag_33500_id)
    except Exception as e:
        return 0,"ag_33500_%s" % (str(e))
    if "configured" not in ag_33500:
        return 0,"not configured"
    retcode,res = get_error_queue(ag_33500)
    if retcode==0:
        submod.setres(0,"ag_33500: %s" % (res))
    submod.setres(retcode,res)
    
def get_error_queue(link):
    command = "SYST:ERR?"
    errors = ""
    while True: 
        sleep(0.005)
        retcode,res = submod.execcmd("wrnrd_until_"+link["bus"],link["bus_id"],command+r"\n",r"\n")
        if retcode==0:
            return 0,res
        try:
            if int(res.split(",",1)[0])!=0: 
                errors += res if errors=="" else "; "+res
            else:
                break
        except Exception as e:
            return 0,"Read wrong response while getting error queue: %s" % (res)
    return 1,errors

