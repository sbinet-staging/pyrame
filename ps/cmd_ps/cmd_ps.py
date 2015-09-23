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

import conf_strings, pools, getapi, apipools

from time import sleep

# CLASS ##########################################################

class ps_class():
    ps_pool = pools.pool()

    def init(self,conf_string):
        try:
            conf = conf_strings.parse(conf_string)
        except Exception as e:
            return 0,str(e)
        # Initialize PS
        model = conf.name
        retcode,res=submod.execcmd("init_"+model,conf_string)
        if retcode==0:
            return 0,"Error initializing %s power supply <- %s" % (model,res)
        model_id = res
        # Get API of the module and add it to the api_pool, if it's not already there
        if not api_pool.is_present(model):
            retcode,res=submod.execcmd("getapi_"+model)
            if retcode==0:
                return 0,"Can't get API for %s <- %s" % (model,res)
            api_pool.add_api_from_string(model,res)
        ps_id = self.ps_pool.new({"model": model, "model_id": model_id})
        return 1,ps_id

    def deinit(self,ps_id):
        try:
            ps = self.ps_pool.get(ps_id)
        except Exception as e:
            return 0,str(e)
        # Call the deinitializer function for the model
        retcode,res=submod.execcmd("deinit_"+ps["model"],ps["model_id"])
        if retcode==0:
            return 0,"Error deinitializing %s power supply <- %s" % (ps["model"],res)
        # Remove ps from the pool
        try:
            self.ps_pool.remove(ps_id)
        except Exception as e:
            return 0,str(e)
        return retcode,res

    def config(self,ps_id,error_check="normal"):
        try:
            ps = self.ps_pool.get(ps_id)
        except Exception as e:
            return 0,str(e)
        # Call the configuration function for the model
        retcode,res=submod.execcmd("config_"+ps["model"],ps["model_id"],error_check)
        if retcode==0:
            return 0,"Error configuring %s power supply <- %s" % (ps["model"],res)
        return retcode,res

    def inval(self,ps_id):
        try:
            ps = self.ps_pool.get(ps_id)
        except Exception as e:
            return 0,str(e)
        # Call the invalidation function for the model
        retcode,res=submod.execcmd("inval_"+ps["model"],ps["model_id"])
        if retcode==0:
            return 0,"Error invalidating %s power supply <- %s" % (ps["model"],res)
        return retcode,res

    def relay(self,ps_id,function,channel,*params):
        try:
            ps = self.ps_pool.get(ps_id)
        except Exception as e:
            return 0,str(e)
        # Call the set_voltage_limit function for the model
        api = api_pool.get_api(ps["model"],function+"_"+ps["model"])
        if api == -1:
            return 0,"The selected PS model does not implement this function"
        if "channel" in api["args"]:
            params += (channel,)
        else:
            if channel not in ["undef",""]:
                print("\n\nWarning: The selected PS model does not support channel selection in this function\n\n")
        retcode,res=submod.execcmd(function+"_"+ps["model"],ps["model_id"],*params)
        if retcode==0:
            return 0,"Error in %s <- %s" % (function+"_"+ps["model"],res)
        return 1,res

    def reset(self,ps_id):
        return self.relay(ps_id,"reset","undef")

    def set_voltage(self,ps_id,voltage,channel="undef",slew_rate="undef"):
        try:
            ps = self.ps_pool.get(ps_id)
        except Exception as e:
            return 0,str(e)
        # Check capabilities
        api = api_pool.get_api(ps["model"],"set_voltage_"+ps["model"])
        if api == -1:
            return 0,"The selected PS model does not implement this function"
        if "channel" in api["args"]:
            channel = [channel]
        else:
            if channel!="undef" and channel!="":
                print("\n\nWarning: The selected PS model does not support channel selection in this function\n\n")
            channel = []
        # Call the set_voltage function for the model
        if "slew_rate" in api["args"]:
            retcode,res=submod.execcmd("set_voltage_"+ps["model"],ps["model_id"],voltage,*(channel+[slew_rate]))
            if retcode==0:
                return 0,"Error setting voltage <- %s" % (res)
        elif slew_rate!="undef" and slew_rate!="" and voltage!="undef" and voltage!="":
            api = api_pool.get_api(ps["model"],"get_voltage_"+ps["model"])
            if api == -1:
                return 0,"The selected PS model does not implement the required get_voltage function for ramps."
            retcode,res=submod.execcmd("get_voltage_"+ps["model"],ps["model_id"],*channel)
            if retcode==0:
                return 0,"Error getting voltage <- %s" % (res)
            v_i = float(res)
            voltage = float(voltage)
            slew_rate = float(slew_rate)
            steps = int(round((v_i - voltage)/slew_rate))
            if steps == 0: steps = 1
            for t in reversed(range(0,steps,steps/abs(steps))):
                sleep(1)
                v = str(voltage + t*slew_rate)
                retcode,res=submod.execcmd("set_voltage_"+ps["model"],ps["model_id"],v,*channel)
                if retcode==0:
                    return 0,"Error setting voltage <- %s" % (res)
        else:
            retcode,res=submod.execcmd("set_voltage_"+ps["model"],ps["model_id"],voltage,*channel)
            if retcode==0:
                return 0,"Error setting voltage <- %s" % (res)
        return retcode,res

    def set_current(self,ps_id,current,channel="undef"):
        return self.relay(ps_id,"set_current",channel,current)

    def set_voltage_limit(self,ps_id,voltage_limit,channel="undef"):
        return self.relay(ps_id,"set_voltage_limit",channel,voltage_limit)

    def set_current_limit(self,ps_id,current_limit,channel="undef"):
        return self.relay(ps_id,"set_current_limit",channel,current_limit)

    def get_voltage(self,ps_id,channel="undef"):
        return self.relay(ps_id,"get_voltage",channel)

    def get_current(self,ps_id,channel="undef"):
        return self.relay(ps_id,"get_current",channel)

    def power_on(self,ps_id,channel="undef"):
        return self.relay(ps_id,"power_on",channel)

    def power_off(self,ps_id,channel="undef"):
        return self.relay(ps_id,"power_off",channel)

    def free_command(self,ps_id):
        return self.relay(ps_id,"free_command","undef")

    def get_error_queue(self,ps_id):
        return self.relay(ps_id,"get_error_queue","undef")

# CREATE POOL ####################################################

me = ps_class()
api_pool = apipools.api_pool()

# COMMANDS #######################################################

# Put serialized API in memory if not called via import
if __name__=='__main__':
    global api; api = getapi.load_api(__file__)

# Functions
def getapi_ps():
    submod.setres(1,api)

def init_ps(conf_string):
    """Registers in the pool and initializes a new PS. *conf_string* is the configuration string for the module to be initialized.

    Returns its ps_id."""
    retcode,res = me.init(conf_string)
    if retcode==0:
        submod.setres(retcode,"ps: %s" % (res))
        return
    submod.setres(retcode,res)

def deinit_ps(ps_id):
    "Deregister a PS from the pool"
    retcode,res = me.deinit(ps_id)
    if retcode==0:
        submod.setres(retcode,"ps: %s" % (res))
        return
    submod.setres(retcode,res)

def config_ps(ps_id,error_check="normal"):
    "Configure the PS"
    retcode,res = me.config(ps_id,error_check)
    if retcode==0:
        submod.setres(retcode,"ps: %s" % (res))
        return
    submod.setres(retcode,res)

def inval_ps(ps_id):
    "Invalidate configuration of PS"
    retcode,res = me.inval(ps_id)
    if retcode==0:
        submod.setres(retcode,"ps: %s" % (res))
        return
    submod.setres(retcode,res)


def reset_ps(ps_id):
    "Reset PS"
    retcode,res = me.reset(ps_id)
    if retcode==0:
        submod.setres(retcode,"ps: %s" % (res))
        return
    submod.setres(retcode,res)

def set_voltage_ps(ps_id,voltage,channel="undef",slew_rate="undef"):
    "Set voltage in Volts. Optional channel argument for multi-channel PS and slew_rate argument in V/s for PS modules that support it."
    retcode,res = me.set_voltage(ps_id,voltage,channel,slew_rate)
    if retcode==0:
        submod.setres(retcode,"ps: %s" % (res))
        return
    submod.setres(retcode,res)

def set_current_ps(ps_id,current,channel="undef"):
    "Set current in Ampers. Optional channel argument for multi-channel PS"
    retcode,res = me.set_current(ps_id,current,channel)
    if retcode==0:
        submod.setres(retcode,"ps: %s" % (res))
        return
    submod.setres(retcode,res)

def set_voltage_limit_ps(ps_id,voltage_limit,channel="undef"):
    "Set voltage limit in Volts. Optional channel argument for multi-channel PS"
    retcode,res = me.set_voltage_limit(ps_id,voltage_limit,channel)
    if retcode==0:
        submod.setres(retcode,"ps: %s" % (res))
        return
    submod.setres(retcode,res)

def set_current_limit_ps(ps_id,current_limit,channel="undef"):
    "Set current limit in Ampers. Optional channel argument for multi-channel PS"
    retcode,res = me.set_current_limit(ps_id,current_limit,channel)
    if retcode==0:
        submod.setres(retcode,"ps: %s" % (res))
        return
    submod.setres(retcode,res)

def get_voltage_ps(ps_id,channel="undef"):
    "Get voltage in Volts. Optional channel argument for multi-channel PS."
    retcode,res = me.get_voltage(ps_id,channel)
    if retcode==0:
        submod.setres(retcode,"ps: %s" % (res))
        return
    submod.setres(retcode,res)

def get_current_ps(ps_id,channel="undef"):
    "Get current in Ampers. Optional channel argument for multi-channel PS."
    retcode,res = me.get_current(ps_id,channel)
    if retcode==0:
        submod.setres(retcode,"ps: %s" % (res))
        return
    submod.setres(retcode,res)

def set_rise_delay_ps(ps_id,rise_delay,channel):
    "Set power-on (rise) delay in seconds."
    retcode,res = me.set_rise_delay(ps_id,channel)
    if retcode==0:
        submod.setres(retcode,"ps: %s" % (res))
        return
    submod.setres(retcode,res)

def power_on_ps(ps_id,channel="undef"):
    "Turn on PS"
    retcode,res = me.power_on(ps_id,channel)
    if retcode==0:
        submod.setres(retcode,"ps: %s" % (res))
        return
    submod.setres(retcode,res)

def power_off_ps(ps_id,channel="undef"):
    "Turn off PS"
    retcode,res = me.power_off(ps_id,channel)
    if retcode==0:
        submod.setres(retcode,"ps: %s" % (res))
        return
    submod.setres(retcode,res)

def free_command_ps(ps_id,command):
    "Send free command PS"
    retcode,res = me.free_command_ps(ps_id)
    if retcode==0:
        submod.setres(retcode,"ps: %s" % (res))
        return
    submod.setres(retcode,res)

def get_error_queue_ps(ps_id):
    "Read error queue"
    retcode,res = me.get_error_queue(ps_id)
    if retcode==0:
        submod.setres(retcode,"ps: %s" % (res))
        return
    submod.setres(retcode,res)
