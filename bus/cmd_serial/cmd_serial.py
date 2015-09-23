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

from buses import *
from pools import *
import conf_strings, getapi

import serial,select
import subprocess,os

# SERIAL_BUS #####################################################

baudrates = [50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800, 500000, 576000, 921600, 1000000, 1152000, 1500000, 2000000, 2500000, 3000000, 3500000, 4000000]

class serial_bus(buses):
    def __init__(self):
        self.serial_pool = pool()

    def init(self,conf_string):
        try:
            conf = conf_strings.parse(conf_string)
        except Exception as e:
            return 0,str(e)
        if conf.name!="serial":
            return 0,"Invalid module name %s in conf_string. Should be serial" % (conf.name)
        serialnum=vendor=product=device = "undef"
        baudrate = "9600"
        bytesize = serial.EIGHTBITS
        stopbits = serial.STOPBITS_ONE
        parity = serial.PARITY_NONE
        flow = "undef"
        # serial number
        if conf.has("serialnum"):
            serialnum = conf.params["serialnum"]
        # vendor/product or device
        if conf.has("vendor","product"):
            vendor = conf.params["vendor"]
            product = conf.params["product"]
            # validate
            if (len(vendor)!=4 or len(product)!=4):
                return 0,"Invalid length of vendor or product id's"
        elif conf.has("device"):
            device = conf.params["device"]
        else:
            return 0,"conf_string does not contain neither vendor and product id's or device name"
        # baudrate
        if conf.has("baudrate") and conf.params["baudrate"]!="undef":
            baudrate = int(conf.params["baudrate"])
            if baudrate not in baudrates:
                return 0,"baudrate %d in conf_string is not valid"%(baudrate)
        # bytesize
        if conf.has("bytesize") and conf.params["bytesize"]!="undef":
            bytesize = conf.params["bytesize"]
            if bytesize=="8":
                bytesize = serial.EIGHTBITS
            elif bytesize=="7":
                bytesize = serial.SEVENBITS
            elif bytesize=="6":
                bytesize = serial.SIXBITS
            elif bytesize=="5":
                bytesize = serial.FIVEBITS
            else:
                return 0,"bytesize %s in conf_string is not valid"%(bytesize)
        # stopbits
        if conf.has("stopbits") and conf.params["stopbits"]!="undef":
            stopbits = conf.params["stopbits"]
            if stopbits=="1":
                stopbits = serial.STOPBITS_ONE
            elif stopbits=="1.5":
                stopbits = serial.STOPBITS_ONE_POINT_FIVE
            elif stopbits=="2":
                stopbits = serial.STOPBITS_TWO
            else:
                return 0,"stopbits %s in conf_string are not valid"%(stopbits)
        # parity
        if conf.has("parity") and conf.params["parity"]!="undef":
            parity = conf.params["parity"]
            if parity=="N":
                parity = serial.PARITY_NONE
            elif parity=="E":
                parity = serial.PARITY_EVEN
            elif parity=="O":
                parity = serial.PARITY_ODD
            elif parity=="M":
                parity = serial.PARITY_MARK
            elif parity=="S":
                partiy = serial.PARITY_SPACE
            else:
                return 0,"parity %s in conf_string is not valid"%(parity)
        # flow control
        if conf.has("flow") and conf.params["flow"]!="undef":
            flow = conf.params["flow"]
            if flow!="xonxoff" and flow!="rtscts" and flow!="dsrdtr":
                return 0,"invalid flow. must be xonxoff, rtscts or dsrftr"
        # timeout
        if conf.has("timeout") and conf.params["timeout"]!="undef":
            timeout = float(conf.params["timeout"])
        else:
            timeout = 60
        # Add to the pool
        serial_id = self.serial_pool.new({"vendor": vendor, "product": product, "device": device, "serialnum": serialnum, "baudrate": baudrate, "bytesize": bytesize, "stopbits": stopbits, "parity": parity, "flow": flow, "timeout": timeout})
        return 1,serial_id

    def deinit(self,serial_id):
        try:
            link = self.serial_pool.get(serial_id)
        except Exception as e:
            return 1,"link_%s" % (str(e))
        # Check status
        if "socket" in link:
            self.inval(serial_id)
        # Remove
        try:
            self.serial_pool.remove(serial_id)
        except Exception as e:
            return 0,str(e)
        return 1,"ok"

    def config(self,serial_id):
        try:
            link = self.serial_pool.get(serial_id)
        except Exception as e:
            return 0,"link_%s" % (str(e))
        # Check status
        if "socket" in link:
            return 0,"already configured"
        # Get device if necessary
        if link["device"]=="undef":
            result = subprocess.Popen(["/usr/local/bin/get_dev_"+os.uname()[0].lower()+".sh",link["vendor"],link["product"],link["serialnum"]],stdout=subprocess.PIPE)
            res,_ = result.communicate()
            link["device"] = res.strip()
            if result.returncode!=0:
                link["device"] = "undef"
                return 0,"Error getting device name <- %s"%(res.strip())
        # Initialize serial socket
        try:
            link["socket"] = serial.Serial(link["device"],link["baudrate"],link["bytesize"],link["parity"],link["stopbits"],link["timeout"],link["flow"]=="xonxoff",link["flow"]=="rtscts",dsrdtr=(link["flow"]=="dsrdtr"))
            if link["flow"]=="rtscts":
                link["socket"].setRTS()
            if link["flow"]=="dsrdtr":
                link["socket"].setDTR()
            link["socket"].flushInput()
        except:
            return 0,"Error connecting to %s" % (link["device"])
        return 1,link["device"]

    def inval(self,serial_id):
        try:
            link = self.serial_pool.get(serial_id)
        except Exception as e:
            return 0,"link_%s" % (str(e))
        # Check status
        if "socket" not in link:
            return 0,"not configured"
        link["socket"].close()
        del link["socket"]
        if link["vendor"]!="undef" and link["product"]!="undef":
            link["device"] = "undef"
        return 1,"ok"

    def write(self,serial_id,mode,data):
        try:
            link = self.serial_pool.get(serial_id)
        except Exception as e:
            return 0,"link_%s" % (str(e))
        return super(serial_bus,self).write(link,mode,data)

    def read(self,serial_id,mode,bytes_to_read,timeout="undef"):
        try:
            link = self.serial_pool.get(serial_id)
        except Exception as e:
            return 0,"link_%s" % (str(e))
        return super(serial_bus,self).read(link,mode,bytes_to_read,timeout)

    def read_until(self,serial_id,mode,eot,timeout="undef"):
        try:
            link = self.serial_pool.get(serial_id)
        except Exception as e:
            return 0,"link_%s" % (str(e))
        return super(serial_bus,self).read_until(link,mode,eot,timeout)

    def expect(self,serial_id,pattern,timeout="undef"):
        try:
            link = self.serial_pool.get(serial_id)
        except Exception as e:
            return 0,"link_%s" % (str(e))
        return super(serial_bus,self).expect(link,pattern,timeout)

    def get_timeout(self,link):
        return link["timeout"]

    def ll_send(self,link,data):
        if not "socket" in link:
            return 0,"not configured"
        try:
            res = link["socket"].write(data)
            if res!=len(data):
                raise Exception("Not all data sent")
        except Exception as e:
            return 0,"Error sending data to %s <- %s" % (link["device"],str(e))
        return 1,"ok"

    def ll_receive(self,link,bytes_to_read,timeout="undef"):
        if not "socket" in link:
            return 0,"not configured"
        if timeout=="" or timeout=="undef":
            timeout = link["timeout"]
        res = select.select([link["socket"].fileno()],[],[],float(timeout))
        if len(res[0])==0:
            return 0,"Timeout while waiting for data"
        # Read
        try:
            response = link["socket"].read(int(bytes_to_read))
        except Exception as e:
            return 0,"Error reading data from %s <- %s" % (link["device"],str(e))
        return 1,response

# CREATE BUS POOL ################################################

me = serial_bus()

# COMMANDS #######################################################

# Put serialized API in memory if not called via import
if __name__ == '__main__':
    global api; api = getapi.load_api(__file__)

def getapi_serial():
    submod.setres(1,api)

def init_serial(conf_string):
    """Initialize a serial link.

    *conf_string* must include either:

    - vendor and product: vendor and product id's of a USB device

        or

    - device: UNIX device name. e.g.: /dev/ttyUSB0

    it can optionally include:

    - serialnum: serial number of the USB device.
    - baudrate: rate in bits per second
    - bytesize: byte size in bits
    - stopbits: number of stop bits (1, 1.5 or 2)
    - parity: parity (N, E, O, M or S for None, Even, Odd, Mark and Space)
    - timeout: default timeout in seconds for this link. Can be float.

    Returns id of the serial link, *serial_id*."""
    retcode,res = me.init(conf_string)
    if retcode==0:
        submod.setres(retcode,"serial: %s" % (res))
        return
    submod.setres(retcode,res)

def deinit_serial(serial_id):
    "Deinitialize serial link *serial_id*."
    retcode,res = me.deinit(serial_id)
    if retcode==0:
        submod.setres(retcode,"serial: %s" % (res))
        return
    submod.setres(retcode,res)

def config_serial(serial_id):
    "Configure serial link *serial_id*."
    retcode,res = me.config(serial_id)
    if retcode==0:
        submod.setres(retcode,"serial: %s" % (res))
        return
    submod.setres(retcode,res)

def inval_serial(serial_id):
    "Invalidate configuration of serial link *serial_id*."
    retcode,res = me.inval(serial_id)
    if retcode==0:
        submod.setres(retcode,"serial: %s" % (res))
        return
    submod.setres(retcode,res)

# WRITE ##########################################################

def write_serial(serial_id,data):
    "Write *data* to serial link *serial_id*."
    retcode,res = me.write(serial_id,"escaped",data)
    if retcode==0:
        submod.setres(retcode,"serial: %s" % (res))
        return
    submod.setres(retcode,res)

def write_bin_serial(serial_id,data):
    "Write binary *data* to serial link *serial_id*. *data* is a string where each character represents 4 bits in hexadecimal base. Little endian for each group of 8 bits."
    retcode,res = me.write(serial_id,"bin",data)
    if retcode==0:
        submod.setres(retcode,"serial: %s" % (res))
        return
    submod.setres(retcode,res)

# READ ###########################################################

def read_serial(serial_id,bytes_to_read,timeout="undef"):
    "Read up to *bytes_to_read* bytes from serial link *serial_id*"
    retcode,res = me.read(serial_id,"ignore_chars",bytes_to_read,timeout)
    if retcode==0:
        submod.setres(retcode,"serial: %s" % (res))
        return
    submod.setres(retcode,res)

def read_bin_serial(serial_id,bytes_to_read,timeout="undef"):
    "Read up to *bytes_to_read* bytes from serial link *serial_id* in binary format. The data read is encoded by blocks of 8 bits with two hexadecimal characters little endian."
    retcode,res = me.read(serial_id,"bin",bytes_to_read,timeout)
    if retcode==0:
        submod.setres(retcode,"serial: %s" % (res))
        return
    submod.setres(retcode,res)

# READ UNTIL #####################################################

def read_until_serial(serial_id,eot,timeout="undef"):
    "Read from serial link *serial_id* until a character from *eot* comma-separated list is found"
    retcode,res = me.read_until(serial_id,"ignore_chars",eot,timeout)
    if retcode==0:
        submod.setres(retcode,"serial: %s" % (res))
        return
    submod.setres(retcode,res)

def read_bin_until_serial(serial_id,eot,timeout="undef"):
    "Read from serial link *serial_id* until a character from *eot* comma-separated list is found. The data read is encoded by blocks of 8 bits with two hexadecimal characters little endian."
    retcode,res = me.read_until(serial_id,"bin",eot,timeout)
    if retcode==0:
        submod.setres(retcode,"serial: %s" % (res))
        return
    submod.setres(retcode,res)

# WRNRD ##########################################################

def wrnrd_serial(serial_id,data,bytes_to_read,timeout="undef"):
    "Write and read *data* to and from serial link *serial_id*"
    retcode,res = me.write(serial_id,"escaped",data)
    if retcode==0:
        submod.setres(retcode,"serial: %s" % (res))
        return
    retcode,res = me.read(serial_id,"ignore_chars",bytes_to_read,timeout)
    if retcode==0:
        submod.setres(retcode,"serial: %s" % (res))
        return
    submod.setres(retcode,res)

def wrnrd_bin_serial(serial_id,data,bytes_to_read,timeout="undef"):
    "Write and read binary *data* to and from serial link *serial_id*. *data* is a string where each character represents 4 bits in hexadecimal base. Little endian for each group of 8 bits."
    retcode,res = me.write(serial_id,"bin",data)
    if retcode==0:
        submod.setres(retcode,"serial: %s" % (res))
        return
    retcode,res = me.read(serial_id,"bin",bytes_to_read,timeout)
    if retcode==0:
        submod.setres(retcode,"serial: %s" % (res))
        return
    submod.setres(retcode,res)

# WRNRD_UNTIL ####################################################

def wrnrd_until_serial(serial_id,data,eot,timeout="undef"):
    "Write and read *data* to and from serial link *serial_id* until a character from comma-separated list *eot* is found"
    retcode,res = me.write(serial_id,"escaped",data)
    if retcode==0:
        submod.setres(retcode,"serial: %s" % (res))
        return
    retcode,res = me.read_until(serial_id,"ignore_chars",eot,timeout)
    if retcode==0:
        submod.setres(retcode,"serial: %s" % (res))
        return
    submod.setres(retcode,res)

def wrnrd_bin_until_serial(serial_id,data,eot,timeout="undef"):
    "Write and read *data* to and from serial link *serial_id* until a character from comma-separated list *eot* is found. *data* is a string where each character represents 4 bits in hexadecimal base. Little endian for each group of 8 bits. Read data is return in the same format."
    retcode,res = me.write(serial_id,"bin",data)
    if retcode==0:
        submod.setres(retcode,"serial: %s" % (res))
        return
    retcode,res = me.read_until(serial_id,"bin",eot,timeout)
    if retcode==0:
        submod.setres(retcode,"serial: %s" % (res))
        return
    submod.setres(retcode,res)

# EXPECT #########################################################

def expect_serial(serial_id,pattern,timeout="undef"):
    "Read data from serial link *serial_id* until *pattern* is found or timeout."
    retcode,res = me.expect(serial_id,pattern,timeout)
    if retcode==0:
        submod.setres(retcode,"serial: %s" % (res))
        return
    submod.setres(retcode,res)

