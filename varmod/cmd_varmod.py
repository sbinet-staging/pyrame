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

vars={}

def init_varmod(parent_device,dev_name):
    "Initialize varmod by registering itself on cmod as a new device of varmod type"
    retcode,res=submod.execcmd("new_device_cmod","varmod",dev_name,parent_device)
    if retcode==0:
        submod.setres(0,"varmod: cant register in cmod <- %s"%(res))
        return
    submod.setres(1,res)

def setvar_varmod(vid,name,value):
    "Set value on variable *vid*"
    global vars
    vars[name]=value
    submod.setres(1,"ok")

def getvar_varmod(vid,name):
    "Get value of variable *vid*"
    global vars
    if name in vars.keys():
        submod.setres(1,vars[name])
    else:
        submod.setres(0,"varmod: unknown variable")

def intopvar_varmod(vid,name,op,value):
    "Do integer operation *op* with *value* on variable *vid*. *op* can be '+', '-', 'x' or '/'"
    global vars
    if not value.isdigit():
         submod.setres(0,"varmod: value should be numeric")
         return
    if not name in vars.keys():
        vars[name]="0"
    if vars[name].isdigit():
        if op=="+":
            vars[name]=str(int(vars[name])+int(value))
            submod.setres(1,vars[name])
            return
        if op=="-":
            vars[name]=str(int(vars[name])-int(value))
            submod.setres(1,vars[name])
            return
        if op=="x":
            vars[name]=str(int(vars[name])*int(value))
            submod.setres(1,vars[name])
            return
        if op=="/":
            vars[name]=str(int(vars[name])/int(value))
            submod.setres(1,vars[name])
            return
        submod.setres(0,"varmod: unknown operation")
        return
    else:
        submod.setres(0,"varmod: variable is not numeric")
        return


def stropvar_varmod(vid,name,op,value):
    "Do string operation *op* with *value* on variable *vid*. *op* can only be 'c' for concatenation"
    global vars
    if not name in vars.keys():
        vars[name]=""
    if op=="c":
        vars[name]=vars[name]+value
        submod.setres(1,vars[name])
        return
    submod.setres(0,"varmod: unknown operation")

