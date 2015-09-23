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

import time
import getapi,pools,conf_strings

nw_esp301_pool = pools.pool()

# Axes
axes = ["1","2","3"]

# Ports
ports = ["A","B"]

# COMMANDS #######################################################

# Put serialized API in memory if not called via import
if __name__=='__main__':
    global api; api = getapi.load_api(__file__)

def getapi_nw_esp301():
    submod.setres(1,api)

def init_nw_esp301(conf_string):
    """Initialize NW_ESP301 motion controller.
    
    *conf_string* must contain:

    - bus: conf_string of the underlying link module
    - chan: 1, 2 or 3 for the channel of the axis

    Returns id of NW_ESP301, nw_esp301_id"""
    try:
        conf = conf_strings.parse(conf_string)
    except Exception as e:
        submod.setres(0,"nw_esp301: %s" % str(e))
        return
    if conf.name!="nw_esp301":
        submod.setres(0,"nw_esp301: Invalid module name %s in conf_string instead of nw_esp301"%(conf.name))
        return
    if not conf.has("bus","chan"):
        submod.setres(0,"nw_esp301: Some of the required parameters (bus and chan) in conf_string are not present")
        return
    if conf.params["chan"] not in axes:
        submod.setres(0,"nw_esp301: invalid channel")
        return
    try:
        conf_bus = conf_strings.parse(conf.params["bus"])
    except Exception as e:
        return 0,str(e)
    if conf_bus.name=="serial" and not conf_bus.has("baudrate"):
        conf_bus.params["baudrate"]="115200"
    retcode,res = submod.execcmd("init_"+conf_bus.name,conf_strings.unparse(conf_bus))
    if retcode==0:
        submod.setres(0,"nw_esp301: error initializing axis <- %s"%(res))
        return
    nw_esp301_id = nw_esp301_pool.new({"bus":conf_bus.name,"bus_id":res,"chan":conf.params["chan"]})
    submod.setres(1,nw_esp301_id)

def deinit_nw_esp301(nw_esp301_id):
    "Deinitialize and deregister nw_esp301 motion controller from the pool."
    try:
        nw_esp301 = nw_esp301_pool.get(nw_esp301_id)
    except Exception as e:
        submod.setres(1,"nw_esp301: nw_esp301_%s"%(str(e)))
        return
    retcode,res = submod.execcmd("deinit_"+nw_esp301["bus"],nw_esp301["bus_id"])
    if retcode==0:
        submod.setres(0,"nw_esp301: Error deinitializing link <- %s" % (res))
        return
    nw_esp301_pool.remove(nw_esp301_id)
    submod.setres(1,"ok")

def config_nw_esp301(nw_esp301_id,pos_max,pos_min):
    "Configure *nw_esp301_id* axis. *pos_max* and *pos_min* define the limits of excursion."
    try:
        nw_esp301 = nw_esp301_pool.get(nw_esp301_id)
    except Exception as e:
        submod.setres(0,"nw_esp301: nw_esp301_%s"%(str(e)))
        return
    pos_min = float(pos_min)
    pos_max = float(pos_max)
    if pos_max<=pos_min:
        submod.setres(0,"nw_esp301: max must be higher than min")
        return
    if pos_max<0 or pos_min<0:
        submod.setres(0,"nw_esp301: neither max nor min can be negative")
        return
    retcode,res = submod.execcmd("config_"+nw_esp301["bus"],nw_esp301["bus_id"])
    if retcode==0:
        submod.setres(0,"nw_esp301: Error configuring link <- %s" % (res))
        return
    command = r"{0}MO\r".format(nw_esp301["chan"])
    retcode,res = submod.execcmd("write_"+nw_esp301["bus"],nw_esp301["bus_id"],command)
    if retcode==0:
        submod.setres(0,"nw_esp301: Error writing to link <- %s" % (res))
        return
    nw_esp301["max"]=pos_max
    nw_esp301["min"]=pos_min
    submod.setres(1,"ok")

def inval_nw_esp301(nw_esp301_id):
    "Invalidate *nw_esp301_id* configuration"
    try:
        nw_esp301 = nw_esp301_pool.get(nw_esp301_id)
    except Exception as e:
        submod.setres(0,"nw_esp301: nw_esp301_%s"%(str(e)))
        return
    command = r"{0}MF\r".format(nw_esp301["chan"])
    retcode,res = submod.execcmd("write_"+nw_esp301["bus"],nw_esp301["bus_id"],command)
    if retcode==0:
        submod.setres(0,"nw_esp301: Error writing to link <- %s" % (res))
        return
    retcode,res = submod.execcmd("inval_"+nw_esp301["bus"],nw_esp301["bus_id"])
    if retcode==0:
        submod.setres(0,"nw_esp301: Error invalidating link <- %s" % (res))
        return
    del nw_esp301["max"]
    del nw_esp301["min"]
    submod.setres(1,"ok")

def command(nw_esp301,command):
    retcode,res = submod.execcmd("wrnrd_until_"+nw_esp301["bus"],nw_esp301["bus_id"],command,r"\r")
    if retcode==0:
        return 0,"Error writing and reading to/from link <- %s" % (res)
    elif res!="1":
        return 0,"Error monitoring move completion status <- %s" % (res)
    retcode,errors = get_error_queue(nw_esp301)
    if errors!="": 
        return 0,"Error(s) returned from the MC: %s" % (errors)
    return 1,"ok"

def reset_nw_esp301(nw_esp301_id,direction,velocity):
    "Reset axis *nw_esp301_id* by homing on *direction* at *velocity*."
    try:
        nw_esp301 = nw_esp301_pool.get(nw_esp301_id)
    except Exception as e:
        submod.setres(0,"nw_esp301: nw_esp301_%s"%(str(e)))
        return
    if "max" not in nw_esp301:
        submod.setres(0,"nw_esp301: not configured")
        return
    # Send command to nw_esp301
    command = r"{0}OH{1};{0}OL0.1;{0}OR;{0}WS;" \
              r"{0}PR0.2;{0}WS;{0}DH;" \
              r"{0}MD\r".format(nw_esp301["chan"],velocity)
    retcode,res = command(nw_esp301,command)
    if retcode==0:
        submod.setres(0,"nw_esp301: Error resetting axis: %s"%(res))
        return
    submod.setres(1,"ok")

def reset_controller_nw_esp301(nw_esp301_id):
    "Reset the controller of *nw_esp301_id*, not just the axis"
    try:
        nw_esp301 = nw_esp301_pool.get(nw_esp301_id)
    except Exception as e:
        submod.setres(0,"nw_esp301: nw_esp301_%s"%(str(e)))
        return
    if "max" not in nw_esp301:
        submod.setres(0,"nw_esp301: not configured")
        return
    command = r"RS\r"
    retcode,res = submod.execcmd("write_"+nw_esp301["bus"],nw_esp301["bus_id"],command)
    if retcode==0:
        submod.setres(0,"nw_esp301: Error resetting nw_esp301 <- %s" % (res))
        return
    time.sleep(12)
    retcode,errors = get_error_queue(nw_esp301)
    if errors!="":
        submod.setres(0,"nw_esp301: Error(s) returned from the MC <- %s" % (errors))
        return
    submod.setres(1,"ok")

def go_min_nw_esp301(nw_esp301_id,velocity,acceleration):
    "Go to the minimum position as defined during the initalization of the axis"
    try:
        nw_esp301 = nw_esp301_pool.get(nw_esp301_id)
    except Exception as e:
        submod.setres(0,"nw_esp301: nw_esp301_%s"%(str(e)))
        return
    if "max" not in nw_esp301:
        submod.setres(0,"nw_esp301: not configured")
        return
    # Send command to nw_esp301
    command = r"{0}MO;" \
              r"{0}AC{1:f};" \
              r"{0}VA{2:f};" \
              r"{0}PA{3:f};{0}WS;" \
              r"{0}MD\r".format(nw_esp301["chan"],acceleration,velocity,nw_esp301["min"])
    retcode,res = command(nw_esp301,command)
    if retcode==0:
        submod.setres(0,"nw_esp301: Error moving to min: %s"%(res))
        return
    submod.setres(1,"ok")

def go_max_nw_esp301(nw_esp301_id,velocity,acceleration):
    "Go to the maximum position as defined during the initalization of the axis"
    try:
        nw_esp301 = nw_esp301_pool.get(nw_esp301_id)
    except Exception as e:
        submod.setres(0,"nw_esp301: nw_esp301_%s"%(str(e)))
        return
    if "max" not in nw_esp301:
        submod.setres(0,"nw_esp301: not configured")
        return
    # Send command to nw_esp301
    command = r"{0}MO;" \
              r"{0}AC{1:f};" \
              r"{0}VA{2:f};" \
              r"{0}PA{3:f};{0}WS;" \
              r"{0}MD\r".format(nw_esp301["chan"],acceleration,velocity,nw_esp301["max"])
    retcode,res = command(nw_esp301,command)
    if retcode==0:
        submod.setres(0,"nw_esp301: Error moving to max: %s"%(res))
        return
    submod.setres(1,"ok")

def move_nw_esp301(nw_esp301_id,displacement,velocity,acceleration):
    "Move by displacement units with the specified maximum velocity"
    try:
        nw_esp301 = nw_esp301_pool.get(nw_esp301_id)
    except Exception as e:
        submod.setres(0,"nw_esp301: nw_esp301_%s"%(str(e)))
        return
    if "max" not in nw_esp301:
        submod.setres(0,"nw_esp301: not configured")
        return
    # Send command to nw_esp301
    displacement = float(displacement)
    velocity = float(velocity)
    retcode,res = get_pos(nw_esp301)
    if retcode==0:
        submod.setres(0,"nw_esp301: %s"%(res))
        return
    if float(res)+displacement > nw_esp301["max"] or float(res)+displacement < nw_esp301["min"]:
        submod.setres(0,"nw_esp301: Refusing to move: final position {0:f} would be out of the axis limits".format(float(res)+displacement))
        return
    command = r"{0}MO;" \
              r"{0}AC{1:f};" \
              r"{0}VA{2:f};" \
              r"{0}PR{3:f};{0}WS;" \
              r"{0}MD\r".format(nw_esp301["chan"],acceleration,velocity,displacement)
    retcode,res = command(nw_esp301,command)
    if retcode==0:
        submod.setres(0,"nw_esp301: Error moving: %s"%(res))
        return
    submod.setres(1,"ok")

def get_pos_nw_esp301(nw_esp301_id):
    "Get position of the specified axis"
    try:
        nw_esp301 = nw_esp301_pool.get(nw_esp301_id)
    except Exception as e:
        submod.setres(0,"nw_esp301: nw_esp301_%s"%(str(e)))
        return
    if "max" not in nw_esp301:
        submod.setres(0,"nw_esp301: not configured")
        return
    # Send command to nw_esp301
    retcode,res = get_pos(nw_esp301)
    if retcode==0:
        submod.setres(retcode,"nw_esp301: %s" % (res))
        return
    submod.setres(1,res)

def get_pos(nw_esp301):
    "Get position of the specified axis"
    command = r"{0}TP\r".format(nw_esp301["chan"])
    retcode,res = submod.execcmd("wrnrd_until_"+nw_esp301["bus"],nw_esp301["bus_id"],command,r"\r")
    if retcode==0:
        return 0,"Error writing and reading to/from link <- %s" % (res)
    retcode,errors = get_error_queue(nw_esp301)
    if errors!="": 
        return 0,"Error(s) returned from the MC: %s" % (errors)
    return 1,str(float(res))

def get_error_queue_nw_esp301(nw_esp301_id):
    "Read error queue until the end (code 0)"
    try:
        nw_esp301 = nw_esp301_pool.get(nw_esp301_id)
    except Exception as e:
        submod.setres(0,"nw_esp301: nw_esp301_%s"%(str(e)))
        return
    if "max" not in nw_esp301:
        submod.setres(0,"nw_esp301: not configured")
        return
    retcode,res=get_error_queue(nw_esp301)
    if retcode==0:
        submod.setres(retcode,"nw_esp301: %s" % (res))
        return
    submod.setres(1,res)
        
def get_error_queue(nw_esp301):
    "Read error queue until the end (code 0)"
    command = r"TB\r"
    errors = "" 
    while True:  
        retcode,res=submod.execcmd("wrnrd_until_"+nw_esp301["bus"],nw_esp301["bus_id"],command,r"\r")
        if retcode==0:
            return 0,res
        elif int(res.split(",",1)[0])!=0: 
            errors += res if errors=="" else "; "+res
        else:   
            break
    return 1,errors
