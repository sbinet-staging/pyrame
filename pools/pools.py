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

class pool:
    def __init__(self,name="undef"):
        self.name = name
        self.elements = {}

    def new(self,params={},id=-1):
        id = int(id)
        if id==-1:
            # Calculate id based on last used
            if len(self.elements)>0:
                id = max(self.elements.keys()) + 1
            else:
                id = 0
        elif id in self.elements:
            raise Exception("id %d already existant in the pool" % (id))
        params["id"] = id
        self.elements[id] = params
        return str(id)

    def get(self,id):
        id = int(id)
        # Look for id in pool
        if id not in self.elements:
            raise Exception("id %d has not been found in the pool" % (id))
        return self.elements[id]

    def get_all(self):
        return self.elements.iteritems()

    def remove(self,id):
        id = int(id)
        if id not in self.elements:
            raise Exception("id %d has not been found in the pool" % (id))
        return self.elements.pop(id)

    def length(self):
        return len(self.elements)

    def call(self,id,func,*params):
        try:
            element = self.get(id)
        except Exception as e:
            return 0,str(e)
        return func(element,*params)
