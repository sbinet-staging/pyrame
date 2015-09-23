#!/nsr/bin/env python2
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

import pools, conf_strings, getapi

# CLASS ##########################################################

class gpib_class():
    def __init__(self):
        self.gpib_pool = pools.pool()

    def init(self,conf_string):
        # Extract parameters from conf_string
        try:
            conf = conf_strings.parse(conf_string)
        except Exception as e:
            return 0,str(e)
        if conf.name!="gpib":
            return 0,"Invalid module name in conf_string"
        if not conf.has("bus","dst_addr"):
            return 0,"bus and dst_addr needed in conf_string"
        bus_cs = conf.params["bus"]
        try:
            bus_conf = conf_strings.parse(bus_cs)
        except Exception as e:
            return 0,str(e)
        if bus_conf.name=="tcp" and not bus_conf.has("port"):
            bus_conf.params["port"] = 1234
        elif bus_conf.name=="serial" and not bus_conf.has("device") and not bus_conf.has("vendor","product"):
            bus_conf.params["vendor"] = "0403"
            bus_conf.params["product"] = "6001"
        try:
            conf.params["bus"] = conf_strings.unparse(bus_conf)
        except Exception as e:
            return 0,str(e)
        dst_addr = conf.params["dst_addr"]
        adapter_addr = "0"
        if conf.has("adapter_addr"):
            adapter_addr = conf.params["adapter_addr"]
        # Validate parameters
        if dst_addr=="" or dst_addr=="undef" or int(dst_addr) not in range(0,30):
            return 0,"Invalid dst_addr %s" % (dst_addr)
        if adapter_addr=="" or adapter_addr=="undef" or int(adapter_addr) not in range(0,30):
            return 0,"Invalid adapter_addr %s" % (adapter_addr)
        # Initialize bus
        retcode,res = submod.execcmd("init_"+bus_conf.name,conf.params["bus"])
        if retcode==0:
            return 0,"Error initializing bus <- %s" % (res)
        bus_id = res
        # Add to the pool
        gpib_id = self.gpib_pool.new({"bus_type": bus_conf.name, "bus_id": bus_id, "dst_addr": dst_addr, "adapter_addr": adapter_addr})
        return 1,gpib_id

    def deinit(self,gpib_id):
        try:
            gpib = self.gpib_pool.get(gpib_id)
        except Exception as e:
            return 1,"gpib_" % (str(e))
        retcode,res = submod.execcmd("deinit_"+gpib["bus_type"],gpib["bus_id"])
        if retcode==0:
            return 0,"Error attempting to deinitialize bus <- %s" % (res)
        try:
            self.gpib_pool.remove(gpib_id)
        except Exception as e:
            return 0,str(e)
        return 1,"ok"

    def config(self,gpib_id):
        try:
            gpib = self.gpib_pool.get(gpib_id)
        except Exception as e:
            return 0,"gpib_" % (str(e))
        if "bus_canon" in gpib:
            return 1,"already configured"
        retcode,res = submod.execcmd("config_"+gpib["bus_type"],gpib["bus_id"])
        if retcode==0:
            return 0,"Error attempting to configure bus <- %s" % (res)
        bus_canon = res
        # If a GPIB connection with the same bus is already in the pool,
        # check that there's no inconsistent configuration attempt
        found = False
        for _,b in self.gpib_pool.get_all():
            if "bus_canon" in b and (b["bus_canon"]==bus_canon):
                found = True
                break
        if found:
            if b["adapter_addr"]!=gpib["adapter_addr"]:
                submod.execcmd("inval_"+gpib["bus_type"],gpib["bus_id"])
                del gpib["bus_canon"]
                return 0,"GPIB adapter already initialized with different adapter address %s" % (b["adapter_addr"])
        if not found or (found and "bus_canon" not in b):
            # Configure adapter_addr
            retcode,res=submod.execcmd("write_"+gpib["bus_type"],gpib["bus_id"],r"++mode 0\n++addr %s\n++mode 1\n"%(gpib["adapter_addr"]))
            if retcode==0:
                self.inval(gpib_id)
                return 0,"Error setting adapter address <- %s" % (res)
            # Check connectivity
            retcode,res=submod.execcmd("wrnrd_until_"+gpib["bus_type"],gpib["bus_id"],r"++mode\n",r"\n")
            if retcode==0 or res!="1":
                self.inval(gpib_id)
                return 0,"Error checking connectivity <- %s" % (res)
            # Configure
            retcode,res=submod.execcmd("write_"+gpib["bus_type"],gpib["bus_id"],r"++eot_enable 1\n++eot_char 10\n")
            if retcode==0:
                self.inval(gpib_id)
                return 0,"Error while configuring GPIB link <- %s" % (res)
        # Shut up last recipient
        retcode,res=submod.execcmd("write_"+gpib["bus_type"],gpib["bus_id"],r"++auto 0\n")
        if retcode==0:
            self.inval(gpib_id)
            return 0,"Error while shuting up last recipient %s <- %s" % (res)
        gpib["bus_canon"] = bus_canon
        return 1,"ok"

    def inval(self,gpib_id):
        try:
            gpib = self.gpib_pool.get(gpib_id)
        except Exception as e:
            return 0,"gpib_" % (str(e))
        if "bus_canon" not in gpib:
            return 1,"not configured"
        retcode,res = submod.execcmd("inval_"+gpib["bus_type"],gpib["bus_id"])
        if retcode==0:
            return 0,"Error attempting to invalidate bus <- %s" % (res)
        del gpib["bus_canon"]
        return 1,"ok"

    def send(self,gpib,data):
        if not "bus_canon" in gpib:
            return 0,"not configured"
        data = r"++addr %s\n" % (gpib["dst_addr"]) + data
        retcode,res = submod.execcmd("write_"+gpib["bus_type"],gpib["bus_id"],data)
        if (retcode==0):
            return 0,"Error writing data <- %s" % (res)
        return 1,"ok"
    
    def write(self,gpib_id,data):
        try:
            gpib = self.gpib_pool.get(gpib_id)
        except Exception as e:
            return 0,"gpib_" % (str(e))
        # Write
        return self.send(gpib,data)

    def wrnrd_until(self,gpib_id,data,eot=r"\n",timeout="undef"):
        try:
            gpib = self.gpib_pool.get(gpib_id)
        except Exception as e:
            return 0,"gpib_" % (str(e))
        if eot!=r"\n":
            print("\n\nWarning: Calling wrnrd_until_gpib with eot other than %s\n\n"%(r"\n"))
        # Write and read
        data += r"++auto 1\n" # At the end add command to address device to talk
        retcode,res=self.send(gpib,data)
        if retcode==0:
            return 0,res
        # Avoid empty returns because of first character read being an eot
        res = ""
        while res=="":
            retcode,res=submod.execcmd("read_until_"+gpib["bus_type"],gpib["bus_id"],eot,timeout)
            if retcode==0:
                return 0,"Error reading GPIB answer <- %s" % (res)
        # Address device to listen
        retcode2,res2=self.send(gpib,r"++auto 0\n")
        if retcode2==0:
            return 0,"Error setting device to listen: %s" % (res2)
        return retcode,res

    def expect(self,gpib_id,pattern,timeout="undef"):
        try:
            gpib = self.gpib_pool.get(gpib_id)
        except Exception as e:
            return 0,"gpib_" % (str(e))
        if not "bus_canon" in gpib:
            return 0,"not configured"
        retcode,res = submod.execcmd("write_"+gpib["bus_type"],gpib["bus_id"],r"++addr %s\n++auto 1\n" % (gpib["dst_addr"]))
        if retcode==0:
            return 0,"Error setting destination address to talk <- %s" % (res)
        retcode,res=submod.execcmd("expect_"+gpib["bus_type"],gpib["bus_id"],pattern,timeout)
        retcode2,res2=submod.execcmd("write_"+gpib["bus_type"],gpib["bus_id"],r"++auto 0\n")
        if retcode2==0:
            return 0,"%s, and error setting destination address not to talk <- %s" % (res2)
        if retcode==0:
            return 0,"Pattern not found or GPIB link not responding <- %s" % (res)
        return retcode,res

# CREATE POOL ####################################################

me = gpib_class()

# COMMANDS #######################################################

# Put serialized API in memory if not called via import
if __name__ == '__main__':
    global api; api = getapi.load_api(__file__)

def getapi_gpib():
    submod.setres(1,api)

def init_gpib(conf_string):
    """Initialize a GPIB link.

    *conf_string* must include:

    - bus: conf_string of the underlying bus module. For tcp and serial, the default tcp port or serial vendor and product id will be included if not present. For a USB adapter, a typical value could be `serial()`
    - dst_addr: GPIB address of the destination device
    - adapter_addr (defaults to 0): GPIB address of the adapter
    
    Returns *gpib_id*."""
    retcode,res = me.init(conf_string)
    if retcode==0:
        submod.setres(retcode,"gpib: %s" % (res))
        return
    submod.setres(retcode,res)

def deinit_gpib(gpib_id):
    "Deinitialize and deregister GPIB link *gpib_id*."
    retcode,res = me.deinit(gpib_id)
    if retcode==0:
        submod.setres(retcode,"gpib: %s" % (res))
        return
    submod.setres(retcode,res)

def config_gpib(gpib_id):
    "Configure GPIB link *gpib_id*."
    retcode,res = me.config(gpib_id)
    if retcode==0:
        submod.setres(retcode,"gpib: %s" % (res))
        return
    submod.setres(retcode,res)

def inval_gpib(gpib_id):
    "Invalidate configuration of GPIB link *gpib_id*."
    retcode,res = me.inval(gpib_id)
    if retcode==0:
        submod.setres(retcode,"gpib: %s" % (res))
        return
    submod.setres(retcode,res)

def write_gpib(gpib_id,data):
    "Write *data* to GPIB link *gpib_id*."
    retcode,res = me.write(gpib_id,data)
    if retcode==0:
        submod.setres(retcode,"gpib: %s" % (res))
        return
    submod.setres(retcode,res)

def wrnrd_until_gpib(gpib_id,data,eot=r"\n",timeout="undef"):
    "Write and read data to and from GPIB link *gpib_id*."
    retcode,res = me.wrnrd_until(gpib_id,data,eot,timeout)
    if retcode==0:
        submod.setres(retcode,"gpib: %s" % (res))
        return
    submod.setres(retcode,res)

def expect_gpib(gpib_id,pattern,timeout="undef"):
    "Read data from GPIB link *gpib_id* until *pattern* is found or timeout."
    retcode,res = me.expect(gpib_id,pattern,timeout)
    if retcode==0:
        submod.setres(retcode,"gpib: %s" % (res))
        return
    submod.setres(retcode,res)

