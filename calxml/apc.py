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

import bindpyrame
import apipools

class APC:
    """automatic procedure caller"""
    def __init__(self,phase,portTable):
	self.phase = phase
        self.domip=""
        self.port_table=bindpyrame.init_ports_table(portTable)
        self.apipools=apipools.api_pool()
        self.devices_lifo=[]
        self.current_id=0
	 
    def init_apc(self,device,name,dicoCmds):
        """this function apply a function to the discovered device"""

        #print what we discovered
        #print("===> init_apc for a %s with name %s on phase %s" %(device,name,self.phase))

        #store the name in the dicoCmds under name dev_name
        dicoCmds["dev_name"]=name

        #searching for such a name in cmod
        if submod.DEBUG:
            print("calling external function get_id_cmod")
        retcode,res=bindpyrame.sendcmd("127.0.0.1",bindpyrame.get_port("CMOD_PORT",self.port_table),"get_id_cmod",name)
        if retcode==1:
            dicoCmds["%s_id"%(device)]=res

        #store the parent device id in the dicoCmds
        if self.devices_lifo!=[]:
            dicoCmds["parent_device"]=self.devices_lifo[-1]
        else:
            dicoCmds["parent_device"]="0"
            
        #if domain store the ip for future pyrame commands
        if device=="domain":
            #store the ip for future pyrame commands
            self.domip= dicoCmds["domain_ip"]
    
            if self.domip=="undef":
                print("domain without IP : exiting...")
                retcode=0
                res="no ip"
                return retcode,res

        #get the module name
        modname="cmd_%s"%device

        #extract the function
        func="%s_%s"%(self.phase,device)

        #extract the api
        if not self.apipools.is_present(modname):
            self.apipools.add_api_from_file(modname,"/opt/pyrame/%s.api"%modname)
                
        api=self.apipools.get_api(modname,func)
        
        #send the command to the module
        if api!= -1:

            #extract the port
            port_name="%s_PORT"%(device.upper())
            port=bindpyrame.get_port(port_name,self.port_table)
            
            if submod.DEBUG:
                print("calling external function %s"%(func))
            params=[]
            for arg in api["args"]:
                if arg=="parent_device":
                    realargname="parent_device"
                elif arg=="dev_name":
                    realargname="dev_name"
                elif arg=="%s_id"%device:
                    realargname="%s_id"%device
                else:
                    realargname="%s_%s"%(device,arg)
                params.append(dicoCmds[realargname])
            retcode,res=bindpyrame.sendcmd(self.domip,port,func,*params)
            #print("-->result %d,%s"%(retcode,res))
            if retcode==0:
                print("Error:%s when executing %s"%(res,func))

            #TODO break if return=0

            #stock the result if it is an id
            self.devices_lifo.append(res)
        else:
            self.devices_lifo.append("-1")
            #print("no function %s for device %s"%(func,device))
            retcode=1
            res="no function with that name"
        return retcode,res


    def finalize_apc(self,device,name):
        """this function is called after the initialization of a device and all its subdevices"""

        #print what we discovered    
        #print ("===> finalize_apc for a %s with name %s on phase %s" %(device,name,self.phase))

        #searching for such a name in cmod
        if submod.DEBUG:
            print("calling external function get_id_cmod")
        retcode,res=bindpyrame.sendcmd("127.0.0.1",bindpyrame.get_port("CMOD_PORT",self.port_table),"get_id_cmod",name)
        if retcode==1:
            local_id=res
        else:
            local_id="-1"
        
        #depile the device id
        self.devices_lifo.pop()
        
        #extract the function
        func="%s_fin_%s"%(self.phase,device)

        #get the module name
        modname="cmd_%s"%device

        #extract the api
        if not self.apipools.is_present(modname):
            self.apipools.add_api_from_file(modname,"/opt/pyrame/%s.api"%modname)
                
        api=self.apipools.get_api(modname,func)

        #execute the command 
        if api!= -1: 

            #extract the port
            port_name="%s_PORT"%(device.upper())
            port=bindpyrame.get_port(port_name,self.port_table)
            
            if submod.DEBUG:
                print("calling external function %s"%(func))
            retcode,res=bindpyrame.sendcmd(self.domip,port,func,local_id)
            #print("-->result %d,%s"%(retcode,res))
            if retcode==0:
                print("Error:%s when executing %s"%(res,func))
            return retcode,res
        else:
            #print("no function %s for device %s"%(func,device))
            return 1,"no function with that name"

