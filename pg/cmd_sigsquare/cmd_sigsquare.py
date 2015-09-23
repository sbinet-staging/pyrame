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

sigsquare_pool = pools.pool()

# Put serialized API in memory if not called via import
if __name__ == '__main__':
    global api; api = getapi.load_api(__file__)

# Functions
def getapi_sigsquare():
    submod.setres(1,api)

def init_sigsquare(dev_name,parent_device,conf_string,channel):
    #init the pg
    retcode,res=submod.execcmd("init_pg_signal",conf_string)
    if retcode==0:
        submod.setres(0,"sigsquare: Can't init pg <- %s"%(res))
        return
    pg_id = res
    #register in the config module
    retcode,res=submod.execcmd("new_device_cmod","sigsquare",dev_name,parent_device)
    if retcode==0:
        _,_=submod.execcmd("deinit_pg_signal",pg_id)
        submod.setres(0,"sigsquare: Can't register in cmod <- %s"%(res))
        return
    sigsquare_id = res
    retcode,res=submod.execcmd("set_param_cmod",sigsquare_id,"sigsquare_conf_string",conf_string)
    if retcode==0:
        _,_=submod.execcmd("deinit_pg_signal",pg_id)
        submod.setres(0,"sigsquare: Can't register in cmod <- %s"%(res))
        return
    retcode,res=submod.execcmd("set_param_cmod",sigsquare_id,"sigsquare_channel",channel)
    if retcode==0:
        _,_=submod.execcmd("deinit_pg_signal",pg_id)
        submod.setres(0,"sigsquare: Can't register in cmod <- %s"%(res))
        return
    #register the new id 
    sigsquare_id = sigsquare_pool.new({"pg_id": pg_id, "channel": channel},id=sigsquare_id)
    submod.setres(1,sigsquare_id)

def deinit_sigsquare(sigsquare_id):
    try:
        sigsquare = sigsquare_pool.get(sigsquare_id)
    except Exception as e:
        submod.setres(1,"sigsquare: sigsquare_%s" % (str(e)))
        return
    #deinit the pg
    retcode,res=submod.execcmd("deinit_pg_signal",sigsquare["pg_id"])
    if retcode==0:
        submod.setres(0,"sigsquare: Can't deinit pg <- %s"%(res))
        return
    sigsquare_pool.remove(sigsquare_id)
    submod.setres(1,"ok")

def config_sigsquare(sigsquare_id,hl,ll,freq,dc,phase):
    try:
        sigsquare = sigsquare_pool.get(sigsquare_id)
    except Exception as e:
        submod.setres(1,"sigsquare: sigsquare_%s" % (str(e)))
        return
    #init the signal
    retcode,res=submod.execcmd("init_signal")
    if retcode==0:
        submod.setres(0,"sigsquare: Can't init signal <- %s"%(res))
        return
    sigsquare["signal_id"] = res
    #bind the signal and the pg
    retcode,res=submod.execcmd("set_pg_signal",sigsquare["signal_id"],sigsquare["pg_id"],sigsquare["channel"])
    if retcode==0:
        _,_=submod.execcmd("deinit_signal",sigsquare["signal_id"])
        submod.setres(0,"sigsquare: Can't bind pg <- %s"%(res))
        return
    #config the pg
    retcode,res=submod.execcmd("config_pg_signal",sigsquare["pg_id"])
    if retcode==0:
        _,_=submod.execcmd("deinit_signal",sigsquare["signal_id"])
        submod.setres(0,"sigsquare: Can't config pg <- %s"%(res))
        return
    #set function
    retcode,res=submod.execcmd("set_function_signal",sigsquare["signal_id"],"pulse")
    if retcode==0:
        _,_=submod.execcmd("inval_pg_signal",sigsquare["pg_id"])
        _,_=submod.execcmd("deinit_signal",sigsquare["signal_id"])
        submod.setres(0,"sigsquare: Can't set function <- %s"%(res))
        return
    #set frequency
    retcode,res=set_frequency(sigsquare_id,freq)
    if retcode==0:
        _,_=submod.execcmd("inval_pg_signal",sigsquare["pg_id"])
        _,_=submod.execcmd("deinit_signal",sigsquare["signal_id"])
        submod.setres(0,"sigsquare: Can't set freq: %s"%(res))
        return
    #set shape
    retcode,res=set_shape(sigsquare_id,hl,ll,dc,phase)
    if retcode==0:
        _,_=submod.execcmd("inval_pg_signal",sigsquare["pg_id"])
        _,_=submod.execcmd("deinit_signal",sigsquare["signal_id"])
        submod.setres(0,"sigsquare: Can't set shape: %s"%(res))
        return 
    #set frequency REPEATED IN PURPOSE
    retcode,res=set_frequency(sigsquare_id,freq)
    if retcode==0:
        _,_=submod.execcmd("inval_pg_signal",sigsquare["pg_id"])
        _,_=submod.execcmd("deinit_signal",sigsquare["signal_id"])
        submod.setres(0,"sigsquare: Can't set freq: %s"%(res))
        return
    submod.setres(1,"ok")

def inval_sigsquare(sigsquare_id):
    try:
        sigsquare = sigsquare_pool.get(sigsquare_id)
    except Exception as e:
        submod.setres(1,"sigsquare: sigsquare_%s" % (str(e)))
        return
    retcode,res=submod.execcmd("inval_pg_signal",sigsquare["pg_id"])
    if retcode==0:
        submod.setres(0,"sigsquare: Can't invalidate PG <- %s"%(res))
        return
    retcode,res=submod.execcmd("deinit_signal",sigsquare["signal_id"])
    if retcode==0:
        submod.setres(0,"sigsquare: Can't deinit signal <- %s"%(res))
        return
    del sigsquare["signal_id"]
    submod.setres(1,"ok")

def set_shape(sigsquare_id,hl,ll,dc,phase):
    try:
        sigsquare = sigsquare_pool.get(sigsquare_id)
    except Exception as e:
        submod.setres(1,"sigsquare: sigsquare_%s" % (str(e)))
        return

    retcode,res=submod.execcmd("set_high_level_signal",sigsquare["signal_id"],hl)
    if retcode==0:
        return 0,"Can't set high level <- %s"%(res)
    retcode,res=submod.execcmd("set_param_cmod",sigsquare_id,"sigsquare_hl",hl)
    if retcode==0:
        return 0,"sigsquare: Can't register in cmod <- %s"%(res)

    retcode,res=submod.execcmd("set_low_level_signal",sigsquare["signal_id"],ll)
    if retcode==0:
        return 0,"Can't set low level <- %s"%(res)
    retcode,res=submod.execcmd("set_param_cmod",sigsquare_id,"sigsquare_ll",ll)
    if retcode==0:
        return 0,"sigsquare: Can't register in cmod <- %s"%(res)

    retcode,res=submod.execcmd("set_duty_cycle_signal",sigsquare["signal_id"],dc)
    if retcode==0:
        return 0,"Can't set duty cycle <- %s"%(res)
    retcode,res=submod.execcmd("set_param_cmod",sigsquare_id,"sigsquare_dc",dc)
    if retcode==0:
        return 0,"sigsquare: Can't register in cmod <- %s"%(res)

    retcode,res=submod.execcmd("set_phase_signal",sigsquare["signal_id"],phase)
    if retcode==0:
        return 0,"Can't set phase <- %s"%(res)
    retcode,res=submod.execcmd("set_param_cmod",sigsquare_id,"sigsquare_phase",phase)
    if retcode==0:
        return 0,"sigsquare: Can't register in cmod <- %s"%(res)

    return 1,"ok"

def set_shape_sigsquare(sigsquare_id,hl,ll,dc,phase):
    retcode,res=set_shape(sigsquare_id,hl,ll,dc,phase)
    if retcode==0:
        submod.setres(0,"sigsquare: %s" % (res))
        return
    submod.setres(retcode,res)

def set_frequency(sigsquare_id,freq):
    try:
        sigsquare = sigsquare_pool.get(sigsquare_id)
    except Exception as e:
        submod.setres(1,"sigsquare: sigsquare_%s" % (str(e)))
        return
    retcode,res=submod.execcmd("set_frequency_signal",sigsquare["signal_id"],freq)
    if retcode==0:
        return 0,"Can't set sp freq <- %s"%(res)
    retcode,res=submod.execcmd("set_param_cmod",sigsquare_id,"sigsquare_freq",freq)
    if retcode==0:
        submod.setres(0,"sigsquare: Can't register in cmod <- %s"%(res))
        return
    return 1,"ok"

def set_frequency_sigsquare(sigsquare_id,freq):
    retcode,res=set_frequency(sigsquare_id,freq)
    if retcode==0:
        submod.setres(0,"sigsquare: %s" % (res))
        return
    submod.setres(retcode,res)

def output_on_sigsquare(sigsquare_id):
    try:
        sigsquare = sigsquare_pool.get(sigsquare_id)
    except Exception as e:
        submod.setres(1,"sigsquare: sigsquare_%s" % (str(e)))
        return
    retcode,res=submod.execcmd("power_on_signal",sigsquare["signal_id"])
    if retcode==0:
        submod.setres(0,"sigsquare: %s" % (res))
        return
    submod.setres(retcode,res)
    
def output_off_sigsquare(sigsquare_id):
    try:
        sigsquare = sigsquare_pool.get(sigsquare_id)
    except Exception as e:
        submod.setres(1,"sigsquare: sigsquare_%s" % (str(e)))
        return
    retcode,res=submod.execcmd("power_off_signal",sigsquare["signal_id"])
    if retcode==0:
        submod.setres(0,"sigsquare: %s" % (res))
        return
    submod.setres(retcode,res)
