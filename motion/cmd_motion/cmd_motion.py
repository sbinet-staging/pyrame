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

import conf_strings, pools, getapi

motion_pool=pools.pool()

def check_param(param,valid_list,default_param,map_func,unique=True):
    if param=="undef" or param=="":
        param = default_param
    if len(param)!=len(default_param) or any(c not in valid_list for c in param):
        return 0,"invalid param"
    result = map(map_func,param)
    if unique and len(set(result))!=len(result):
        return 0,"repeated characters"
    return 1,result

def init_motion(cs1,cs2,cs3):
    "Initialize motion system. Provide the conf_strings for its three axis *csn* (for axis number n: 1,2,3)"
    motion = {}
    cs = [cs1,cs2,cs3]
    for i in [1,2,3]:
        try:
            conf = conf_strings.parse(cs[i-1])
        except Exception as e:
            submod.setres(0,"motion: %s" % str(e))
            return
        retcode,res = submod.execcmd("init_"+conf.name,cs[i-1])
        if retcode==0:
            submod.setres(0,"motion: error initializing axis %d <- %s"%(i,res))
            return
        motion["id_%d"%(i)] = res
        motion["model_%d"%(i)] = conf.name
    motion_id = motion_pool.new(motion)
    submod.setres(1,motion_id)

def deinit_motion(motion_id):
    "Deinitialize motion system"
    try:
        motion = motion_pool.get(motion_id)
    except Exception as e:
        submod.setres(1,"motion: motion_%s"%(str(e)))
        return
    for i in [1,2,3]:
        retcode,res = submod.execcmd("deinit_"+motion["model_%d"%(i)],motion["id_%d"%(i)])
        if retcode==0:
            submod.setres(0,"motion: error deinitializing axis %d <- %s"%(i,res))
            return
    motion_pool.remove(motion_id)
    submod.setres(1,"ok")

def config_motion(motion_id,max1,min1,max2,min2,max3,min3,d1,d2,d3):
    "Configure the motion system to use the maximum and minimum values *maxn* and *minn* (for axis number n: 1,2,3). Each axis can be inverted with respect to its normal direction by setting *dn* to either 's' (straight) or 'i' (inverted)"
    try:
        motion = motion_pool.get(motion_id)
    except Exception as e:
        submod.setres(0,"motion: motion_%s"%(str(e)))
        return
    maxs = map(float,[max1,max2,max3])
    mins = map(float,[min1,min2,min3])
    d = [d1,d2,d3]
    for i in [0,1,2]:
        if maxs[i]<mins[i]:
            submod.setres(0,"motion: max must be greater than min (axis %d)"%(i+1))
            return
        if d[i] not in ["s","i"]:
            submod.setres(0,"motion: direction must be either s (straight) or i (inverted) (axis %d)"%(i+1))
            return
        d[i] = 1 if d[i]=="s" else -1

    for i in [1,2,3]:
        retcode,res = submod.execcmd("config_"+motion["model_%d"%(i)],motion["id_%d"%(i)],str(maxs[i-1]),str(mins[i-1]))
        if retcode==0:
            submod.setres(0,"motion: error configuring axis %d <- %s"%(i,res))
            return
    motion["maxs"] = maxs
    motion["mins"] = mins
    motion["d"] = d
    motion["o"] = [0,0,0]
    submod.setres(1,"ok")

def inval_motion(motion_id):
    "Invalidate motion system"
    try:
        motion = motion_pool.get(motion_id)
    except Exception as e:
        submod.setres(0,"motion: motion_%s"%(str(e)))
        return
    if "o" not in motion:
        submod.setres(1,"not configured")
        return
    for i in [1,2,3]:
        retcode,res = submod.execcmd("inval_"+motion["model_%d"%(i)],motion["id_%d"%(i)])
        if retcode==0:
            submod.setres(0,"motion: error invalidating axis %d <- %s"%(i,res))
            return
    del motion["maxs"]
    del motion["mins"]
    del motion["d"]
    submod.setres(1,"ok")

def reset_motion(motion_id,d1,d2,d3,s1,s2,s3,order="123"):
    "Reset motion system. Provide direction (*d*), speed (*s*) and *order* of reset"
    try:
        motion = motion_pool.get(motion_id)
    except Exception as e:
        submod.setres(0,"motion: motion_%s"%(str(e)))
        return
    if "o" not in motion:
        submod.setres(0,"not configured")
        return
    retcode,order = check_param(order,["1","2","3"],"123",int)
    if retcode==0:
        submod.setres(0,"motion: %s" % (order));
        return
    s = [s1,s2,s3]
    d = [d1,d2,d3]
    for i in order:
        retcode,res = submod.execcmd("reset_"+motion["model_%d"%(i)],motion["id_%d"%(i)],d[i-1],s[i-1])
        if retcode==0:
            submod.setres(0,"motion: error resetting axis %d <- %s"%(i,res))
            return
    submod.setres(1,"ok")

def is_reset_motion(motion_id):
    "Get the reset status of the system. Returns 1 if all axis are reset, 0 otherwise."
    try:
        motion = motion_pool.get(motion_id)
    except Exception as e:
        submod.setres(0,"motion: motion_%s"%(str(e)))
        return
    if "o" not in motion:
        submod.setres(0,"not configured")
        return
    is_reset = []
    for i in [1,2,3]:
        retcode,res = submod.execcmd("is_reset_"+motion["model_%d"%(i)],motion["id_%d"%(i)])
        if retcode==0:
            submod.setres(0,"motion: error checking reset state of axis %d <- %s"%(i,res))
            return
        is_reset.append(int(res)) 
    submod.setres(1,str(int(all(is_reset))))

def move(motion,d,s,a,strategy="undef"):
    retcode,order = check_param(strategy,["1","2","3"],"123",int)
    if retcode==0:
        return 0,"invalid strategy: %s" % (order)
    # check if we are trying to go to a forbidden point
    if d[0]>motion["maxs"][0] or d[0]<motion["mins"][0] or \
       d[1]>motion["maxs"][1] or d[1]<motion["mins"][1] or \
       d[2]>motion["maxs"][2] or d[2]<motion["mins"][2]:
        return 0,"destination out of limits"
    # get current position
    retcode,c = get_pos(motion,real=True)
    for k in order:
        d_rel = d[k-1] - c[k-1]
        if d_rel!=0:
            retcode,res = submod.execcmd("move_"+motion["model_%d"%(k)],motion["id_%d"%(k)],str(d_rel),s[k-1],a[k-1])
            if retcode==0:
                return 0,"error moving axis %d <- %s"%(k,res)
    return 1,"ok"

def set_origin_motion(motion_id,o1,o2,o3):
    "Set a local coordinate origin other than the default 0,0,0"
    try:
        motion = motion_pool.get(motion_id)
    except Exception as e:
        return 0,"motion: motion_%s"%(str(e))
    if "o" not in motion:
        submod.setres(0,"not configured")
        return
    motion["o"] = map(float,[o1,o2,o3])
    submod.setres(1,"ok")

def move_motion(motion_id,d1,d2,d3,s1,s2,s3,a1,a2,a3,strategy="undef",real="undef"):
    "Move to absolute position *dn* with speed *sn* and acceleration *an*(for axis number n: 1,2,3). Optional parameters: *strategy* can be the order of movement of the axis (e.g.: 231); *real* determines whether local (0, default) or real (1) coordinates are used."
    try:
        motion = motion_pool.get(motion_id)
    except Exception as e:
        return 0,"motion: motion_%s"%(str(e))
    if "o" not in motion:
        submod.setres(0,"not configured")
        return
    d = map(float,[d1,d2,d3])
    s = [s1,s2,s3]
    a = [a1,a2,a3]
    if real!="1":
        # convert from local to real coordinates
        for i in [0,1,2]:
            d[i] = motion["d"][i]*d[i] + motion["o"][i]
    retcode,res = move(motion,d,s,a,strategy)
    if retcode==0:
        submod.setres(0,"motion: %s" % (res))
        return
    submod.setres(1,"ok")

def get_pos(motion,real=False):
    pos = []
    for i in [1,2,3]:
        retcode,res = submod.execcmd("get_pos_"+motion["model_%d"%(i)],motion["id_%d"%(i)])
        if retcode==0:
            return 0,"cant get axis %s position <- %s"%(i,res)
        if real:
            p = float(res)
        else:
            p = (float(res)-motion["o"][i-1])*motion["d"][i-1]
        pos.append(p)
    return 1,pos

def get_pos_motion(motion_id,real="undef"):
    "Get the position of the system. Returns three comma-separated values. *real* determines whether local (0, default) or real (1) coordinates are used."
    try:
        motion = motion_pool.get(motion_id)
    except Exception as e:
        return 0,"motion_%s"%(str(e))
    if "o" not in motion:
        submod.setres(0,"not configured")
        return
    retcode,res = get_pos(motion,True if real=="1" else False)
    if retcode==0:
        submod.setres(0,"motion: %s" % (res))
        return
    submod.setres(1,",".join(map(str,res)))

def get_limits_motion(motion_id,real="undef"):
    "Get the limits of the motion system. *real* determines whether local (0, default) or real (1) coordinates are used. Returns max_1,max_2,max_3;min_1,min_2,min3"
    try:
        motion = motion_pool.get(motion_id)
    except Exception as e:
        return 0,"motion_%s"%(str(e))
    if "o" not in motion:
        submod.setres(0,"not configured")
        return
    if real=="1":
        maxs = motion["maxs"]
        mins = motion["mins"]
    else:
        maxs = [None]*3
        mins = [None]*3
        for i in [0,1,2]:
            if motion["d"][i]==1:
                maxs[i] = (motion["maxs"][i] - motion["o"][i])*motion["d"][i]
                mins[i] = (motion["mins"][i] - motion["o"][i])*motion["d"][i]
            else:
                mins[i] = (motion["maxs"][i] - motion["o"][i])*motion["d"][i]
                maxs[i] = (motion["mins"][i] - motion["o"][i])*motion["d"][i]
    submod.setres(1,",".join(map(str,maxs))+";"+",".join(map(str,mins)))
