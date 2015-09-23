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

ag_33200_pool = pools.pool()

from time import sleep

# Put serialized API in memory if not called via import
if __name__ == '__main__':
    global api; api = getapi.load_api(__file__)

# Functions
def getapi_ag_33200():
    submod.setres(1,api)

def init_ag_33200(conf_string):
    """Initialize ag_33200 pattern generator.
    
    *conf_string*: must include a bus parameter with the conf_string of the underlying link module (gpib, tcp, serial, ...)

    Returns ag_33200_id"""

    try:
        conf = conf_strings.parse(conf_string)
    except Exception as e:
        submod.setres(0,str(e))
        return
    if conf.name!="ag_33200":
        submod.setres(0,"ag_33200: Invalid module name %s in conf_string instead of ag_33200"%(conf.name))
        return
    if not conf.has("bus"):
        submod.setres(0,"ag_33200: Error: a required parameter in conf_string is not present")
        return
    try:
        conf_bus = conf_strings.parse(conf.params["bus"])
    except Exception as e:
        submod.setres(0,"ag_33200: %s" % (str(e)))
        return
    retcode,res = submod.execcmd("init_"+conf_bus.name,conf.params["bus"])
    if retcode==0:
        submod.setres(0,"ag_33200: Error initializing link <- %s" % (res))
        return
    ag_33200_id = ag_33200_pool.new({
        "bus": conf_bus.name,
        "bus_id": res,
        "cache_func": "",
        "cache_freq": "",
        "cache_hl": "",
        "cache_ll": "",
        "cache_dc": "",
        "cache_sym": "",
        "cache_pw": "",
        "cache_e": "",
        "cache_phase": "",
        "cache_sync": -1})
    submod.setres(1,ag_33200_id)

def deinit_ag_33200(ag_33200_id):
    "Deregister an ag_33200 from the pool"
    try:
        ag_33200 = ag_33200_pool.get(ag_33200_id)
    except Exception as e:
        submod.setres(1,"ag_33200: ag_33200_%s" % (str(e)))
        return
    # Deinitialize link
    retcode,res = submod.execcmd("deinit_"+ag_33200["bus"],ag_33200["bus_id"])
    if retcode==0:
        submod.setres(0,"ag_33200: Error deinitializing link <- %s" % (res))
        return
    # Remove ag_33200 from the pool
    try:
        ag_33200_pool.remove(ag_33200_id)
    except Exception as e:
        submod.setres(0,"ag_33200: %s" % (str(e)))
        return
    submod.setres(1,"ok")

def config_ag_33200(ag_33200_id):
    try:
        ag_33200 = ag_33200_pool.get(ag_33200_id)
    except Exception as e:
        submod.setres(0,"ag_33200: ag_33200_%s" % (str(e)))
        return
    # Configure link
    retcode,res = submod.execcmd("config_"+ag_33200["bus"],ag_33200["bus_id"])
    if retcode==0:
        submod.setres(0,"ag_33200: Error configuring link <- %s" % (res))
        return
    # Cleanup error queue
    retcode,errors = get_error_queue(ag_33200)
    if retcode==0:
        _,_ = submod.execcmd("inval_"+ag_33200["bus"],ag_33200["bus_id"])
        submod.setres(0,"ag_33200: Error cleaning up the error queue : %s" % (errors))
        return
    ag_33200["configured"] = True
    submod.setres(1,"ok")

def inval_ag_33200(ag_33200_id):
    try:
        ag_33200 = ag_33200_pool.get(ag_33200_id)
    except Exception as e:
        submod.setres(0,"ag_33200: ag_33200_%s" % (str(e)))
        return
    if not "configured" in ag_33200:
        submod.setres(1,"ag_33200: not configured")
        return
    # Invalidate link
    retcode,res = submod.execcmd("inval_"+ag_33200["bus"],ag_33200["bus_id"])
    if retcode==0:
        submod.setres(0,"ag_33200: Error configuring link <- %s" % (res))
        return
    del ag_33200["configured"]
    submod.setres(1,"ok")

def reset_ag_33200(ag_33200_id):
    "Send RST signal to PG"
    try:
        ag_33200 = ag_33200_pool.get(ag_33200_id)
    except Exception as e:
        submod.setres(0,"ag_33200: ag_33200_%s" % (str(e)))
        return
    if "configured" not in ag_33200:
        submod.setres(0,"ag_33200: not configured")
        return
    command = "*RST"
    retcode,res = submod.execcmd("write_"+ag_33200["bus"],ag_33200["bus_id"],command+r"\n")
    if retcode==0:
        submod.setres(0,"ag_33200: Error writing to link <- %s" % (res))
    retcode,errors = get_error_queue(ag_33200)
    if errors!="":
        submod.setres(0,"ag_33200: Error(s) returned from the PG : %s" % (errors))
    submod.setres(1,"ok")

def configure_sine_ag_33200(ag_33200_id, frequency, high_level, low_level):
    "Configure ag_33200 to a sine wave with the specified parameters"
    retcode,res = set_function(ag_33200_id, "sine")
    if retcode == 0:
        submod.setres(retcode,"ag_33200: %s"%(res))
        return
    retcode,res = set_frequency(ag_33200_id, frequency)
    if retcode == 0:
        submod.setres(retcode,"ag_33200: %s"%(res))
        return
    retcode,res = set_high_level(ag_33200_id, high_level)
    if retcode == 0:
        submod.setres(retcode,"ag_33200: %s"%(res))
        return
    retcode,res = set_low_level(ag_33200_id, low_level)
    if retcode == 0:
        submod.setres(retcode,"ag_33200: %s"%(res))
        return
    submod.setres(1,"ok")

def configure_square_ag_33200(ag_33200_id, frequency, high_level, low_level, duty_cycle):
    "Configure ag_33200 to a square wave with the specified parameters"
    retcode,res = set_function(ag_33200_id, "square")
    if retcode == 0:
        submod.setres(retcode,"ag_33200: %s"%(res))
        return
    retcode,res = set_frequency(ag_33200_id, frequency)
    if retcode == 0:
        submod.setres(retcode,"ag_33200: %s"%(res))
        return
    retcode,res = set_high_level(ag_33200_id, high_level)
    if retcode == 0:
        submod.setres(retcode,"ag_33200: %s"%(res))
        return
    retcode,res = set_low_level(ag_33200_id, low_level)
    if retcode == 0:
        submod.setres(retcode,"ag_33200: %s"%(res))
        return
    retcode,res = set_duty_cycle(ag_33200_id, duty_cycle)
    if retcode == 0:
        submod.setres(retcode,"ag_33200: %s"%(res))
        return
    submod.setres(1,"ok")

def configure_ramp_ag_33200(ag_33200_id, frequency, high_level, low_level, symmetry):
    "Configure ag_33200 to a ramp wave with the specified parameters"
    retcode,res = set_function(ag_33200_id, "ramp")
    if retcode == 0:
        submod.setres(retcode,"ag_33200: %s"%(res))
        return
    retcode,res = set_frequency(ag_33200_id, frequency)
    if retcode == 0:
        submod.setres(retcode,"ag_33200: %s"%(res))
        return
    retcode,res = set_high_level(ag_33200_id, high_level)
    if retcode == 0:
        submod.setres(retcode,"ag_33200: %s"%(res))
        return
    retcode,res = set_low_level(ag_33200_id, low_level)
    if retcode == 0:
        submod.setres(retcode,"ag_33200: %s"%(res))
        return
    retcode,res = set_symmetry(ag_33200_id, symmetry)
    if retcode == 0:
        submod.setres(retcode,"ag_33200: %s"%(res))
        return
    submod.setres(1,"ok")

def configure_pulse_ag_33200(ag_33200_id, frequency, high_level, low_level, pulse_width, rising_edge, falling_edge):
    "Configure ag_33200 to a pulse train with the specified parameters"
    retcode,res = set_function(ag_33200_id, "pulse")
    if retcode == 0:
        submod.setres(retcode,"ag_33200: %s"%(res))
        return
    retcode,res = set_frequency(ag_33200_id, frequency)
    if retcode == 0:
        submod.setres(retcode,"ag_33200: %s"%(res))
        return
    retcode,res = set_high_level(ag_33200_id, high_level)
    if retcode == 0:
        submod.setres(retcode,"ag_33200: %s"%(res))
        return
    retcode,res = set_low_level(ag_33200_id, low_level)
    if retcode == 0:
        submod.setres(retcode,"ag_33200: %s"%(res))
        return
    retcode,res = set_pulse_width(ag_33200_id, pulse_width)
    if retcode == 0:
        submod.setres(retcode,"ag_33200: %s"%(res))
        return
    retcode,res = set_edges(ag_33200_id, rising_edge, falling_edge)
    if retcode == 0:
        submod.setres(retcode,"ag_33200: %s"%(res))
        return
    submod.setres(1,"ok")

def power_on(ag_33200_id):
    try:
        ag_33200 = ag_33200_pool.get(ag_33200_id)
    except Exception as e:
        return 0,"ag_33200_%s" % (str(e))
    if "configured" not in ag_33200:
        return 0,"not configured"
    command = "OUTP ON"
    retcode,res = submod.execcmd("write_"+ag_33200["bus"],ag_33200["bus_id"],command+r"\n")
    if retcode==0:
        return 0,"Error writing to link <- %s" % (res)
    retcode,errors = get_error_queue(ag_33200)
    if errors!="":
        return 0,"Error(s) returned from the PG : %s" % (errors)
    return 1,"ok"

def power_on_ag_33200(ag_33200_id):
    "Turn on"
    retcode,res = power_on(ag_33200_id)
    if retcode==0:
        submod.setres(0,"ag_33200: %s" % (res))
    submod.setres(retcode,res)

def power_off(ag_33200_id):
    try:
        ag_33200 = ag_33200_pool.get(ag_33200_id)
    except Exception as e:
        return 0,"ag_33200_%s" % (str(e))
    if "configured" not in ag_33200:
        return 0,"not configured"
    command = "OUTP OFF"
    retcode,res = submod.execcmd("write_"+ag_33200["bus"],ag_33200["bus_id"],command+r"\n")
    if retcode==0:
        return 0,"Error writing to link <- %s" % (res)
    retcode,errors = get_error_queue(ag_33200)
    if errors!="":
        return 0,"Error(s) returned from the PG : %s" % (errors)
    return 1,"ok"

def power_off_ag_33200(ag_33200_id):
    "Turn off"
    retcode,res = power_off(ag_33200_id)
    if retcode==0:
        submod.setres(0,"ag_33200: %s" % (res))
    submod.setres(retcode,res)

def set_function(ag_33200_id,function):
    try:
        ag_33200 = ag_33200_pool.get(ag_33200_id)
    except Exception as e:
        return 0,"ag_33200_%s" % (str(e))
    if "configured" not in ag_33200:
        return 0,"not configured"
    # Verify consistency of parameters
    if function not in ["sine", "square", "ramp", "pulse"]:
        return 0,"invalid function"
    if ag_33200["cache_func"]!=function:
        # Send the command
        value = { "sine":"SIN", "square":"SQU", "ramp":"RAMP", "pulse":"PULS" }.get(function)
        command = "FUNC %s" % (value)
        retcode,res = submod.execcmd("write_"+ag_33200["bus"],ag_33200["bus_id"],command+r"\n")
        if retcode==0:
            return 0,"Error writing to link <- %s" % (res)
        retcode,errors = get_error_queue(ag_33200)
        if errors!="":
            return 0,"Error(s) returned from the PG : %s" % (errors)
        ag_33200["cache_func"] = function
    return 1,"ok"

def set_function_ag_33200(ag_33200_id,function):
    "Set function, where function is 'sine', 'square', 'ramp', 'pulse'"
    retcode,res = set_function(ag_33200_id,function)
    if retcode==0:
        submod.setres(0,"ag_33200: %s" % (res))
    submod.setres(retcode,res)

def set_high_level(ag_33200_id,high_level):
    try:
        ag_33200 = ag_33200_pool.get(ag_33200_id)
    except Exception as e:
        return 0,"ag_33200_%s" % (str(e))
    if "configured" not in ag_33200:
        return 0,"not configured"
    if ag_33200["cache_hl"]!=high_level and high_level!="undef" and high_level!="":
        # Send the command
        value = float(high_level)
        command = "VOLT:HIGH {0:.4f}".format(value)
        retcode,res = submod.execcmd("write_"+ag_33200["bus"],ag_33200["bus_id"],command+r"\n")
        if retcode==0:
            return 0,"Error writing to link <- %s" % (res)
        retcode,errors = get_error_queue(ag_33200)
        if errors!="":
            return 0,"Error(s) returned from the PG : %s" % (errors)
        ag_33200["cache_hl"] = high_level
    return 1,"ok"

def set_high_level_ag_33200(ag_33200_id,high_level):
    "Set high level value in Volts."
    retcode,res = set_high_level(ag_33200_id,high_level)
    if retcode==0:
        submod.setres(0,"ag_33200: %s" % (res))
    submod.setres(retcode,res)

def set_low_level(ag_33200_id,low_level):
    try:
        ag_33200 = ag_33200_pool.get(ag_33200_id)
    except Exception as e:
        return 0,"ag_33200_%s" % (str(e))
    if "configured" not in ag_33200:
        return 0,"not configured"
    if ag_33200["cache_ll"]!=low_level and low_level!="undef" and low_level!="":
        # Send the command
        value = float(low_level)
        command = "VOLT:LOW {0:.4f}".format(value)
        retcode,res = submod.execcmd("write_"+ag_33200["bus"],ag_33200["bus_id"],command+r"\n")
        if retcode==0:
            return 0,"Error writing to link <- %s" % (res)
        retcode,errors = get_error_queue(ag_33200)
        if errors!="":
            return 0,"Error(s) returned from the PG : %s" % (errors)
        ag_33200["cache_ll"] = low_level
    return 1,"ok"

def set_low_level_ag_33200(ag_33200_id,low_level):
    "Set low level value in Volts."
    retcode,res = set_low_level(ag_33200_id,low_level)
    if retcode==0:
        submod.setres(0,"ag_33200: %s" % (res))
    submod.setres(retcode,res)

def set_frequency(ag_33200_id,frequency):
    try:
        ag_33200 = ag_33200_pool.get(ag_33200_id)
    except Exception as e:
        return 0,"ag_33200_%s" % (str(e))
    if "configured" not in ag_33200:
        return 0,"not configured"
    if ag_33200["cache_freq"]!=frequency and frequency!="undef" and frequency!="":
        # Send the command
        value = float(frequency)
        command = "FREQ {0:.6f}".format(value)
        retcode,res = submod.execcmd("write_"+ag_33200["bus"],ag_33200["bus_id"],command+r"\n")
        if retcode==0:
            return 0,"Error writing to link <- %s" % (res)
        retcode,errors = get_error_queue(ag_33200)
        if errors!="":
            return 0,"Error(s) returned from the PG : %s" % (errors)
        ag_33200["cache_freq"] = frequency
    return 1,"ok"

def set_frequency_ag_33200(ag_33200_id,frequency):
    "Set frequency in Hertz."
    retcode,res = set_frequency(ag_33200_id,frequency)
    if retcode==0:
        submod.setres(0,"ag_33200: %s" % (res))
    submod.setres(retcode,res)

def get_frequency_ag_33200(ag_33200_id):
    "Get frequency in Hertz."
    try:
        ag_33200 = ag_33200_pool.get(ag_33200_id)
    except Exception as e:
        submod.setres(0,"ag_33200: ag_33200_%s" % (str(e)))
        return
    if "configured" not in ag_33200:
        submod.setres(0,"ag_33200: not configured")
        return
    # Send the command
    command = "FREQ?"
    retcode,res = submod.execcmd("wrnrd_until_"+ag_33200["bus"],ag_33200["bus_id"],command+r"\n",r"\n")
    if retcode==0:
        submod.setres(0,"ag_33200: Error writing and reading to link <- %s" % (res))
        return
    retcode,errors = get_error_queue(ag_33200)
    if errors!="":
        submod.setres(0,"ag_33200: Error(s) returned from the PG : %s" % (errors))
        return
    submod.setres(1,res)

def set_duty_cycle(ag_33200_id,duty_cycle):
    try:
        ag_33200 = ag_33200_pool.get(ag_33200_id)
    except Exception as e:
        return 0,"ag_33200_%s" % (str(e))
    if "configured" not in ag_33200:
        return 0,"not configured"
    if ag_33200["cache_dc"]!=duty_cycle and duty_cycle!="undef" and duty_cycle!="":
        # Send the command
        value = float(duty_cycle)
        command = "FUNC:SQU:DCYC {0:.4f}".format(value)
        retcode,res = submod.execcmd("write_"+ag_33200["bus"],ag_33200["bus_id"],command+r"\n")
        if retcode==0:
            return 0,"Error writing to link <- %s" % (res)
        retcode,errors = get_error_queue(ag_33200)
        if errors!="":
            return 0,"Error(s) returned from the PG : %s" % (errors)
        ag_33200["cache_dc"] = duty_cycle
    return 1,"ok"

def set_duty_cycle_ag_33200(ag_33200_id,duty_cycle):
    "Set duty cycle of square function. Duty cycle ranges from 0 to 100."
    retcode,res = set_duty_cycle(ag_33200_id,duty_cycle)
    if retcode==0:
        submod.setres(0,"ag_33200: %s" % (res))
    submod.setres(retcode,res)

def set_pulse_width(ag_33200_id,pulse_width):
    try:
        ag_33200 = ag_33200_pool.get(ag_33200_id)
    except Exception as e:
        return 0,"ag_33200_%s" % (str(e))
    if "configured" not in ag_33200:
        return 0,"not configured"
    if ag_33200["cache_pw"]!=pulse_width and pulse_width!="undef" and pulse_width!="":
        # Send the command
        value = float(pulse_width)
        command = "PULS:WIDT {0:.9f}".format(value)
        retcode,res = submod.execcmd("write_"+ag_33200["bus"],ag_33200["bus_id"],command+r"\n")
        if retcode==0:
            return 0,"Error writing to link <- %s" % (res)
        retcode,errors = get_error_queue(ag_33200)
        if errors!="":
            return 0,"Error(s) returned from the PG : %s" % (errors)
        ag_33200["cache_pw"] = pulse_width
    return 1,"ok"

def set_pulse_width_ag_33200(ag_33200_id,pulse_width):
    "Set pulse width of pulse function in seconds."
    retcode,res = set_pulse_width(ag_33200_id,pulse_width)
    if retcode==0:
        submod.setres(0,"ag_33200: %s" % (res))
    submod.setres(retcode,res)

def set_edges(ag_33200_id,rising_edge,falling_edge):
    try:
        ag_33200 = ag_33200_pool.get(ag_33200_id)
    except Exception as e:
        return 0,"ag_33200_%s" % (str(e))
    if "configured" not in ag_33200:
        return 0,"not configured"
    if ag_33200["cache_e"]!=rising_edge and rising_edge!="undef" and rising_edge!="":
        # Verify edges
        if rising_edge!=falling_edge:
            return 0,"Error, rising and falling edges must be equal"
        if rising_edge not in ["MIN","min","MAX","max"]:
            value = "{0:.9f}".format(float(rising_edge))
        else:
            value = rising_edge
        # Send the command
        command = "PULS:TRAN {0}".format(value)
        retcode,res = submod.execcmd("write_"+ag_33200["bus"],ag_33200["bus_id"],command+r"\n")
        if retcode==0:
            return 0,"Error writing to link <- %s" % (res)
        retcode,errors = get_error_queue(ag_33200)
        if errors!="":
            return 0,"Error(s) returned from the PG : %s" % (errors)
        ag_33200["cache_e"] = rising_edge
    return 1,"ok"

def set_edges_ag_33200(ag_33200_id,edge_time):
    "Set raising and falling edges duration in seconds for pulse function."
    retcode,res = set_edges(ag_33200_id,edge_time,edge_time)
    if retcode==0:
        submod.setres(0,"ag_33200: %s" % (res))
    submod.setres(retcode,res)

def set_symmetry(ag_33200_id,symmetry):
    try:
        ag_33200 = ag_33200_pool.get(ag_33200_id)
    except Exception as e:
        return 0,"ag_33200_%s" % (str(e))
    if "configured" not in ag_33200:
        return 0,"not configured"
    if ag_33200["cache_sym"]!=symmetry and symmetry!="undef" and symmetry!="":
        # Send the command
        value = float(symmetry)
        command = "FUNC:RAMP:SYMM {0:.4f}".format(value)
        retcode,res = submod.execcmd("write_"+ag_33200["bus"],ag_33200["bus_id"],command+r"\n")
        if retcode==0:
            return 0,"Error writing to link <- %s" % (res)
        retcode,errors = get_error_queue(ag_33200)
        if errors!="":
            return 0,"Error(s) returned from the PG : %s" % (errors)
        ag_33200["cache_sym"] = symmetry
    return 1,"ok"

def set_symmetry_ag_33200(ag_33200_id,symmetry):
    "Set symmetry for ramp functions. symmetry ranges from 0 to 100."
    retcode,res = set_symmetry(ag_33200_id,symmetry)
    if retcode==0:
        submod.setres(0,"ag_33200: %s" % (res))
    submod.setres(retcode,res)

def set_phase(ag_33200_id,phase):
    try:
        ag_33200 = ag_33200_pool.get(ag_33200_id)
    except Exception as e:
        return 0,"ag_33200_%s" % (str(e))
    if "configured" not in ag_33200:
        return 0,"not configured"
    if ag_33200["cache_phase"]!=phase and phase!="undef" and phase!="":
        # Send the command
        value = float(phase)
        command = "PHAS {0:.3f}".format(value)
        retcode,res = submod.execcmd("write_"+ag_33200["bus"],ag_33200["bus_id"],command+r"\n")
        if retcode==0:
            return 0,"Error writing to link <- %s" % (res)
        retcode,errors = get_error_queue(ag_33200)
        if errors!="":
            return 0,"Error(s) returned from the PG : %s" % (errors)
        ag_33200["cache_phase"] = phase
    return 1,"ok"

def set_phase_ag_33200(ag_33200_id,phase):
    "Set phase of output in degrees. Phase ranges from -360 to +360 degrees."
    retcode,res = set_phase(ag_33200_id,phase)
    if retcode==0:
        submod.setres(0,"ag_33200: %s" % (res))
    submod.setres(retcode,res)

def set_sync(ag_33200_id,sync):
    try:
        ag_33200 = ag_33200_pool.get(ag_33200_id)
    except Exception as e:
        return 0,"ag_33200_%s" % (str(e))
    if "configured" not in ag_33200:
        return 0,"not configured"
    # Verify parameter
    if sync=="undef" or sync=="":
        return 1,"ok"
    if sync not in ["0","1"]:
        return 0,"Invalid sync parameter"
    sync = int(sync)
    if ag_33200["cache_sync"]!=sync:
        # Send the command
        command = "OUTP:SYNC "
        command += "ON" if sync else "OFF"
        retcode,res = submod.execcmd("write_"+ag_33200["bus"],ag_33200["bus_id"],command+r"\n")
        if retcode==0:
            return 0,"Error turning on ag_33200 %d sync <- %s" % (ag_33200.id,res)
        retcode,errors = get_error_queue(ag_33200)
        if errors!="":
            return 0,"Error(s) returned from the PG : %s" % (errors)
        ag_33200["cache_sync"] = sync
    return 1,"ok"

def set_sync_ag_33200(ag_33200_id,sync):
    "Turn sync on (1) or off (0)"
    retcode,res = set_sync(ag_33200_id,sync)
    if retcode==0:
        submod.setres(0,"ag_33200: %s" % (res))
    submod.setres(retcode,res)

def get_error_queue_ag_33200(ag_33200_id):
    "Read error queue until the end (code 0)"
    try:
        ag_33200 = ag_33200_pool.get(ag_33200_id)
    except Exception as e:
        return 0,"ag_33200_%s" % (str(e))
    if "configured" not in ag_33200:
        return 0,"not configured"
    retcode,res = get_error_queue(ag_33200)
    if retcode==0:
        submod.setres(0,"ag_33200: %s" % (res))
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

