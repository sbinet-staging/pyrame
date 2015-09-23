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

def void_test():
    print("void python code")
    submod.setres(1,"void()")

def fail_test():
    submod.setres(0,"fail()")

def cmod_test(dev_name,function,arg1,arg2):
    retcode,res=submod.execcmd(function,dev_name,arg1,arg2)
    if retcode==0:
        submod.setres(retcode,res)
        return
    submod.setres(1,r"hello <%s> \n%s"%(arg1,arg2))

def onearg_test(arg1):
    submod.setres(1,"onearg(%s)"%(arg1))

def twoargs_test(arg1,arg2):
    submod.setres(1,"twoargs(%s,%s)"%(arg1,arg2))

def varmod_test():
    retcode,res=submod.execcmd("setvar_varmod","0","x","2")
    if retcode==0:
        submod.setres(0,"cant setvar: %s"%(res))
    else:
        submod.setres(1,"ok")
    
