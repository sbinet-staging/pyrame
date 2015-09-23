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
import pools, getapi, conf_strings

# CLASS ##########################################################

class scpi(object):
    def __init__(self,module_name):
        self.module_name = module_name
        self.scpi_pool = pools.pool(module_name)

    def init(self,conf_string):
        try:
            conf = conf_strings.parse(conf_string)
        except Exception as e:
            return 0,str(e)
        if conf.name!=self.scpi_pool.name:
            return 0,"Invalid module name %s in conf_string. Should be %s" % (conf.name,self.scpi_pool.name)
        if not conf.has("bus"):
            return 0,"Missing bus parameter in conf_string"
        try:
            conf_bus = conf_strings.parse(conf.params["bus"])
        except Exception as e:
            return 0,str(e)
        # Initialize link
        retcode,res=submod.execcmd("init_"+conf_bus.name,conf.params["bus"])
        if retcode==0:
            return 0,"Error initializing link <- %s" % (res)
        link_id = res
        # Add to the pool
        scpi_id = self.scpi_pool.new({"bus":conf_bus.name,"link_id":link_id})
        return 1,scpi_id

    def deinit(self,scpi_id):
        try:
            scpi = self.scpi_pool.get(scpi_id)
        except Exception as e:
            return 1,"%s_%s" % (self.scpi_pool.name,str(e))
        # Deinitialize link
        retcode,res=submod.execcmd("deinit_"+scpi["bus"],scpi["link_id"])
        if retcode==0:
            return 0,"Error deinitializing link %s <- %s" % (scpi["link_id"],res)
        # Remove scpi from the pool
        try:
            self.scpi_pool.remove(scpi_id)
        except Exception as e:
            return 0,str(e)
        return 1,"ok"

    def config(self,scpi_id,error_check="normal",command=""):
        try:
            scpi = self.scpi_pool.get(scpi_id)
        except Exception as e:
            return 0,"%s_%s" % (self.scpi_pool.name,str(e))
        if "error_check" in scpi:
            return 1,"already configured"
        # Define error checking level
        # Fast: doesn't check error queue. Sends all commands at once
        # Normal: checks error queue. Sends all commands at once
        # Careful: checks error queue. Sends commands one by one
        if error_check.lower() not in ["fast","normal","careful"]:
            return 0,"Invalid error_check mode. Valid modes are: fast, normal, careful"
        # Configure link
        retcode,res=submod.execcmd("config_"+scpi["bus"],scpi["link_id"])
        if retcode==0:
            return 0,"Error configuring link <- %s" % (res)
        scpi["error_check"] = error_check.lower()
        # Optional configuration commands
        if command!="" and command!="undef":
            retcode,res=submod.execcmd("write_"+scpi["bus"],scpi["link_id"],command+r"\n")
            if retcode==0:
                self.inval(scpi_id)
                return 0,"Error writing to link <- %s" % (res)
        # Clean up error queue
        retcode,errors = self.get_errors(scpi)
        if retcode==0:
            self.inval(scpi_id)
            return 0,"Error cleaning up the error queue <- %s" % errors
        return 1,"ok"

    def inval(self,scpi_id):
        try:
            scpi = self.scpi_pool.get(scpi_id)
        except Exception as e:
            return 0,"%s_%s" % (self.scpi_pool.name,str(e))
        if "error_check" not in scpi:
            return 1,"not configured"
        # Invalidate link
        retcode,res=submod.execcmd("inval_"+scpi["bus"],scpi["link_id"])
        if retcode==0:
            return 0,"Error configuring link <- %s" % (res)
        del scpi["error_check"]
        return 1,"ok"

    def expand_channels(self,channel_list):
        "Parse comma-separated channel list. Dash-defined ranges accepted. e.g.: 1,3,7-12,5"
        if channel_list=="all":
            return self.channels
        channel_list = channel_list.split(",")
        channels = []
        for channel in channel_list:
            if len(channel.split("-")) > 1:
                channels += range(int(channel.split("-")[0]),int(channel.split("-")[1])+1)
            else:
                channels.append(int(channel))
        return list(set(channels))

    def check_channel(self,channel):
        if channel=="" or channel=="undef":
            return None
        channel_list = self.expand_channels(channel)
        for i in range(len(channel_list)):
            if int(channel_list[i]) in range(1,len(self.channels)+1):
                channel_list[i] = self.channels[int(channel_list[i])-1]
            else:
                return None
        return channel_list

    def get_errors(self,scpi):
        if scpi["error_check"]=="fast":
            return 1,""
        command = "SYST:ERR?"
        errors = ""
        while True: 
            time.sleep(0.005)
            retcode,res=submod.execcmd("wrnrd_until_"+scpi["bus"],scpi["link_id"],command+r"\n",r"\n")
            if retcode==0:
                return 0,res
            try:
                if int(res.split(",",1)[0])!=0:
                    errors += res if errors=="" else "; "+res
                else:
                    break
            except Exception as e:
                return 0,"Read wrong response while getting error queue: %s" % (res)
        return 1,errors

    def send_command(self,scpi,command):
        if "error_check" not in scpi:
            return 0,"not configured"
        if scpi["error_check"]=="careful":
            command = command.split(r"\n")
        else:
            command = [command]
        for cmd in command:
            retcode,res=submod.execcmd("write_"+scpi["bus"],scpi["link_id"],cmd+r"\n")
            if retcode==0:
                return 0,"Error writing to link <- %s" % (res)
            retcode,errors = self.get_errors(scpi)
            if errors!="":
                return 0,"Error(s) returned from the PS <- %s" % (errors)
        return 1,"ok"

    def send_query(self,scpi,query):
        if "error_check" not in scpi:
            return 0,"not configured"
        retcode,res=submod.execcmd("wrnrd_until_"+scpi["bus"],scpi["link_id"],query+r"\n",r"\n")
        if retcode==0:
            return 0,"Error querying link <- %s" % (res)
        retcode,errors = self.get_errors(scpi)
        if errors!="":
            return 0,"Error(s) returned from the PS <- %s" % (errors)
        return 1,res

    def simple_query(self,scpi_id,channel,query):
        try:
            scpi = self.scpi_pool.get(scpi_id)
        except Exception as e:
            return 0,"%s_%s" % (self.scpi_pool.name,str(e))
        # Check parameters
        channel = self.check_channel(channel)
        if channel==None:
            return 0,"invalid channel"
        # Send the command
        response = ""
        for chan in channel:
            qy = query.format(channel=chan)
            retcode,res = self.send_query(scpi,qy)
            if retcode==0:
                return retcode,res
            response += res + ";"
        return 1,response[:-1]

    def simple_command(self,scpi_id,channel,command):
        try:
            scpi = self.scpi_pool.get(scpi_id)
        except Exception as e:
            return 0,"%s_%s" % (self.scpi_pool.name,str(e))
        channel = self.check_channel(channel)
        if channel==None:
            return 0,"invalid channel"
        # Send the command
        for chan in channel:
            cmd = command.format(channel=chan)
            retcode,res = self.send_command(scpi,cmd)
            if retcode==0:
                return retcode,res
        return 1,"ok"

    def free_command(self,scpi_id,command):
        try:
            scpi = self.scpi_pool.get(scpi_id)
        except Exception as e:
            return 0,"%s_%s" % (self.scpi_pool.name,str(e))
        return self.send_command(scpi,command)

    def reset(self,scpi_id):
        try:
            scpi = self.scpi_pool.get(scpi_id)
        except Exception as e:
            return 0,"%s_%s" % (self.scpi_pool.name,str(e))
        command = "*RST"
        return self.send_command(scpi,command)

    def set_voltage(self,scpi_id,voltage,channel,command):
        try:
            scpi = self.scpi_pool.get(scpi_id)
        except Exception as e:
            return 0,"%s_%s" % (self.scpi_pool.name,str(e))
        # Check parameters
        if voltage=="undef":
            return 1,"Did nothing !"
        channel = self.check_channel(channel)
        if channel==None:
            return 0,"invalid channel"
        # Send the command
        for chan in channel:
            if "current_limit"+chan not in scpi:
                return 0,"Set current limit first"
            current = scpi["current_limit"+chan]
            voltage = float(voltage)
            cmd = command.format(channel=chan,current=current,voltage=voltage)
            retcode,res = self.send_command(scpi,cmd)
            if retcode==0:
                return 0,"Error setting voltage on channel %s: %s" % (chan,res)
        return 1,"ok"

    def set_current(self,scpi_id,current,channel,command):
        try:
            scpi = self.scpi_pool.get(scpi_id)
        except Exception as e:
            return 0,"%s_%s" % (self.scpi_pool.name,str(e))
        # Check parameters
        if current=="undef":
            return 1,"Did nothing !"
        channel = self.check_channel(channel)
        if channel==None:
            return 0,"invalid channel"
        # Send the command
        for chan in channel:
            if "voltage_limit"+chan not in scpi:
                return 0,"Set voltage limit first"
            voltage = scpi["voltage_limit"+chan]
            current = float(current)
            cmd = command.format(channel=chan,current=current,voltage=voltage)
            retcode,res = self.send_command(scpi,cmd)
            if retcode==0:
                return 0,"Error setting current on channel %s: %s" % (chan,res)
        return 1,"ok"

    def set_voltage_limit(self,scpi_id,voltage_limit,channel,command):
        try:
            scpi = self.scpi_pool.get(scpi_id)
        except Exception as e:
            return 0,"%s_%s" % (self.scpi_pool.name,str(e))
        # Check parameters
        if voltage_limit=="undef":
            return 1,"Did nothing !"
        voltage_limit = float(voltage_limit)
        channel = self.check_channel(channel)
        if channel==None:
            return 0,"invalid channel"
        # Send the command
        for chan in channel:
            cmd = command.format(channel=chan,voltage_limit=voltage_limit)
            retcode,res = self.send_command(scpi,cmd)
            if retcode==0:
                return 0,"Error setting voltage limit on channel %s: %s" % (chan,res)
            scpi["voltage_limit"+chan] = voltage_limit
        return 1,"ok"

    def set_current_limit(self,scpi_id,current_limit,channel,command):
        try:
            scpi = self.scpi_pool.get(scpi_id)
        except Exception as e:
            return 0,"%s_%s" % (self.scpi_pool.name,str(e))
        # Check parameters
        if current_limit=="undef":
            return 1,"Did nothing !"
        current_limit = float(current_limit)
        channel = self.check_channel(channel)
        if channel==None:
            return 0,"invalid channel"
        # Send the command
        for chan in channel:
            cmd = command.format(channel=chan,current_limit=current_limit)
            retcode,res = self.send_command(scpi,cmd)
            if retcode==0:
                return 0,"Error setting current limit on channel %s: %s" % (chan,res)
            scpi["current_limit"+chan] = current_limit
        return 1,"ok"

    def check_range(self,range,ranges):
        range=range.lower()
        if range not in ["auto","min","max","undef"]:
            try:
                if float(range) not in ranges:
                    raise Exception()
            except:
                return 0,"Invalid range. Valid values are: " + " ".join(map(str,ranges))
        if range in ["auto","undef"]:
            return 1,None
        return 2,range

    def check_resolution(self,resolution,units):
        resolution=resolution.lower()
        if resolution in ["","undef"]:
            return 1,"undef"
        if resolution.endswith(units):
            resolution=resolution[:-len(units)]
            retcode=2
        else:
            retcode=3
        if resolution not in ["max","min"]:
            try:
                float(resolution)
            except:
                return 0,"Invalid resolution"
        else:
            # so that "max"/"min" refer to maximum/minimum resolution
            # e.g: maximum/minimum number of PLC integration
            retcode=2
        return retcode,resolution

    def measure(self,scpi_id,range,resolution,channel,conf_command,measure_command):
        try:
            scpi = self.scpi_pool.get(scpi_id)
        except Exception as e:
            return 0,"%s_%s" % (self.scpi_pool.name,str(e))
        # Parse channel
        channel = self.check_channel(channel)
        if channel==None:
            return 0,"invalid channel"
        # Send the command
        results=[]
        for chan in channel:
            cmd = conf_command.format(channel=chan,range=range,resolution=resolution)
            if not ("last_measure_conf"+chan in scpi and scpi["last_measure_conf"+chan]==cmd):
                retcode,res = self.send_command(scpi,cmd)
                if retcode==0:
                    return 0,"Error configuring measurement on channel %s: %s" % (chan,res)
                scpi["last_measure_conf"+chan]=cmd
            cmd = measure_command.format(channel=chan,range=range,resolution=resolution)
            retcode,res = self.send_query(scpi,cmd)
            if retcode==0:
                return 0,"Error performing measurement on channel %s: %s" % (chan,res)
            results.append(res)
        return 1,";".join(results)

    def get_error_queue(self,scpi_id):
        try:
            scpi = self.scpi_pool.get(scpi_id)
        except Exception as e:
            return 0,"%s_%s" % (self.scpi_pool.name,str(e))
        if "error_check" not in scpi:
            return 0,"not configured"
        return self.get_errors(scpi)

