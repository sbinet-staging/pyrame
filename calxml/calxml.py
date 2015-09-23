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
import xmlConf

verbose = False
if len(sys.argv) < 5 :
    print("xmlConf.py needs 3 or 4  arguments :")
    print(" - action phase : init or config phase")
    print(" - the currentConfigFile  to parse (xml file)")
    print(" - the defaultConfigFile  to parse (xml file)")
    print(" - the port table")
    print(" - verbose :this fourth argument is optional (for test prints)") 
    sys.exit("Must provide at least actionPhase, an xmlCurrentFile and an xmlDefaultFile as parameters to the command xmlConf ")
    
phase = sys.argv[1]
xmlCurrentCfgFile = sys.argv[2]
xmlDefaultCfgFile = sys.argv[3]
portTable = sys.argv[4]
if len(sys.argv) == 6 :
    if sys.argv[5]=="verbose" :
	verbose =True
 
cfgStr=xmlConf.strip_file(xmlCurrentCfgFile)
  
y=xmlConf.XmlParserConf(phase,cfgStr,xmlDefaultCfgFile,portTable,verbose)
retcode,res=y.parserConf()
print("End of calxml : retcode=%d,res=%s"%(retcode,res))
	    
