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

import pools, getapi, conf_strings, apipools

signal_pool = pools.pool()
pg_pool = pools.pool()
api_pool = apipools.api_pool()

from time import sleep

# Put serialized API in memory if not called via import
if __name__ == '__main__':
    global api; api = getapi.load_api(__file__)

# Functions
def getapi_signal():
    submod.setres(1,api)

def init_signal():
    """Initialize (create) a new signal.
    Returns id of signal *signal_id*"""
    signal_id = signal_pool.new({
        # Powered status flag (boolean: 1/0)
        "power": "undef",
        # id of associated PG
        "pg_id": -1,
        # Channel of PG pg_id to be used
        "channel": "undef",
        # Signal function ('sine', 'square', 'ramp', 'pulse')
        "function": "undef",
        #High level in Volts
        "high_level": "undef",
        # Low level in Volts
        "low_level": "undef",
        # Frequency in Hertz
        "frequency": "undef",
        # Duty cycle from 0 to 100
        "duty_cycle": "undef",
        # Pulse width in seconds
        "pulse_width": "undef",
        # Rising edge duration in seconds
        "rising_edge": "undef",
        # Falling edge duration in seconds
        "falling_edge": "undef",
        # Symmetry from 0 to 100
        "symmetry": "undef",
        # Phase in degrees
        "phase": "undef",
        # Output sync flag (boolean: 1/0)
        "sync": "undef"})
    submod.setres(1,signal_id)

def deinit_signal(signal_id):
    "Deinitialize signal *signal_id*"
    try:
        signal = signal_pool.get(signal_id)
    except Exception as e:
        submod.setres(1,"signal: signal_%s" % (str(e)))
        return
    pg_id = signal["pg_id"]
    # Remove signal from the pool
    try:
        signal_pool.remove(signal_id)
    except Exception as e:
        submod.setres(0,"signal: %s" % (str(e)))
        return
    # Look for pg_used in pool
    try:
        pg = pg_pool.get(pg_id)
    except Exception as e:
        submod.setres(1,"signal: pg_%s" % (str(e)))
        return
    used = False
    for _,signal in signal_pool.get_all():
        if signal["pg_id"] == pg_id:
            used = True
            break
    if used:
        # Deinitialize PG
        retcode,res=submod.execcmd("deinit_"+pg["model"],str(pg["model_id"]))
        if retcode==0:
            submod.setres(0,"signal: Error deinitializing %s pattern generator <- %s" % (pg["model"],res))
            return
        # Remove PG from the pool
        try:
            pg_pool.remove(pg_id)
        except Exception as e:
            submod.setres(0,"signal: pg_%s" % (str(e)))
            return
    submod.setres(1,"ok")

def init_pg_signal(conf_string):
    """Initialize pattern generator where *conf_string* is that of the instrument to initialize:

       Returns id of the pattern generator *pg_id*"""
    try:
        conf = conf_strings.parse(conf_string)
    except Exception as e:
        submod.setres(0,"signal: %s" % (str(e)))
        return
    # Initialize PG
    retcode,res=submod.execcmd("init_"+conf.name,conf_string)
    if retcode==0:
        submod.setres(0,"signal: Error initializing %s pattern generator <- %s" % (conf.name,res))
        return
    model_id = res
    # Get API of the module and add it to the api_pool, if it's not already there
    if not api_pool.is_present(conf.name):
        retcode,res=submod.execcmd("getapi_"+conf.name)
        if retcode==0:
            submod.setres(0,"signal: cant get API for %s  <- %s" % (conf.name,res))
            return
        api_pool.add_api_from_string(conf.name,res)
    pg_id = pg_pool.new({"model": conf.name, "model_id": model_id})
    submod.setres(1,pg_id)

def deinit_pg_signal(pg_id):
    try:
        pg = pg_pool.get(pg_id)
    except Exception as e:
        submod.setres(1,"signal: pg_%s" % (str(e)))
        return
    # Deinitialize PG
    retcode,res=submod.execcmd("deinit_"+pg["model"],str(pg["model_id"]))
    if retcode==0:
        submod.setres(0,"signal: Error deinitializing %s pattern generator <- %s" % (pg["model"],res))
        return
    # Unset this PG from signals
    for signal in signal_pool.get_all():
        if signal["pg_id"] == pg_id:
            signal["pg_id"] = -1
    # Remove PG from the pool
    try:
        pg_pool.remove(pg_id)
    except Exception as e:
        submod.setres(0,"signal: pg_%s" % (str(e)))
        return
    submod.setres(1,"ok")

def config_pg_signal(pg_id):
    try:
        pg = pg_pool.get(pg_id)
    except Exception as e:
        submod.setres(0,"signal: pg_%s" % (str(e)))
        return
    # Configure PG
    retcode,res=submod.execcmd("config_"+pg["model"],pg["model_id"])
    if retcode==0:
        submod.setres(0,"signal: Error configuring PG <- %s" % (res))
        return
    pg["configured"] = True
    submod.setres(1,"ok")

def inval_pg_signal(pg_id):
    try:
        pg = pg_pool.get(pg_id)
    except Exception as e:
        submod.setres(0,"signal: pg_%s" % (str(e)))
        return
    # Invalidate PG
    retcode,res=submod.execcmd("inval_"+pg["model"],pg["model_id"])
    if retcode==0:
        submod.setres(0,"signal: Error invalidating PG <- %s" % (res))
        return
    if "configured" in pg:
        del pg["configured"]
    submod.setres(1,"ok")


def set_pg_signal(signal_id,pg_id,channel="undef"):
    "Associate signal with the pattern generator *pg_id* and channel *channel*"
    try:
        signal = signal_pool.get(signal_id)
    except Exception as e:
        submod.setres(0,"signal: signal_%s" % (str(e)))
        return
    try:
        pg = pg_pool.get(pg_id)
    except Exception as e:
        submod.setres(0,"signal: pg_%s" % (str(e)))
        return
    signal["pg_id"] = pg_id
    if channel != "undef" and channel != "":
        signal["channel"] = channel
    submod.setres(1,"ok")

def set_function_signal(signal_id,function):
    "Set function of *signal_id*. Valid values are: 'sine', 'square', 'ramp', 'pulse'"
    try:
        signal = signal_pool.get(signal_id)
    except Exception as e:
        submod.setres(0,"signal: signal_%s" % (str(e)))
        return
    signal["function"] = function
    retcode,res=configure(signal_id,signal)
    if retcode==0:
        submod.setres(0,"signal: %s" % (res))
    submod.setres(retcode,res)

def set_high_level_signal(signal_id,high_level):
    "Set high level value of *signal_id* in Volts."
    try:
        signal = signal_pool.get(signal_id)
    except Exception as e:
        submod.setres(0,"signal: signal_%s" % (str(e)))
        return
    signal["high_level"] = high_level
    retcode,res=configure(signal_id,signal)
    if retcode==0:
        submod.setres(0,"signal: %s" % (res))
    submod.setres(retcode,res)

def set_low_level_signal(signal_id,low_level):
    "Set low level value of *signal_id* in Volts."
    try:
        signal = signal_pool.get(signal_id)
    except Exception as e:
        submod.setres(0,"signal: signal_%s" % (str(e)))
        return
    signal["low_level"] = low_level
    retcode,res=configure(signal_id,signal)
    if retcode==0:
        submod.setres(0,"signal: %s" % (res))
    submod.setres(retcode,res)

def set_frequency_signal(signal_id,frequency):
    "Set frequency of *signal_id* in Hertz."
    try:
        signal = signal_pool.get(signal_id)
    except Exception as e:
        submod.setres(0,"signal: signal_%s" % (str(e)))
        return
    signal["frequency"] = frequency
    retcode,res=configure(signal_id,signal)
    if retcode==0:
        submod.setres(0,"signal: %s" % (res))
    submod.setres(retcode,res)

def set_duty_cycle_signal(signal_id,duty_cycle):
    "Set duty cycle of *signal_id*. Ranges from 0 to 100."
    try:
        signal = signal_pool.get(signal_id)
    except Exception as e:
        submod.setres(0,"signal: signal_%s" % (str(e)))
        return
    signal["duty_cycle"] = duty_cycle
    retcode,res=configure(signal_id,signal)
    if retcode==0:
        submod.setres(0,"signal: %s" % (res))
    submod.setres(retcode,res)

def set_pulse_width_signal(signal_id,pulse_width):
    "Set width of pulse in seconds for *signal_id*."
    try:
        signal = signal_pool.get(signal_id)
    except Exception as e:
        submod.setres(0,"signal: signal_%s" % (str(e)))
        return
    signal["pulse_width"] = pulse_width
    retcode,res=configure(signal_id,signal)
    if retcode==0:
        submod.setres(0,"signal: %s" % (res))
    submod.setres(retcode,res)

def set_edges_signal(signal_id,rising_edge,falling_edge):
    "Set rising and falling edge duration in seconds for *signal_id* with pulse function. The parameters can also be 'MIN' and/or 'MAX'."
    try:
        signal = signal_pool.get(signal_id)
    except Exception as e:
        submod.setres(0,"signal: signal_%s" % (str(e)))
        return
    signal["rising_edge"] = rising_edge
    signal["falling_edge"] = falling_edge
    retcode,res=configure(signal_id,signal)
    if retcode==0:
        submod.setres(0,"signal: %s" % (res))
    submod.setres(retcode,res)

def set_symmetry_signal(signal_id,symmetry):
    "Set symmetry of *signal_id* with ramp function. Ranges from 0 to 100."
    try:
        signal = signal_pool.get(signal_id)
    except Exception as e:
        submod.setres(0,"signal: signal_%s" % (str(e)))
        return
    signal["symmetry"] = symmetry
    retcode,res=configure(signal_id,signal)
    if retcode==0:
        submod.setres(0,"signal: %s" % (res))
    submod.setres(retcode,res)

def set_phase_signal(signal_id,phase):
    "Set phase of *signal_id*. Ranges from -360 to +360 degrees."
    try:
        signal = signal_pool.get(signal_id)
    except Exception as e:
        submod.setres(0,"signal: signal_%s" % (str(e)))
        return
    signal["phase"]=phase
    retcode,res=configure(signal_id,signal)
    if retcode==0:
        submod.setres(0,"signal: %s" % (res))
    submod.setres(retcode,res)

def set_sync_signal(signal_id,sync):
    "Activate or deactivate output of sync associated to *signal_id*. *sync* can be 1 or 0."
    try:
        signal = signal_pool.get(signal_id)
    except Exception as e:
        submod.setres(0,"signal: signal_%s" % (str(e)))
        return
    if sync not in ["0","1"]:
        submod.setres(0,"signal: sync must be either 0 or 1")
        return
    signal["sync"] = sync
    retcode,res=configure(signal_id,signal)
    if retcode==0:
        submod.setres(0,"signal: %s" % (res))
    submod.setres(retcode,res)

def configure(signal_id,signal):
    "Configure signal *signal_id*"
    # Verify that function and pg have been configured
    if signal["function"] == "undef" or signal["function"] == "":
        return 0,"function is required to power on"
    if signal["pg_id"] == -1:
        return 0,"a PG is required"
    # Verify that no other signal with the same signal["pg"] and signal["channel"] is powered on
    for s_id,s in signal_pool.get_all():
        if s["pg_id"] == signal["pg_id"] and \
           s["channel"] == signal["channel"] and \
           s_id != int(signal_id) and \
           s["power"]:
            return 0,"signal {0} using the same PG and channel is already on".format(s_id)
    try:
        pg = pg_pool.get(signal["pg_id"])
    except Exception as e:
        submod.setres(0,"signal: pg_%s" % (str(e)))
        return
    # Call the configure function for the model
    api = api_pool.get_api(pg["model"],"configure_"+signal["function"]+"_"+pg["model"])
    if api == -1:
        return 0,"the selected PG model does not implement function {0}".format(signal["function"])
    parameters = list(signal[arg] for arg in api["args"] if arg in signal)
    retcode,res=submod.execcmd(api["function"],pg["model_id"],*parameters)
    if retcode==0:
        return 0,"Error configuring the PG <- %s" % (res)
    # Call the set_phase function for the model
    api = api_pool.get_api(pg["model"],"set_phase_"+pg["model"])
    if api == -1:
        if signal["phase"] != "undef":
            print("\n\nWarning: the selected PG model does not implement function {0} and phase is set\n\n".format("set_phase_"+pg["model"]))
    else:
        if "channel" in api["args"]:
            retcode,res=submod.execcmd(api["function"],pg["model_id"],signal["phase"],signal["channel"])
        else:
            if signal["channel"] != "undef":
                print("\n\nWarning: the selected PG model does not support channel selection in function {0}\n\n".format(api["function"]))
            retcode,res=submod.execcmd(api["function"],pg["model_id"],signal["phase"])
        if retcode==0:
            return 0,"Error setting the PG/channel's phase <- %s" % (res)
    # Call the set_sync function for the model
    api = api_pool.get_api(pg["model"],"set_sync_"+pg["model"])
    if api == -1:
        if signal["sync"] != "undef":
            print("\n\nWarning: the selected PG model does not implement function {0} and sync is set\n\n".format("set_sync_"+pg["model"]))
    else:
        if "channel" in api["args"]:
            retcode,res=submod.execcmd(api["function"],pg["model_id"],signal["sync"],signal["channel"])
        else:
            if signal["channel"] != "undef":
                print("\n\nError: the selected PG model does not support channel selection in function {0}\n\n".format(api["function"]))
            retcode,res=submod.execcmd(api["function"],pg["model_id"],signal["sync"])
        if retcode==0:
            return 0,"Error turning on the PG/channel sync <- %s" % (res)
    return 1,"ok"

def power_on_signal(signal_id):
    "Turn on signal *signal_id*"
    try:
        signal = signal_pool.get(signal_id)
    except Exception as e:
        submod.setres(0,"signal: signal_%s" % (str(e)))
        return
    try:
        pg = pg_pool.get(signal["pg_id"])
    except Exception as e:
        submod.setres(0,"signal: pg_%s" % (str(e)))
        return
    # Verify that function and pg have been configured
    if signal["function"] == "undef":
        submod.setres(0,"signal: function is required to power on")
        return
    if signal["pg_id"] == -1:
        submod.setres(0,"signal: a PG is required to power on")
        return
    # Verify that no other signal with the same signal["pg"] and signal["channel"] is powered on
    for s_id,s in signal_pool.get_all():
        if s["pg_id"] == signal["pg_id"] and \
           s["channel"] == signal["channel"] and \
           s_id != int(signal_id) and \
           s["power"]:
            submod.setres(0,"signal: signal {0} using the same PG and channel is already on".format(s_id))
            return
    # Call the power_on function for the model
    api = api_pool.get_api(pg["model"],"power_on_"+pg["model"])
    if api == -1:
        submod.setres(0,"signal: the selected PG model does not implement function {0}".format("power_on_"+pg["model"]))
        return
    if "channel" in api["args"]:
        retcode,res=submod.execcmd(api["function"],pg["model_id"],signal["channel"])
    else:
        if signal["channel"] != "undef":
            print("Warning: the selected PG model does not support channel selection in function {0}".format(api["function"]))
        retcode,res=submod.execcmd(api["function"],pg["model_id"])
    if retcode==0:
        submod.setres(0,"signal: Error turning on the PG/channel <- %s" % (res))
    signal["power"] = 1
    submod.setres(1,"ok")

def power_off_signal(signal_id):
    "Turn off signal *signal_id*"
    try:
        signal = signal_pool.get(signal_id)
    except Exception as e:
        submod.setres(0,"signal: signal_%s" % (str(e)))
        return
    try:
        pg = pg_pool.get(signal["pg_id"])
    except Exception as e:
        submod.setres(0,"signal: pg_%s" % (str(e)))
        return
    # Call the power_off function for the model
    api = api_pool.get_api(pg["model"],"power_off_"+pg["model"])
    if api == -1:
        submod.setres(0,"signal: the selected PG model does not implement function {0}".format("power_off_"+pg["model"]))
        return
    if "channel" in api["args"]:
        retcode,res=submod.execcmd(api["function"],pg["model_id"],signal["channel"])
    elif signal["channel"] != "undef":
        print("Warning: the selected PG model does not support channel selection in function {0}".format(api["function"]))
        retcode,res=submod.execcmd(api["function"],pg["model_id"])  
    else:
        retcode,res=submod.execcmd(api["function"],pg["model_id"])  
    if retcode==0:
        submod.setres(0,"signal: Error turning off the PG/channel <- %s" % (res))
    signal["power"] = 0
    submod.setres(1,"ok")

def get_error_queue_signal(pg_id):
    "Read error queue of PG"
    try:
        pg = pg_pool.get(pg_id)
    except Exception as e:
        submod.setres(0,"signal: pg_%s" % (str(e)))
        return
    # Call the get_error_queue function for the model
    api = api_pool.get_api(pg["model"],"get_error_queue_"+pg["model"])
    if api == -1:
        submod.setres(0,"signal: the selected PG model does not implement function {0}".format("get_error_queue_"+pg["model"]))
        return
    retcode,res=submod.execcmd("get_error_queue_"+pg["model"],pg["model_id"])
    if retcode==0:
        submod.setres(0,"signal: Error getting error queue <- %s" % (res))
    submod.setres(1,res)

