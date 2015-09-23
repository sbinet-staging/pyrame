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

sg_wl350_pool = pools.pool()

# Put serialized API in memory if not called via import
if __name__ == '__main__':
    global api; api = getapi.load_api(__file__)

# Functions
def getapi_sg_wl350():
    submod.setres(1,api)

def init_sg_wl350(conf_string):
    """Initialize SG_WL350 motion controller.
    
    *conf_string* must contain a bus parameter with the conf_string of the GPIB module

    Returns id of SG_WL350, sg_wl350_id"""
    try:
        conf = conf_strings.parse(conf_string)
    except Exception as e:
        submod.setres(0,"sg_wl350: %s"%(str(e)))
        return
    if conf.name!="sg_wl350":
        submod.setres(0,"sg_wl350: Invalid module name %s in conf_string instead of th_apt"%(conf.name))
        return
    if not conf.has("bus"):
        submod.setres(0,"sg_wl350: Error: the required parameter bus in conf_string is not present")
        return
    try:
        conf_bus = conf_strings.parse(conf.params["bus"])
    except Exception as e:
        submod.setres(0,str(e))
        return
    if conf_bus.name!="gpib":
        submod.setres(0,"sg_wl350: Error: only the GPIB bus is accepted")
        return
    # Initialize GPIB link
    retcode,res = submod.execcmd("init_gpib",conf.params["bus"])
    if retcode==0:
        submod.setres(0,"sg_wl350: Error initializing GPIB link <- %s" % (res))
        return
    sg_wl350_id = sg_wl350_pool.new({"bus_id": res})
    submod.setres(1,sg_wl350_id)

def deinit_sg_wl350(sg_wl350_id):
    "Deinitialize and deregister sg_wl350 motion controller from the pool."
    try:
        sg_wl350 = sg_wl350_pool.get(sg_wl350_id)
    except Exception as e:
        submod.setres(1,"sg_wl350: sg_wl350_%s" % (str(e)))
        return
    retcode,res=submod.execcmd("deinit_gpib",sg_wl350["bus_id"])
    if retcode==0:
        submod.setres(0,"sg_wl350: Error deinitializing link <- %s" % (res))
        return
    try:
        sg_wl350_pool.remove(sg_wl350_id)
    except Exception as e:
        submod.setres(0,"sg_wl350: %s"%(str(e)))
        return
    submod.setres(1,"ok")

def config_sg_wl350(sg_wl350_id):
    try:
        sg_wl350 = sg_wl350_pool.get(sg_wl350_id)
    except Exception as e:
        submod.setres(0,"sg_wl350_%s" % (str(e)))
        return
    retcode,res=submod.execcmd("config_gpib",sg_wl350["bus_id"])
    if retcode==0:
        submod.setres(0,"sg_wl350: Error configuring link <- %s" % (res))
        return
    sg_wl350["configured"] = True
    submos.setres(1,"ok")

def inval_sg_wl350(sg_wl350_id):
    try:
        sg_wl350 = sg_wl350_pool.get(sg_wl350_id)
    except Exception as e:
        submod.setres(0,"sg_wl350_%s" % (str(e)))
        return
    if "configured" not in sg_wl350:
        submod.setres(1,"not configured")
        return
    retcode,res=submod.execcmd("inval_gpib",sg_wl350["bus_id"])
    if retcode==0:
        submod.setres(0,"sg_wl350: Error invalidating link <- %s" % (res))
        return
    del sg_wl350["configured"]
    submos.setres(1,"ok")

def execute_command(sg_wl350_id,command):
    try:
        sg_wl350 = sg_wl350_pool.get(sg_wl350_id)
    except Exception as e:
        return 0,str(e)
    if "configured" not in sg_wl350:
        return 0,"not configured"
    retcode,res=submod.execcmd("wrnrd_gpib",sg_wl350["bus_id"],command+r"\n")
    if retcode==0:
        return 0,"Error writing and reading to/from GPIB <- %s" % (res)
    if res=="C":
        return 1,"ok"
    return 0,"Error processing execute command: %s" % (res)

def request_command(sg_wl350_id,command):
    try:
        sg_wl350 = sg_wl350_pool.get(sg_wl350_id)
    except Exception as e:
        return 0,str(e)
    if "configured" not in sg_wl350:
        return 0,"not configured"
    retcode,res=submod.execcmd("wrnrd_gpib",sg_wl350["bus_id"],command+r"\n")
    if retcode==0:
        return 0,"Error writing and reading to/from GPIB <- %s" % (res)
    if res=="#":
        return 0,"Error processing request command: %s" % (res)
    return 1,res

def next_sg_wl350(sg_wl350_id):
    "Go to next position in predefined path"
    command = "NEXT"
    retcode,res = execute_command(sg_wl350_id,command)
    if retcode==0:
        submod.setres(0,"sg_wl350: Error going to next position: %s" % (res))
        return
    submod.setres(1,"ok")

def get_pos(sg_wl350_id,units="um"):
    """Get position"""
    if units=="" or units=="undef":
        return 0,"Valid units are needed"
    if units=="um":
        command = "GETDIE"
    elif units=="colrow":
        command = "GETCR"
    else:
        return 0,"Invalid units"
    retcode,res = request_command(sg_wl350_id,command)
    if retcode==0:
        return 0,"Error getting position: %s" % (res)
    return 1,res

def get_pos_sg_wl350(sg_wl350_id,units="um"):
    """Get position"""
    retcode,res = get_pos(sg_wl350_id,units)
    if retcode==0:
        submod.setres(retcode,"sg_wl350: %s" % (res))
    submod.setres(retcode,res)

def go_first_point_sg_wl350(sg_wl350_id):
    command = "TOFIRSTSITE"
    retcode,res = execute_command(sg_wl350_id,command)
    if retcode==0:
        submod.setres(0,"sg_wl350: Error going to first position: %s" % (res))
        return
    submod.setres(1,"ok")

def is_last_point_sg_wl350(sg_wl350_id):
    command = "GETLASTPOINT"
    retcode,res = request_command(sg_wl350_id,command)
    if retcode==0:
        submod.setres(0,"sg_wl350: Error checking if it's last position: %s" % (res))
        return
    if res.lower()=="yes":
        res="1"
    else:
        res="0"
    submod.setres(1,res)

