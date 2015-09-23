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

from time import sleep

# LS_421 #########################################################

class ls_421(object):
    def __init__(self):
        self.ls_421_pool = pools.pool()

    class ls_421_Exception(Exception):
        pass

    def init(self,conf_string):
        try:
            conf = conf_strings.parse(conf_string)
        except Exception as e:
            return 0,str(e)
        if conf.name!="ls_421":
            return 0,"Invalid module name %s in conf_string instead of ls_421"%(conf.name)
        if not conf.has("bus"):
            return 0,"Error: some of the required parameters (bus) in conf_string are not present"
        try:
            conf_bus = conf_strings.parse(conf.params["bus"])
        except Exception as e:
            return 0,str(e)
        if conf_bus.name=="serial" and not conf_bus.has("baudrate"):
            conf_bus.params["baudrate"]="9600"
        conf_bus.params["parity"]="O"
        conf_bus.params["bytesize"]="7"
        retcode,res = submod.execcmd("init_"+conf_bus.name,conf_strings.unparse(conf_bus))
        if retcode==0:
            return 0,"Error initializing link <- %s" % (res)
        ls_421_id = self.ls_421_pool.new({"bus": conf_bus.name, "bus_id": res})
        return 1,ls_421_id

    def deinit(self,ls_421_id):
        try:
            ls_421 = self.ls_421_pool.get(ls_421_id)
        except Exception as e:
            return 1,"ls_421_%s" % (str(e))
        retcode,res = submod.execcmd("deinit_"+ls_421["bus"],ls_421["bus_id"])
        if retcode==0:
            return 0,"Error deinitializing link <- %s" % (res)
        self.ls_421_pool.remove(ls_421_id)
        return 1,"ok"

    def config(self,ls_421_id,Bunits,Bmode,Bfilter):
        try:
            ls_421 = self.ls_421_pool.get(ls_421_id)
        except Exception as e:
            return 0,"ls_421_%s" % (str(e))
        if "configured" in ls_421:
            return 1,"already configured"
        retcode,res = submod.execcmd("config_"+ls_421["bus"],ls_421["bus_id"])
        if retcode==0:
            return 0,"Error configuring link <- %s" % (res)
        try:
            if Bunits not in ["G","T"]:
                raise self.ls_421_Exception((0,"invalid units. must be G or T"))
            if Bmode not in ["1","0"]:
                raise self.ls_421_Exception((0,"invalid AC/DC mode. must be 1 or 0"))
            if Bfilter not in ["1","0"]:
                raise self.ls_421_Exception((0,"invalid filter state. must be 1 or 0"))
            cmd = "UNIT %s;ACDC %s;FILT %s;AUTO 1"%(Bunits,Bmode,Bfilter)
            retcode,res = submod.execcmd("write_"+ls_421["bus"],ls_421["bus_id"],cmd+r"\r\n")
            if retcode==0:
                raise self.ls_421_Exception((0,"Error configuring <- %s" % (res)))
            sleep(0.5)
        except self.ls_421_Exception as e:
            _,_ = submod.execcmd("inval_"+ls_421["bus"],ls_421["bus_id"])
            return e[0]
        ls_421["range"] = "auto"
        ls_421["configured"] = True
        return 1,"ok"

    def inval(self,ls_421_id):
        try:
            ls_421 = self.ls_421_pool.get(ls_421_id)
        except Exception as e:
            return 0,"ls_421_%s" % (str(e))
        if not "configured" in ls_421:
            return 1,"not configured"
        # Invalidate bus
        retcode,res = submod.execcmd("inval_"+ls_421["bus"],ls_421["bus_id"])
        if retcode==0:
            return 0,"Error invalidating link <- %s" % (res)
        # Remove parameters set during config
        del ls_421["range"]
        del ls_421["configured"]
        return 1,"ok"

    def reset(self,ls_421_id):
        try:
            ls_421 = self.ls_421_pool.get(ls_421_id)
        except Exception as e:
            return 0,"ls_421_%s" % (str(e))
        if not "configured" in ls_421:
            return 0,"not configured"
        retcode,res = submod.execcmd("write_"+ls_421["bus"],ls_421["bus_id"],r"*RST\r\n")
        if retcode==0:
            return 0,"Error resetting <- %s" % (res)
        return 1,"ok"

    def measure(self,ls_421_id,Brange):
        try:
            ls_421 = self.ls_421_pool.get(ls_421_id)
        except Exception as e:
            return 0,"ls_421_%s" % (str(e))
        if not "configured" in ls_421:
            return 0,"not configured"
        if Brange not in ["auto","0","1","2","3"]:
            return 0,"invalid range"
        if ls_421["range"]!=Brange:
            if Brange=="auto":
                cmd = "AUTO 1"
            else:
                cmd = "AUTO 0;RANGE %s"%(Brange)
            retcode,res = submod.execcmd("write_"+ls_421["bus"],ls_421["bus_id"],cmd+r"\r\n")
            if retcode==0:
                return 0,"Error setting range <- %s" % (res)
            sleep(1)
            ls_421["range"] = Brange
        cmd = "FIELD?"
        retcode,res = submod.execcmd("wrnrd_until_"+ls_421["bus"],ls_421["bus_id"],cmd+r"\r\n",r"\n")
        if retcode==0:
            return 0,"Error reading field <- %s" % (res)
        field = res.strip()
        cmd = "FIELDM?"
        retcode,res = submod.execcmd("wrnrd_until_"+ls_421["bus"],ls_421["bus_id"],cmd+r"\r\n",r"\n")
        if retcode==0:
            return 0,"Error reading field multiplier <- %s" % (res)
        res = res.strip()
        if res=="u":
            multiplier = 1e-6
        elif res=="m":
            multiplier = 1e-3
        elif res=="":
            multiplier = 1
        elif res=="k":
            multiplier = 1e3
        else:
            return 0,"Invalid field multiplier: %s"%(res)
        if field!="OL":
            field = float(field)*multiplier
        return 1,str(field)

# CREATE LS_421 POOL #############################################

me = ls_421()

# COMMANDS #######################################################

# Put serialized API in memory if not called via import
if __name__ == '__main__':
    global api; api = getapi.load_api(__file__)

def getapi_ls_421():
    submod.setres(1,api)

def init_ls_421(conf_string):
    """Initialize LS_421 gaussmeter.
    
    conf_string must contain the parameters:

    - bus: a conf_string for cmd_serial or cmd_tcp

    Returns id of LS_421, ls_421_id"""
    retcode,res = me.init(conf_string)
    if retcode==0:
        submod.setres(retcode,"ls_421: %s" % (res))
        return
    submod.setres(retcode,res) 
    
def deinit_ls_421(ls_421_id):
    "Deinitialize *ls_421_id* gaussmeter."
    retcode,res = me.deinit(ls_421_id)
    if retcode==0:
        submod.setres(retcode,"ls_421: %s" % (res))
        return
    submod.setres(retcode,res)

def config_ls_421(ls_421_id,Bunits,Bmode,Bfilter):
    "Configure *ls_421_id* gaussmeter. *Bunits* can be G (Gauss) or T (Tesla), *Bmode* can be 1 (AC) or 0 (DC), *Bfilter* can be 0 (OFF) or 1 (ON)."
    retcode,res = me.config(ls_421_id,Bunits,Bmode,Bfilter)
    if retcode==0:
        submod.setres(retcode,"ls_421: %s" % (res))
        return
    submod.setres(retcode,res)

def inval_ls_421(ls_421_id):
    "Invalidate *ls_421_id* gaussmeter."
    retcode,res = me.inval(ls_421_id)
    if retcode==0:
        submod.setres(retcode,"ls_421: %s" % (res))
        return
    submod.setres(retcode,res)

def reset_ls_421(ls_421_id):
    "Reset *ls_421_id* gaussmeter (send \*RST command)"
    retcode,res = me.reset(ls_421_id)
    if retcode==0:
        submod.setres(retcode,"ls_421: %s" % (res))
        return
    submod.setres(retcode,res)

def measure_ls_421(ls_421_id,Brange):
    "Take a measure from *ls_421_id* gaussmeter using range *Brange* (0 to 3; 0 for the highest, 3 for the lowest)"
    retcode,res = me.measure(ls_421_id,Brange)
    if retcode==0:
        submod.setres(retcode,"ls_421: %s" % (res))
        return
    submod.setres(retcode,res)

