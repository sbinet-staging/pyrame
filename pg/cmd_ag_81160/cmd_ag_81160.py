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

ag_81160_pool = pools.pool()

from time import sleep

# Put serialized API in memory if not called via import
if __name__ == '__main__':
    global api; api = getapi.load_api(__file__)

# Functions
def getapi_ag_81160():
    submod.setres(1,api)

def init_ag_81160(conf_string):
    """Initialize ag_81160 pattern generator.
    
    *conf_string*: must include a bus parameter with the conf_string of the underlying link module (gpib, tcp, serial, ...)

    Returns ag_81160_id"""

    try:
        conf = conf_strings.parse(conf_string)
    except Exception as e:
        submod.setres(0,str(e))
        return
    if conf.name!="ag_81160":
        submod.setres(0,"ag_81160: Invalid module name %s in conf_string instead of ag_81160"%(conf.name))
        return
    if not conf.has("bus"):
        submod.setres(0,"ag_81160: Error: a required parameter in conf_string is not present")
        return
    try:
        conf_bus = conf_strings.parse(conf.params["bus"])
    except Exception as e:
        submod.setres(0,"ag_81160: %s" % (str(e)))
        return
    retcode,res = submod.execcmd("init_"+conf_bus.name,conf.params["bus"])
    if retcode==0:
        submod.setres(0,"ag_81160: Error initializing link <- %s" % (res))
        return
    ag_81160_id = ag_81160_pool.new({
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
        "cache_sync": [-1,-1]})
    submod.setres(1,ag_81160_id)

def deinit_ag_81160(ag_81160_id):
    "Deregister an ag_81160 from the pool"
    try:
        ag_81160 = ag_81160_pool.get(ag_81160_id)
    except Exception as e:
        submod.setres(1,"ag_81160: ag_81160_%s" % (str(e)))
        return
    # Deinitialize link
    retcode,res = submod.execcmd("deinit_"+ag_81160["bus"],ag_81160["bus_id"])
    if retcode==0:
        submod.setres(0,"ag_81160: Error deinitializing link <- %s" % (res))
        return
    # Remove ag_81160 from the pool
    try:
        ag_81160_pool.remove(ag_81160_id)
    except Exception as e:
        submod.setres(0,"ag_81160: %s" % (str(e)))
        return
    submod.setres(1,"ok")

def config_ag_81160(ag_81160_id):
    try:
        ag_81160 = ag_81160_pool.get(ag_81160_id)
    except Exception as e:
        submod.setres(0,"ag_81160: ag_81160_%s" % (str(e)))
        return
    # Configure link
    retcode,res = submod.execcmd("config_"+ag_81160["bus"],ag_81160["bus_id"])
    if retcode==0:
        submod.setres(0,"ag_81160: Error configuring link <- %s" % (res))
        return
    # Cleanup error queue
    retcode,errors = get_error_queue(ag_81160)
    if retcode==0:
        _,_ = submod.execcmd("inval_"+ag_81160["bus"],ag_81160["bus_id"])
        submod.setres(0,"ag_81160: Error cleaning up the error queue : %s" % (errors))
        return
    ag_81160["configured"] = True
    submod.setres(1,"ok")

def inval_ag_81160(ag_81160_id):
    try:
        ag_81160 = ag_81160_pool.get(ag_81160_id)
    except Exception as e:
        submod.setres(0,"ag_81160: ag_81160_%s" % (str(e)))
        return
    if not "configured" in ag_81160:
        submod.setres(1,"ag_81160: not configured")
        return
    # Invalidate link
    retcode,res = submod.execcmd("inval_"+ag_81160["bus"],ag_81160["bus_id"])
    if retcode==0:
        submod.setres(0,"ag_81160: Error configuring link <- %s" % (res))
        return
    del ag_81160["configured"]
    submod.setres(1,"ok")

def reset_ag_81160(ag_81160_id):
    "Send RST signal to PG"
    try:
        ag_81160 = ag_81160_pool.get(ag_81160_id)
    except Exception as e:
        submod.setres(0,"ag_81160: ag_81160_%s" % (str(e)))
        return
    if "configured" not in ag_81160:
        submod.setres(0,"ag_81160: not configured")
        return
    command =  r"*RST\n"
    command += r"OUTP1:TRIG:ROUT NONE\n"
    command +=  "OUTP1:STR:ROUT NONE"
    retcode,res = submod.execcmd("write_"+ag_81160["bus"],ag_81160["bus_id"],command+r"\n")
    if retcode==0:
        submod.setres(0,"ag_81160: Error writing to link <- %s" % (res))
    retcode,errors = get_error_queue(ag_81160)
    if errors!="":
        submod.setres(0,"ag_81160: Error(s) returned from the PG : %s" % (errors))
    submod.setres(1,"ok")

def configure_sine_ag_81160(ag_81160_id, frequency, high_level, low_level, channel):
    "Configure ag_81160 to a sine wave with the specified parameters"
    retcode,res = set_function(ag_81160_id, "sine", channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_81160: %s" % (res))
        return
    retcode,res = set_frequency(ag_81160_id, frequency, channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_81160: %s" % (res))
        return
    retcode,res = set_high_level(ag_81160_id, high_level, channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_81160: %s" % (res))
        return
    retcode,res = set_low_level(ag_81160_id, low_level, channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_81160: %s" % (res))
        return
    submod.setres(1,"ok")

def configure_square_ag_81160(ag_81160_id, frequency, high_level, low_level, duty_cycle, channel):
    "Configure ag_81160 to a square wave with the specified parameters"
    retcode,res = set_function(ag_81160_id, "square", channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_81160: %s" % (res))
        return
    retcode,res = set_frequency(ag_81160_id, frequency, channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_81160: %s" % (res))
        return
    retcode,res = set_high_level(ag_81160_id, high_level, channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_81160: %s" % (res))
        return
    retcode,res = set_low_level(ag_81160_id, low_level, channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_81160: %s" % (res))
        return
    retcode,res = set_duty_cycle(ag_81160_id, duty_cycle, channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_81160: %s" % (res))
        return
    submod.setres(1,"ok")

def configure_ramp_ag_81160(ag_81160_id, frequency, high_level, low_level, symmetry, channel):
    "Configure ag_81160 to a ramp wave with the specified parameters"
    retcode,res = set_function(ag_81160_id, "ramp", channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_81160: %s" % (res))
        return
    retcode,res = set_frequency(ag_81160_id, frequency, channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_81160: %s" % (res))
        return
    retcode,res = set_high_level(ag_81160_id, high_level, channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_81160: %s" % (res))
        return
    retcode,res = set_low_level(ag_81160_id, low_level, channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_81160: %s" % (res))
        return
    retcode,res = set_symmetry(ag_81160_id, symmetry, channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_81160: %s" % (res))
        return
    submod.setres(1,"ok")

def configure_pulse_ag_81160(ag_81160_id, frequency, high_level, low_level, pulse_width, rising_edge, falling_edge, channel):
    "Configure ag_81160 to a pulse train with the specified parameters"
    retcode,res = set_function(ag_81160_id, "pulse", channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_81160: %s" % (res))
        return
    retcode,res = set_frequency(ag_81160_id, frequency, channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_81160: %s" % (res))
        return
    retcode,res = set_high_level(ag_81160_id, high_level, channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_81160: %s" % (res))
        return
    retcode,res = set_low_level(ag_81160_id, low_level, channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_81160: %s" % (res))
        return
    retcode,res = set_pulse_width(ag_81160_id, pulse_width, channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_81160: %s" % (res))
        return
    retcode,res = set_edges(ag_81160_id, rising_edge, falling_edge, channel)
    if (retcode == 0):
        submod.setres(retcode,"ag_81160: %s" % (res))
        return
    submod.setres(1,"ok")

def power_on(ag_81160_id, channel):
    try:
        ag_81160 = ag_81160_pool.get(ag_81160_id)
    except Exception as e:
        return 0,"ag_81160_%s" % (str(e))
    if "configured" not in ag_81160:
        return 0,"not configured"
    # Verify channel
    if channel=="undef" or channel=="":
        return 0,"Channel must be specified"
    if int(channel) not in range(1,2+1):
        return 0,"Invalid channel"
    # Send the command
    command = "OUTP{0} ON".format(channel)
    retcode,res = submod.execcmd("write_"+ag_81160["bus"],ag_81160["bus_id"],command+r"\n")
    if retcode==0:
        return 0,"Error writing to link <- %s" % (res)
    retcode,errors = get_error_queue(ag_81160)
    if errors!="":
        return 0,"Error(s) returned from the PG : %s" % (errors)
    return 1,"ok"

def power_on_ag_81160(ag_81160_id,channel):
    "Turn on"
    retcode,res = power_on(ag_81160_id,channel)
    if retcode==0:
        submod.setres(0,"ag_81160: %s" % (res))
    submod.setres(retcode,res)

def power_off(ag_81160_id,channel):
    try:
        ag_81160 = ag_81160_pool.get(ag_81160_id)
    except Exception as e:
        return 0,"ag_81160_%s" % (str(e))
    if "configured" not in ag_81160:
        return 0,"not configured"
    # Verify channel
    if channel=="undef" or channel=="":
        return 0,"Channel must be specified"
    if int(channel) not in range(1,2+1):
        return 0,"Invalid channel"
    # Send the command
    command = "OUTP{0} OFF".format(channel)
    retcode,res = submod.execcmd("write_"+ag_81160["bus"],ag_81160["bus_id"],command+r"\n")
    if retcode==0:
        return 0,"Error writing to link <- %s" % (res)
    retcode,errors = get_error_queue(ag_81160)
    if errors!="":
        return 0,"Error(s) returned from the PG : %s" % (errors)
    return 1,"ok"

def power_off_ag_81160(ag_81160_id,channel):
    "Turn off"
    retcode,res = power_off(ag_81160_id,channel)
    if retcode==0:
        submod.setres(0,"ag_81160: %s" % (res))
    submod.setres(retcode,res)

def set_function(ag_81160_id,function,channel):
    try:
        ag_81160 = ag_81160_pool.get(ag_81160_id)
    except Exception as e:
        return 0,"ag_81160_%s" % (str(e))
    if "configured" not in ag_81160:
        return 0,"not configured"
    # Verify channel
    if channel=="undef" or channel=="":
        return 0,"Channel must be specified"
    if int(channel) not in range(1,2+1):
        return 0,"Invalid channel"
    # Verify consistency of parameters
    if function not in ["sine", "square", "ramp", "pulse"]:
        return 0,"invalid function"
    if ag_81160["cache_func"][int(channel)-1]!=function:
        # Send the command
        value = { "sine":"SIN", "square":"SQU", "ramp":"RAMP", "pulse":"PULS" }.get(function)
        command = "FUNC{0} {1}".format(channel,value)
        retcode,res = submod.execcmd("write_"+ag_81160["bus"],ag_81160["bus_id"],command+r"\n")
        if retcode==0:
            return 0,"Error writing to link <- %s" % (res)
        retcode,errors = get_error_queue(ag_81160)
        if errors!="":
            return 0,"Error(s) returned from the PG : %s" % (errors)
        ag_81160["cache_func"][int(channel)-1] = function
    return 1,"ok"

def set_function_ag_81160(ag_81160_id,function,channel):
    "Set function, where function is 'sine', 'square', 'ramp', 'pulse'"
    retcode,res = set_function(ag_81160_id,function,channel)
    if retcode==0:
        submod.setres(0,"ag_81160: %s" % (res))
    submod.setres(retcode,res)

def set_high_level(ag_81160_id,high_level,channel):
    try:
        ag_81160 = ag_81160_pool.get(ag_81160_id)
    except Exception as e:
        return 0,"ag_81160_%s" % (str(e))
    if "configured" not in ag_81160:
        return 0,"not configured"
    # Verify channel
    if channel=="undef" or channel=="":
        return 0,"Channel must be specified"
    if int(channel) not in range(1,2+1):
        return 0,"Invalid channel"
    if ag_81160["cache_hl"][int(channel)-1]!=high_level and high_level!="undef" and high_level!="":
        # Send the command
        value = float(high_level)
        command = "VOLT{0}:HIGH {1:.5e}".format(channel,value)
        retcode,res = submod.execcmd("write_"+ag_81160["bus"],ag_81160["bus_id"],command+r"\n")
        if retcode==0:
            return 0,"Error writing to link <- %s" % (res)
        retcode,errors = get_error_queue(ag_81160)
        if errors!="":
            return 0,"Error(s) returned from the PG : %s" % (errors)
        ag_81160["cache_hl"][int(channel)-1] = high_level
    return 1,"ok"

def set_high_level_ag_81160(ag_81160_id,high_level,channel):
    "Set high level value in Volts."
    retcode,res = set_high_level(ag_81160_id,high_level,channel)
    if retcode==0:
        submod.setres(0,"ag_81160: %s" % (res))
    submod.setres(retcode,res)

def set_low_level(ag_81160_id,low_level,channel):
    try:
        ag_81160 = ag_81160_pool.get(ag_81160_id)
    except Exception as e:
        return 0,"ag_81160_%s" % (str(e))
    if "configured" not in ag_81160:
        return 0,"not configured"
    # Verify channel
    if channel=="undef" or channel=="":
        return 0,"Channel must be specified"
    if int(channel) not in range(1,2+1):
        return 0,"Invalid channel"
    if ag_81160["cache_ll"][int(channel)-1]!=low_level and low_level!="undef" and low_level!="":
        # Send the command
        value = float(low_level)
        command = "VOLT{0}:LOW {1:.5e}".format(channel,value)
        retcode,res = submod.execcmd("write_"+ag_81160["bus"],ag_81160["bus_id"],command+r"\n")
        if retcode==0:
            return 0,"Error writing to link <- %s" % (res)
        retcode,errors = get_error_queue(ag_81160)
        if errors!="":
            return 0,"Error(s) returned from the PG : %s" % (errors)
        ag_81160["cache_ll"][int(channel)-1] = low_level
    return 1,"ok"

def set_low_level_ag_81160(ag_81160_id,low_level,channel):
    "Set low level value in Volts."
    retcode,res = set_low_level(ag_81160_id,low_level,channel)
    if retcode==0:
        submod.setres(0,"ag_81160: %s" % (res))
    submod.setres(retcode,res)

def set_frequency(ag_81160_id,frequency,channel):
    try:
        ag_81160 = ag_81160_pool.get(ag_81160_id)
    except Exception as e:
        return 0,"ag_81160_%s" % (str(e))
    if "configured" not in ag_81160:
        return 0,"not configured"
    # Verify channel
    if channel=="undef" or channel=="":
        return 0,"Channel must be specified"
    if int(channel) not in range(1,2+1):
        return 0,"Invalid channel"
    if ag_81160["cache_freq"][int(channel)-1]!=frequency and frequency!="undef" and frequency!="":
        # Send the command
        value = float(frequency)
        command = "FREQ{0} {1:.12e}".format(channel,value)
        retcode,res = submod.execcmd("write_"+ag_81160["bus"],ag_81160["bus_id"],command+r"\n")
        if retcode==0:
            return 0,"Error writing to link <- %s" % (res)
        retcode,errors = get_error_queue(ag_81160)
        if errors!="":
            return 0,"Error(s) returned from the PG : %s" % (errors)
        ag_81160["cache_freq"][int(channel)-1] = frequency
    return 1,"ok"

def set_frequency_ag_81160(ag_81160_id,frequency,channel):
    "Set frequency in Hertz."
    retcode,res = set_frequency(ag_81160_id,frequency,channel)
    if retcode==0:
        submod.setres(0,"ag_81160: %s" % (res))
    submod.setres(retcode,res)

def set_duty_cycle(ag_81160_id,duty_cycle,channel):
    try:
        ag_81160 = ag_81160_pool.get(ag_81160_id)
    except Exception as e:
        return 0,"ag_81160_%s" % (str(e))
    if "configured" not in ag_81160:
        return 0,"not configured"
    # Verify channel
    if channel=="undef" or channel=="":
        return 0,"Channel must be specified"
    if int(channel) not in range(1,2+1):
        return 0,"Invalid channel"
    if ag_81160["cache_dc"][int(channel)-1]!=duty_cycle and duty_cycle!="undef" and duty_cycle!="":
        # Send the command
        value = float(duty_cycle)
        command = "FUNC{0}:SQU:DCYC {1:.9e}".format(channel,value)
        retcode,res = submod.execcmd("write_"+ag_81160["bus"],ag_81160["bus_id"],command+r"\n")
        if retcode==0:
            return 0,"Error writing to link <- %s" % (res)
        retcode,errors = get_error_queue(ag_81160)
        if errors!="":
            return 0,"Error(s) returned from the PG : %s" % (errors)
        ag_81160["cache_dc"][int(channel)-1] = duty_cycle
    return 1,"ok"

def set_duty_cycle_ag_81160(ag_81160_id,duty_cycle,channel):
    "Set duty cycle of square function. Duty cycle ranges from 0 to 100."
    retcode,res = set_duty_cycle(ag_81160_id,duty_cycle,channel)
    if retcode==0:
        submod.setres(0,"ag_81160: %s" % (res))
    submod.setres(retcode,res)

def set_pulse_width(ag_81160_id,pulse_width,channel):
    try:
        ag_81160 = ag_81160_pool.get(ag_81160_id)
    except Exception as e:
        return 0,"ag_81160_%s" % (str(e))
    if "configured" not in ag_81160:
        return 0,"not configured"
    # Verify channel
    if channel=="undef" or channel=="":
        return 0,"Channel must be specified"
    if int(channel) not in range(1,2+1):
        return 0,"Invalid channel"
    if ag_81160["cache_pw"][int(channel)-1]!=pulse_width and pulse_width!="undef" and pulse_width!="":
        # Send the command
        value = float(pulse_width)
        command = "FUNC{0}:PULS:WIDT {1:.4e}".format(channel,value)
        retcode,res = submod.execcmd("write_"+ag_81160["bus"],ag_81160["bus_id"],command+r"\n")
        if retcode==0:
            return 0,"Error writing to link <- %s" % (res)
        retcode,errors = get_error_queue(ag_81160)
        if errors!="":
            return 0,"Error(s) returned from the PG : %s" % (errors)
        ag_81160["cache_pw"][int(channel)-1] = pulse_width
    return 1,"ok"

def set_pulse_width_ag_81160(ag_81160_id,pulse_width,channel):
    "Set pulse width of pulse function in seconds."
    retcode,res = set_pulse_width(ag_81160_id,pulse_width,channel)
    if retcode==0:
        submod.setres(0,"ag_81160: %s" % (res))
    submod.setres(retcode,res)

def set_edges(ag_81160_id,rising_edge,falling_edge,channel):
    try:
        ag_81160 = ag_81160_pool.get(ag_81160_id)
    except Exception as e:
        return 0,"ag_81160_%s" % (str(e))
    if "configured" not in ag_81160:
        return 0,"not configured"
    # Verify channel
    if channel=="undef" or channel=="":
        return 0,"Channel must be specified"
    if int(channel) not in range(1,2+1):
        return 0,"Invalid channel"
    # Rising edge
    if ag_81160["cache_re"][int(channel)-1]!=rising_edge and rising_edge!="undef" and rising_edge!="":
        # Verify edges
        if rising_edge not in ["MIN","min","MAX","max"]:
            value_r = "{0:.9f}".format(float(rising_edge))
        else:
            value_r = rising_edge
        # Send the command
        command = "FUNC{0}:PULS:TRAN:LEAD {1}".format(channel,value_r)
        retcode,res = submod.execcmd("write_"+ag_81160["bus"],ag_81160["bus_id"],command+r"\n")
        if retcode==0:
            return 0,"Error writing to link <- %s" % (res)
        retcode,errors = get_error_queue(ag_81160)
        if errors!="":
            return 0,"Error(s) returned from the PG : %s" % (errors)
        ag_81160["cache_re"][int(channel)-1] = rising_edge
    # Falling edge
    if ag_81160["cache_fe"][int(channel)-1]!=falling_edge and falling_edge!="undef" and falling_edge!="":
        # Verify edges
        if falling_edge not in ["MIN","min","MAX","max"]:
            value_f = "{0:.9f}".format(float(falling_edge))
        else:
            value_f = falling_edge
        # Send the command
        command = "FUNC{0}:PULS:TRAN:TRA {1}".format(channel,value_f)
        retcode,res = submod.execcmd("write_"+ag_81160["bus"],ag_81160["bus_id"],command+r"\n")
        if retcode==0:
            return 0,"Error writing to link <- %s" % (res)
        retcode,errors = get_error_queue(ag_81160)
        if errors!="":
            return 0,"Error(s) returned from the PG : %s" % (errors)
        ag_81160["cache_fe"][int(channel)-1] = falling_edge
    return 1,"ok"

def set_edges_ag_81160(ag_81160_id,rising_edge,falling_edge,channel):
    "Set raising and falling edges duration in seconds for pulse function."
    retcode,res = set_edges(ag_81160_id,rising_edge,falling_edge,channel)
    if retcode==0:
        submod.setres(0,"ag_81160: %s" % (res))
    submod.setres(retcode,res)

def set_symmetry(ag_81160_id,symmetry,channel):
    try:
        ag_81160 = ag_81160_pool.get(ag_81160_id)
    except Exception as e:
        return 0,"ag_81160_%s" % (str(e))
    if "configured" not in ag_81160:
        return 0,"not configured"
    # Verify channel
    if channel=="undef" or channel=="":
        return 0,"Channel must be specified"
    if int(channel) not in range(1,2+1):
        return 0,"Invalid channel"
    if ag_81160["cache_sym"][int(channel)-1]!=symmetry and symmetry!="undef" and symmetry!="":
        # Send the command
        value = float(symmetry)
        command = "FUNC{0}:RAMP:SYMM {1:.9e}".format(channel,value)
        retcode,res = submod.execcmd("write_"+ag_81160["bus"],ag_81160["bus_id"],command+r"\n")
        if retcode==0:
            return 0,"Error writing to link <- %s" % (res)
        retcode,errors = get_error_queue(ag_81160)
        if errors!="":
            return 0,"Error(s) returned from the PG : %s" % (errors)
        ag_81160["cache_sym"][int(channel)-1] = symmetry
    return 1,"ok"

def set_symmetry_ag_81160(ag_81160_id,symmetry,channel):
    "Set symmetry for ramp functions. symmetry ranges from 0 to 100."
    retcode,res = set_symmetry(ag_81160_id,symmetry,channel)
    if retcode==0:
        submod.setres(0,"ag_81160: %s" % (res))
    submod.setres(retcode,res)

def set_phase(ag_81160_id,phase,channel):
    try:
        ag_81160 = ag_81160_pool.get(ag_81160_id)
    except Exception as e:
        return 0,"ag_81160_%s" % (str(e))
    if "configured" not in ag_81160:
        return 0,"not configured"
    # Verify channel
    if channel=="undef" or channel=="":
        return 0,"Channel must be specified"
    if int(channel) not in range(1,2+1):
        return 0,"Invalid channel"
    if ag_81160["cache_phase"][int(channel)-1]!=phase and phase!="undef" and phase!="":
        # Send the command
        value = float(phase)
        command = r"FUNC{0}:PULSE:DEL:UNIT DEG\n".format(channel,value)
        command += "FUNC{0}:PULSE:DEL {1:.9e}".format(channel,value)
        retcode,res = submod.execcmd("write_"+ag_81160["bus"],ag_81160["bus_id"],command+r"\n")
        if retcode==0:
            return 0,"Error writing to link <- %s" % (res)
        retcode,errors = get_error_queue(ag_81160)
        if errors!="":
            return 0,"Error(s) returned from the PG : %s" % (errors)
        ag_81160["cache_phase"][int(channel)-1] = phase
    return 1,"ok"

def set_phase_ag_81160(ag_81160_id,phase,channel):
    "Set phase of output in degrees. Phase ranges from -360 to +360 degrees."
    retcode,res = set_phase(ag_81160_id,phase,channel)
    if retcode==0:
        submod.setres(0,"ag_81160: %s" % (res))
    submod.setres(retcode,res)

def set_sync(ag_81160_id,sync,channel):
    try:
        ag_81160 = ag_81160_pool.get(ag_81160_id)
    except Exception as e:
        return 0,"ag_81160_%s" % (str(e))
    if "configured" not in ag_81160:
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
    if ag_81160["cache_sync"][int(channel)-1]!=sync:
        # Send the command
        command =  "OUTP{0}:TRIG:ROUT ".format(channel)
        command += ("SYNA" if channel == "1" else "SYNB") if sync else "NONE"
        retcode,res = submod.execcmd("write_"+ag_81160["bus"],ag_81160["bus_id"],command+r"\n")
        if retcode==0:
            return 0,"Error turning on ag_81160 %d sync <- %s" % (ag_81160.id,res)
        retcode,errors = get_error_queue(ag_81160)
        if errors!="":
            return 0,"Error(s) returned from the PG : %s" % (errors)
        ag_81160["cache_sync"][int(channel)-1] = sync
    return 1,"ok"

def set_sync_ag_81160(ag_81160_id,sync,channel):
    "Select sync source with channel and turn sync on (1) or off (0). Channels 1 and 2 always go to Sync Out A and B, respectively."
    retcode,res = set_sync(ag_81160_id,sync,channel)
    if retcode==0:
        submod.setres(0,"ag_81160: %s" % (res))
    submod.setres(retcode,res)

def get_error_queue_ag_81160(ag_81160_id):
    "Read error queue until the end (code 0)"
    try:
        ag_81160 = ag_81160_pool.get(ag_81160_id)
    except Exception as e:
        return 0,"ag_81160_%s" % (str(e))
    if "configured" not in ag_81160:
        return 0,"not configured"
    retcode,res = get_error_queue(ag_81160)
    if retcode==0:
        submod.setres(0,"ag_81160: %s" % (res))
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

