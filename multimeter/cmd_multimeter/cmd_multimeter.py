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

# CLASS ##########################################################

class multimeter_class():
    multimeter_pool = pools.pool("multimeter")

    def init(self,conf_string):
        try:
            conf = conf_strings.parse(conf_string)
        except Exception as e:
            return 0,str(e)
        # Initialize MULTIMETER
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
        multimeter_id = self.multimeter_pool.new({"model":model,"model_id":model_id})
        return 1,multimeter_id

    def deinit(self,multimeter_id):
        try:
            multimeter = self.multimeter_pool.get(multimeter_id)
        except Exception as e:
            return 0,str(e)
        # Call the deinitializer function for the model
        retcode,res=submod.execcmd("deinit_"+multimeter["model"],multimeter["model_id"])
        if retcode==0:
            return 0,"Error deinitializing %s power supply <- %s" % (multimeter["model"],res)
        # Remove multimeter from the pool
        try:
            self.multimeter_pool.remove(multimeter_id)
        except Exception as e:
            return 0,str(e)
        return retcode,res

    def config(self,multimeter_id,error_check="normal"):
        try:
            multimeter = self.multimeter_pool.get(multimeter_id)
        except Exception as e:
            return 0,str(e)
        # Call the configuration function for the model
        retcode,res=submod.execcmd("config_"+multimeter["model"],multimeter["model_id"],error_check)
        if retcode==0:
            return 0,"Error configuring %s power supply <- %s" % (multimeter["model"],res)
        return retcode,res

    def inval(self,multimeter_id):
        try:
            multimeter = self.multimeter_pool.get(multimeter_id)
        except Exception as e:
            return 0,str(e)
        # Call the invalidation function for the model
        retcode,res=submod.execcmd("inval_"+multimeter["model"],multimeter["model_id"])
        if retcode==0:
            return 0,"Error invalidating %s power supply <- %s" % (multimeter["model"],res)
        return retcode,res

    def relay(self,multimeter_id,function,range,resolution,channel,*params):
        try:
            multimeter = self.multimeter_pool.get(multimeter_id)
        except Exception as e:
            return 0,str(e)
        # Call the set_voltage_limit function for the model
        api = api_pool.get_api(multimeter["model"],function+"_"+multimeter["model"])
        if api == -1:
            return 0,"The selected MULTIMETER model does not implement this function"
        #range
        if "range" in api["args"]:
            params += (range,)
        else:
            if range not in ["undef",""]:
                print("\n\nWarning: The selected MULTIMETER model does not support range selection in this function\n\n")
        #resolution
        if "resolution" in api["args"]:
            params += (resolution,)
        else:
            if resolution not in ["undef",""]:
                print("\n\nWarning: The selected MULTIMETER model does not support resolution selection in this function\n\n")
        #channel
        if "channel" in api["args"]:
            params += (channel,)
        else:
            if channel not in ["undef",""]:
                print("\n\nWarning: The selected MULTIMETER model does not support channel selection in this function\n\n")
        retcode,res=submod.execcmd(function+"_"+multimeter["model"],multimeter["model_id"],*params)
        if retcode==0:
            return 0,"Error in %s <- %s" % (function+"_"+multimeter["model"],res)
        return 1,res

    def reset(self,multimeter_id):
        return self.relay(multimeter_id,"reset","undef","undef","undef")

    def get_dc_voltage(self,multimeter_id,range="undef",resolution="undef",channel="undef"):
        return self.relay(multimeter_id,"get_dc_voltage",range,resolution,channel)

    def get_ac_voltage(self,multimeter_id,range="undef",resolution="undef",channel="undef"):
        return self.relay(multimeter_id,"get_ac_voltage",range,resolution,channel)

    def get_dc_current(self,multimeter_id,range="undef",resolution="undef",channel="undef"):
        return self.relay(multimeter_id,"get_dc_current",range,resolution,channel)

    def get_ac_current(self,multimeter_id,range="undef",resolution="undef",channel="undef"):
        return self.relay(multimeter_id,"get_ac_current",range,resolution,channel)

    def get_2w_resistance(self,multimeter_id,range="undef",resolution="undef",channel="undef"):
        return self.relay(multimeter_id,"get_2w_resistance",range,resolution,channel)

    def get_4w_resistance(self,multimeter_id,range="undef",resolution="undef",channel="undef"):
        return self.relay(multimeter_id,"get_4w_resistance",range,resolution,channel)

    def get_frequency(self,multimeter_id,range="undef",resolution="undef",channel="undef"):
        return self.relay(multimeter_id,"get_frequence",range,resolution,channel)

    def get_period(self,multimeter_id,range="undef",resolution="undef",channel="undef"):
        return self.relay(multimeter_id,"get_period",range,resolution,channel)

    def free_command(self,multimeter_id):
        return self.relay(multimeter_id,"free_command","undef","undef","undef")

    def get_error_queue(self,multimeter_id):
        return self.relay(multimeter_id,"get_error_queue","undef","undef","undef")

# CREATE POOL ####################################################

me = multimeter_class()
api_pool = apipools.api_pool()

# COMMANDS #######################################################

# Put serialized API in memory if not called via import
if __name__=='__main__':
    global api; api = getapi.load_api(__file__)

# Functions
def getapi_multimeter():
    submod.setres(1,api)

def init_multimeter(conf_string):
    """Registers in the pool and initializes a new MULTIMETER. *conf_string* is the configuration string for the module to be initialized.

    Returns its multimeter_id."""
    retcode,res = me.init(conf_string)
    if retcode==0:
        submod.setres(retcode,"multimeter: %s" % (res))
        return
    submod.setres(retcode,res)

def deinit_multimeter(multimeter_id):
    "Deregister a MULTIMETER from the pool"
    retcode,res = me.deinit(multimeter_id)
    if retcode==0:
        submod.setres(retcode,"multimeter: %s" % (res))
        return
    submod.setres(retcode,res)

def config_multimeter(multimeter_id,error_check="normal"):
    "Configure the MULTIMETER"
    retcode,res = me.config(multimeter_id,error_check)
    if retcode==0:
        submod.setres(retcode,"multimeter: %s" % (res))
        return
    submod.setres(retcode,res)

def inval_multimeter(multimeter_id):
    "Invalidate configuration of MULTIMETER"
    retcode,res = me.inval(multimeter_id)
    if retcode==0:
        submod.setres(retcode,"multimeter: %s" % (res))
        return
    submod.setres(retcode,res)


def reset_multimeter(multimeter_id):
    "Reset MULTIMETER"
    retcode,res = me.reset(multimeter_id)
    if retcode==0:
        submod.setres(retcode,"multimeter: %s" % (res))
        return
    submod.setres(retcode,res)

def get_dc_voltage_multimeter(multimeter_id,range="undef",resolution="undef",channel="undef"):
    "Get DC voltage in Volts. Optional *channel* argument for multi-channel MULTIMETER. Optional *range* argument for scale of measurement. Optional *resolution* argument for either integration time or allowable error. See documentation of the particular model for allowed values."
    retcode,res = me.get_dc_voltage(multimeter_id,range,resolution,channel)
    if retcode==0:
        submod.setres(retcode,"multimeter: %s" % (res))
        return
    submod.setres(retcode,res)

def get_ac_voltage_multimeter(multimeter_id,range="undef",resolution="undef",channel="undef"):
    "Get AC voltage in Volts. Optional *channel* argument for multi-channel MULTIMETER. Optional *range* argument for scale of measurement. Optional *resolution* argument for either integration time or allowable error. See documentation of the particular model for allowed values."
    retcode,res = me.get_ac_voltage(multimeter_id,range,resolution,channel)
    if retcode==0:
        submod.setres(retcode,"multimeter: %s" % (res))
        return
    submod.setres(retcode,res)

def get_dc_current_multimeter(multimeter_id,range="undef",resolution="undef",channel="undef"):
    "Get DC current in Ampers. Optional *channel* argument for multi-channel MULTIMETER. Optional *range* argument for scale of measurement. Optional *resolution* argument for either integration time or allowable error. See documentation of the particular model for allowed values."
    retcode,res = me.get_dc_current(multimeter_id,range,resolution,channel)
    if retcode==0:
        submod.setres(retcode,"multimeter: %s" % (res))
        return
    submod.setres(retcode,res)

def get_ac_current_multimeter(multimeter_id,range="undef",resolution="undef",channel="undef"):
    "Get AC current in Ampers. Optional *channel* argument for multi-channel MULTIMETER. Optional *range* argument for scale of measurement. Optional *resolution* argument for either integration time or allowable error. See documentation of the particular model for allowed values."
    retcode,res = me.get_ac_current(multimeter_id,range,resolution,channel)
    if retcode==0:
        submod.setres(retcode,"multimeter: %s" % (res))
        return
    submod.setres(retcode,res)

def get_2w_resistance_multimeter(multimeter_id,range="undef",resolution="undef",channel="undef"):
    "Get 2-wire resitance in Ohms. Optional *channel* argument for multi-channel MULTIMETER. Optional *range* argument for scale of measurement. Optional *resolution* argument for either integration time or allowable error. See documentation of the particular model for allowed values."
    retcode,res = me.get_2w_resistance(multimeter_id,range,resolution,channel)
    if retcode==0:
        submod.setres(retcode,"multimeter: %s" % (res))
        return
    submod.setres(retcode,res)

def get_4w_resistance_multimeter(multimeter_id,range="undef",resolution="undef",channel="undef"):
    "Get 4-wire resitance in Ohms. Optional *channel* argument for multi-channel MULTIMETER. Optional *range* argument for scale of measurement. Optional *resolution* argument for either integration time or allowable error. See documentation of the particular model for allowed values."
    retcode,res = me.get_4w_resistance(multimeter_id,range,resolution,channel)
    if retcode==0:
        submod.setres(retcode,"multimeter: %s" % (res))
        return
    submod.setres(retcode,res)

def get_frequency_multimeter(multimeter_id,range="undef",resolution="undef",channel="undef"):
    "Get frequency in Hertzs. Optional *channel* argument for multi-channel MULTIMETER. Optional *range* argument for scale of measurement. Optional *resolution* argument for either integration time or allowable error. See documentation of the particular model for allowed values."
    retcode,res = me.get_frequency(multimeter_id,range,resolution,channel)
    if retcode==0:
        submod.setres(retcode,"multimeter: %s" % (res))
        return
    submod.setres(retcode,res)

def get_period_multimeter(multimeter_id,range="undef",resolution="undef",channel="undef"):
    "Get period in seconds. Optional *channel* argument for multi-channel MULTIMETER. Optional *range* argument for scale of measurement. Optional *resolution* argument for either integration time or allowable error. See documentation of the particular model for allowed values."
    retcode,res = me.get_period(multimeter_id,range,resolution,channel)
    if retcode==0:
        submod.setres(retcode,"multimeter: %s" % (res))
        return
    submod.setres(retcode,res)

def free_command_multimeter(multimeter_id,command):
    "Send free command MULTIMETER"
    retcode,res = me.free_command_multimeter(multimeter_id)
    if retcode==0:
        submod.setres(retcode,"multimeter: %s" % (res))
        return
    submod.setres(retcode,res)

def get_error_queue_multimeter(multimeter_id):
    "Read error queue"
    retcode,res = me.get_error_queue(multimeter_id)
    if retcode==0:
        submod.setres(retcode,"multimeter: %s" % (res))
        return
    submod.setres(retcode,res)
