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

import sys,os,subprocess,re

if len(sys.argv)<3:
  print("usage %s vendor product [serial_number]"%(sys.argv[0]))
  sys.exit(1)

vendor = sys.argv[1]
product = sys.argv[2]
if len(sys.argv)>3 and sys.argv[3]!="undef":
    serialnum = sys.argv[3]
else:
    serialnum = None

result = subprocess.Popen(["/usr/bin/lsusb"],stdout=subprocess.PIPE)
res,_ = result.communicate()
if result.returncode!=0:
    print("error getting USB list: %s"%(res))
    sys.exit(1)

buses_devs=re.findall("Bus (.*?) Device (.*?): ID %s:%s"%(vendor,product),res)
if len(buses_devs)==0:
    print("vendor and/or product id's not found")
    sys.exit(1)

sys.stderr.write("found %d devices\n"%(len(buses_devs)))

if not serialnum and len(buses_devs)!=1:
    print("multiple devices with same vendor and product id and serial number not provided")
    sys.exit(1)

devnames=[]
errors=[]
for bus_dev in buses_devs:
    result = subprocess.Popen(("udevadm info -q path -n /dev/bus/usb/%s/%s"%(bus_dev[0],bus_dev[1])).split(" "),stdout=subprocess.PIPE)
    res,_ = result.communicate()
    if result.returncode!=0:
        errors.append("error getting USB device path for bus %s dev %s"%(bus_dev[0],bus_dev[1]))
        sys.stderr.write(errors[-1]+"\n")
        continue
    path = "/sys"+res.strip()
    sys.stderr.write("\nchecking out %s\n"%(path))
    result = subprocess.Popen(("find %s -name tty*"%(path)).split(" "),stdout=subprocess.PIPE)
    res,_ = result.communicate()
    if result.returncode!=0 or res.strip()=="":
        errors.append("error getting ttyUSB device path for %s"%(path))
        sys.stderr.write(errors[-1]+"\n")
        continue
    if serialnum:
        if os.path.exists(path+"/serial"):
            with open(path+"/serial","r") as f: s = f.read()
            if s.strip()!=serialnum:
                errors.append("invalid serial number for %s"%(path))
                sys.stderr.write(errors[-1]+"\n")
                continue
        else:
            errors.append("no serial number on %s"%(path))
            sys.stderr.write(errors[-1]+"\n")
            continue
    devnames.append("/dev/"+res.split("\n")[0].split("/")[-1])
    sys.stderr.write("found device at %s\n"%(devnames[-1]))

sys.stderr.write("\n")

if len(devnames)>1:
    print("multiple matches found")
    if len(errors)!=0:
        print(":"+";".join(errors))
    sys.exit(1)
if len(devnames)==0:
    print("no device found")
    sys.exit(1)

print(devnames[0])

sys.exit(0)
