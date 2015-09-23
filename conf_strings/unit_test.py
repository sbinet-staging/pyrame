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

import conf_strings

test_string="ag_33200(reset=7,bus1=gpib(addr=3,vol=5,bus=tcp(ip=10.220.0.3,port=2300),caddr=0),bus2=udp(ip=localhost))"

c = conf_strings.parse(test_string)

if c.name!="ag_33200":
    raise Exception("Incorrect name parsing of ag_33200")
if not c.has("reset","bus1","bus2"):
    raise Exception("Incorrect parsing of the variables")
if c.params["reset"]!="7":
    raise Exception("Incorrect parsing of reset variable")
if c.params["bus1"]!="gpib(addr=3,vol=5,bus=tcp(ip=10.220.0.3,port=2300),caddr=0)":
    raise Exception("Incorrect parsing of bus1 variable")
if c.params["bus2"]!="udp(ip=localhost)":
    raise Exception("Incorrect parsing of bus2 variable")

d = conf_strings.parse(c.params["bus1"])

if d.name!="gpib":
    raise Exception("Incorrect name parsing of gpib")
if not d.has("addr","vol","bus","caddr"):
    raise Exception("Incorrect parsing of the variables")
if d.params["addr"]!="3":
    raise Exception("Incorrect parsing of addr variable")
if d.params["vol"]!="5":
    raise Exception("Incorrect parsing of vol variable")
if d.params["bus"]!="tcp(ip=10.220.0.3,port=2300)":
    raise Exception("Incorrect parsing of bus variable")
if d.params["caddr"]!="0":
    raise Exception("Incorrect parsing of caddr variable")

e = conf_strings.parse(d.params["bus"])

if e.name!="tcp":
    raise Exception("Incorrect name parsing of tcp")
if not e.has("ip","port"):
    raise Exception("Incorrect parsing of the variables")
if e.params["ip"]!="10.220.0.3":
    raise Exception("Incorrect parsing of ip variable")
if e.params["port"]!="2300":
    raise Exception("Incorrect parsing of port variable")

f = conf_strings.parse(c.params["bus2"])

if f.name!="udp":
    raise Exception("Incorrect name parsing of udp")
if not f.has("ip"):
    raise Exception("Incorrect parsing of the variables")
if f.params["ip"]!="localhost":
    raise Exception("Incorrect parsing of ip variable")

