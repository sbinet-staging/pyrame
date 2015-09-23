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

import pools

class api_pool:
    "API pool"
    def __init__(self):
        self.pool=pools.pool()

    def add_api_from_string(self,module_name,str_api):
        """Add API to pool from string. semicolons between functions; colon between function name and parameters; comma between parameters. Example:
            
            get_voltage_ps:ps_id,channel;get_current_ps:ps_id,channel;..."""
        for f in str_api.strip("\n;").split(";"):
            f = f.split(":")
            if f[1]=="":
                args=[]
            else:
                args=f[1].split(",")
            self.pool.new({"model":module_name,"function":f[0],"args":args})
        
    def add_api_from_file(self,module_name,file_name):
        """Add API to pool from file. newlines or semicolons between functions; colon between function name and parameters; comma between parameters. Example:
                        
            get_voltage_ps:ps_id,channel
            get_current_ps:ps_id,channel
            ..."""
        with open(file_name,"r") as api_file: 
            api = api_file.read().replace("\n",";")
        return self.add_api_from_string(module_name,api)

    def get_api(self,module_name,func_name):
        "Find *func_name* of *module_name* in pool and return a dictionary with keys *model*, *function* and *args*, where the two first are strings and the latter is a list of strings. If not found, return -1"
        for _,api in self.pool.get_all():
            if (api["model"]==module_name) and (api["function"]==func_name):
                return api
        return -1

    def is_present(self,module_name):
        "Check if the API of *module_name* is present in the pool"
        for _,api in self.pool.get_all():
            if (api["model"]==module_name):
                return True
        return False
