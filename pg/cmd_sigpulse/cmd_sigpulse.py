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

import pools, getapi

sigpulse_pool = pools.pool()

# Put serialized API in memory if not called via import
if __name__ == '__main__':
    global api; api = getapi.load_api(__file__)

# Functions
def getapi_sigpulse():
    submod.setres(1,api)

def init_sigpulse(dev_name,parent_device,conf_string,channel):
    #init the pg
    retcode,res=submod.execcmd("init_pg_signal",conf_string)
    if retcode==0:
        submod.setres(0,"sigpulse: Can't init pg <- %s"%(res))
        return
    pg_id = res
    #register in the config module
    retcode,res=submod.execcmd("new_device_cmod","sigpulse",dev_name,parent_device)
    if retcode==0:
        _,_=submod.execcmd("deinit_pg_signal",pg_id)
        submod.setres(0,"sigpulse: Can't register in cmod <- %s"%(res))
        return
    sigpulse_id = res
    retcode,res=submod.execcmd("set_param_cmod",sigpulse_id,"sigpulse_conf_string",conf_string)
    if retcode==0:
        _,_=submod.execcmd("deinit_pg_signal",pg_id)
        submod.setres(0,"sigpulse: Can't register in cmod <- %s"%(res))
        return
    retcode,res=submod.execcmd("set_param_cmod",sigpulse_id,"sigpulse_channel",channel)
    if retcode==0:
        _,_=submod.execcmd("deinit_pg_signal",pg_id)
        submod.setres(0,"sigpulse: Can't register in cmod <- %s"%(res))
        return
    #register the new id 
    sigpulse_id = sigpulse_pool.new({"pg_id": pg_id, "channel": channel},id=sigpulse_id)
    submod.setres(1,sigpulse_id)

def deinit_sigpulse(sigpulse_id):
    try:
        sigpulse = sigpulse_pool.get(sigpulse_id)
    except Exception as e:
        submod.setres(1,"sigpulse: sigpulse_%s" % (str(e)))
        return
    #deinit the pg
    retcode,res=submod.execcmd("deinit_pg_signal",sigpulse["pg_id"])
    if retcode==0:
        submod.setres(0,"sigpulse: Can't deinit pg <- %s"%(res))
        return
    sigpulse_pool.remove(sigpulse_id)
    submod.setres(1,"ok")

def config_sigpulse(sigpulse_id,hl,ll,freq,pw,re,fe,phase):
    try:
        sigpulse = sigpulse_pool.get(sigpulse_id)
    except Exception as e:
        submod.setres(1,"sigpulse: sigpulse_%s" % (str(e)))
        return
    #init the signal
    retcode,res=submod.execcmd("init_signal")
    if retcode==0:
        submod.setres(0,"sigpulse: Can't init signal <- %s"%(res))
        return
    sigpulse["signal_id"] = res
    #bind the signal and the pg
    retcode,res=submod.execcmd("set_pg_signal",sigpulse["signal_id"],sigpulse["pg_id"],sigpulse["channel"])
    if retcode==0:
        _,_=submod.execcmd("deinit_signal",sigpulse["signal_id"])
        submod.setres(0,"sigpulse: Can't bind pg <- %s"%(res))
        return
    #config the pg
    retcode,res=submod.execcmd("config_pg_signal",sigpulse["pg_id"])
    if retcode==0:
        _,_=submod.execcmd("deinit_signal",sigpulse["signal_id"])
        submod.setres(0,"sigpulse: Can't config pg <- %s"%(res))
        return
    #set function
    retcode,res=submod.execcmd("set_function_signal",sigpulse["signal_id"],"pulse")
    if retcode==0:
        _,_=submod.execcmd("inval_pg_signal",sigpulse["pg_id"])
        _,_=submod.execcmd("deinit_signal",sigpulse["signal_id"])
        submod.setres(0,"sigpulse: Can't set function <- %s"%(res))
        return
    #set frequency
    retcode,res=set_frequency(sigpulse_id,freq)
    if retcode==0:
        _,_=submod.execcmd("inval_pg_signal",sigpulse["pg_id"])
        _,_=submod.execcmd("deinit_signal",sigpulse["signal_id"])
        submod.setres(0,"sigpulse: Can't set freq: %s"%(res))
        return
    #set shape
    retcode,res=set_shape(sigpulse_id,hl,ll,pw,re,fe,phase)
    if retcode==0:
        _,_=submod.execcmd("inval_pg_signal",sigpulse["pg_id"])
        _,_=submod.execcmd("deinit_signal",sigpulse["signal_id"])
        submod.setres(0,"sigpulse: Can't set shape: %s"%(res))
        return 
    #set frequency REPEATED IN PURPOSE
    retcode,res=set_frequency(sigpulse_id,freq)
    if retcode==0:
        _,_=submod.execcmd("inval_pg_signal",sigpulse["pg_id"])
        _,_=submod.execcmd("deinit_signal",sigpulse["signal_id"])
        submod.setres(0,"sigpulse: Can't set freq: %s"%(res))
        return
    submod.setres(1,"ok")

def inval_sigpulse(sigpulse_id):
    try:
        sigpulse = sigpulse_pool.get(sigpulse_id)
    except Exception as e:
        submod.setres(1,"sigpulse: sigpulse_%s" % (str(e)))
        return
    retcode,res=submod.execcmd("inval_pg_signal",sigpulse["pg_id"])
    if retcode==0:
        submod.setres(0,"sigpulse: Can't invalidate PG <- %s"%(res))
        return
    retcode,res=submod.execcmd("deinit_signal",sigpulse["signal_id"])
    if retcode==0:
        submod.setres(0,"sigpulse: Can't deinit signal <- %s"%(res))
        return
    del sigpulse["signal_id"]
    submod.setres(1,"ok")

def set_shape(sigpulse_id,hl,ll,pw,re,fe,phase):
    try:
        sigpulse = sigpulse_pool.get(sigpulse_id)
    except Exception as e:
        submod.setres(1,"sigpulse: sigpulse_%s" % (str(e)))
        return

    retcode,res=submod.execcmd("set_high_level_signal",sigpulse["signal_id"],hl)
    if retcode==0:
        return 0,"Can't set high level <- %s"%(res)
    retcode,res=submod.execcmd("set_param_cmod",sigpulse_id,"sigpulse_hl",hl)
    if retcode==0:
        return 0,"sigpulse: Can't register in cmod <- %s"%(res)

    retcode,res=submod.execcmd("set_low_level_signal",sigpulse["signal_id"],ll)
    if retcode==0:
        return 0,"Can't set low level <- %s"%(res)
    retcode,res=submod.execcmd("set_param_cmod",sigpulse_id,"sigpulse_ll",ll)
    if retcode==0:
        return 0,"sigpulse: Can't register in cmod <- %s"%(res)

    retcode,res=submod.execcmd("set_pulse_width_signal",sigpulse["signal_id"],pw)
    if retcode==0:
        return 0,"Can't set pulse width <- %s"%(res)
    retcode,res=submod.execcmd("set_param_cmod",sigpulse_id,"sigpulse_pw",pw)
    if retcode==0:
        return 0,"sigpulse: Can't register in cmod <- %s"%(res)

    retcode,res=submod.execcmd("set_edges_signal",sigpulse["signal_id"],re,fe)
    if retcode==0:
        return 0,"Can't set edges <- %s"%(res)
    retcode,res=submod.execcmd("set_param_cmod",sigpulse_id,"sigpulse_re",re)
    if retcode==0:
        return 0,"sigpulse: Can't register in cmod <- %s"%(res)
    retcode,res=submod.execcmd("set_param_cmod",sigpulse_id,"sigpulse_fe",fe)
    if retcode==0:
        return 0,"sigpulse: Can't register in cmod <- %s"%(res)

    retcode,res=submod.execcmd("set_phase_signal",sigpulse["signal_id"],phase)
    if retcode==0:
        return 0,"Can't set phase <- %s"%(res)
    retcode,res=submod.execcmd("set_param_cmod",sigpulse_id,"sigpulse_phase",phase)
    if retcode==0:
        return 0,"sigpulse: Can't register in cmod <- %s"%(res)

    return 1,"ok"

def set_shape_sigpulse(sigpulse_id,hl,ll,pw,re,fe,phase):
    retcode,res=set_shape(sigpulse_id,hl,ll,pw,re,fe,phase)
    if retcode==0:
        submod.setres(0,"sigpulse: %s" % (res))
        return
    submod.setres(retcode,res)

def set_frequency(sigpulse_id,freq):
    try:
        sigpulse = sigpulse_pool.get(sigpulse_id)
    except Exception as e:
        submod.setres(1,"sigpulse: sigpulse_%s" % (str(e)))
        return
    retcode,res=submod.execcmd("set_frequency_signal",sigpulse["signal_id"],freq)
    if retcode==0:
        return 0,"Can't set sp freq <- %s"%(res)
    retcode,res=submod.execcmd("set_param_cmod",sigpulse_id,"sigpulse_freq",freq)
    if retcode==0:
        submod.setres(0,"sigpulse: Can't register in cmod <- %s"%(res))
        return
    return 1,"ok"

def set_frequency_sigpulse(sigpulse_id,freq):
    retcode,res=set_frequency(sigpulse_id,freq)
    if retcode==0:
        submod.setres(0,"sigpulse: %s" % (res))
    submod.setres(retcode,res)

def output_on_sigpulse(sigpulse_id):
    try:
        sigpulse = sigpulse_pool.get(sigpulse_id)
    except Exception as e:
        submod.setres(1,"sigpulse: sigpulse_%s" % (str(e)))
        return
    retcode,res=submod.execcmd("power_on_signal",sigpulse["signal_id"])
    if retcode==0:
        submod.setres(0,"sigpulse: %s" % (res))
        return
    submod.setres(retcode,res)
    
def output_off_sigpulse(sigpulse_id):
    try:
        sigpulse = sigpulse_pool.get(sigpulse_id)
    except Exception as e:
        submod.setres(1,"sigpulse: sigpulse_%s" % (str(e)))
        return
    retcode,res=submod.execcmd("power_off_signal",sigpulse["signal_id"])
    if retcode==0:
        submod.setres(0,"sigpulse: %s" % (res))
        return
    submod.setres(retcode,res)
