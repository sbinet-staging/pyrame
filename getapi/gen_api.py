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

import sys
import os
from inspect import getmembers,isfunction,getargspec
import xml.etree.ElementTree as ET

if len(sys.argv) != 2:
    print("Usage: %s pyrame_module_name"%(sys.argv[0]))
    sys.exit(1)

sys.path.append(os.getcwd())

# Clean up module name
if sys.argv[1].endswith(".py"):
    module_name = sys.argv[1][:-3]
elif sys.argv[1].endswith(".xml"):
    module_name = sys.argv[1][:-4]
else:
    module_name = sys.argv[1]
if module_name.startswith("./"): module_name = module_name[2:]
module = __import__(module_name)

# Get list of python functions in the module
functions = [f[0] for f in getmembers(module) if isfunction(f[1])]

# Get list of external functions declared in the xml file
try:
    tree = ET.parse(module_name+".xml")
except:
    print("Error parsing %s.xml" % (module_name))
    sys.exit(1)
module_xml = tree.getroot()
functions_xml_r = []
functions_xml_py = []
for c in module_xml.findall("cmd"):
    if c.get("type") == "script":
        f_xml_py = []
        for f in c.findall("function"):
            f_xml_py.append(f.text)
            functions_xml_r.append(c.get("name"))
        if len(f_xml_py)==0:
            f_xml_py.append(c.get("name"))
            functions_xml_r.append(c.get("name"))
        functions_xml_py += f_xml_py
if len(functions_xml_r) != len(set(functions_xml_r)):
    print("Error: duplicate external functions names in %s.xml"%(module_name))
    sys.exit(1)

errors = 0

# Compare xml and module
for f in functions_xml_py:
    if f not in functions:
        print("Error: Function %s declared in %s.xml not implemented in %s.py" % (f,module_name,module_name))
        errors += 1

# Compare module and xml
short_module_name = module_name if module_name[:4]!="cmd_" else module_name[4:]
for f in functions:
    if f.endswith(short_module_name) and f not in functions_xml_py:
        print("Error: Function %s implemented in %s.py not declared in %s.xml" % (f,module_name,module_name))
        errors += 1

if errors:
    sys.exit(1)

# Get arguments for functions
output = ""
for i in range(len(functions_xml_r)):
    output += functions_xml_r[i] + ":" + ",".join(getargspec(getattr(module,functions_xml_py[i])).args) + "\n"

with open(module_name+".api","w") as file:
    file.write(output)

sys.exit(0)
