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

from time import sleep
read_delay = 0.05
from math import copysign

# Array of ca_sy527 power supplies (PS). Every PS is a namedtuple
from collections import namedtuple
ca_sy527_pool = []
ca_sy527_tuple = namedtuple ('ca_sy527_tuple', 'id link_type adapter_addr link_id')

# Put serialized API in memory if not called via import
from os import path
if __name__ == '__main__':
    with open(path.dirname(__file__)+"/cmd_ca_sy527.api","r") as api_file: api = api_file.read().replace("\n",";")

# Functions
def getapi_ca_sy527():
    submod.setres(1,api)

def init_ca_sy527(conf_string):
    """Initialize CA_SY527 power supply.

    conf_string: slash-separated string of:
        - link_type: 'usb' or 'eth'
        - adapter_addr: ip-address:port of Ethernet-RS232 adapter or serial device imprint

    Returns ca_sy527_id"""
    global ca_sy527_pool
    global ca_sy527_tuple
    global timeout
    # Extract parameters from conf_string
    if conf_string.count("/") != 1:
        submod.setres(0,"ca_sy527: Invalid number of parameters")
        return
    link_type,adapter_addr = conf_string.split("/",1)
    # Validate link_type and initialize depending on its value
    if link_type == "eth":
        link_type = "tcp"
    elif link_type == "usb":
        link_type = "serial"
    else:
        submod.setres(0,"ca_sy527: Invalid link_type parameter")
        return
    link_id = ""
    for ca_sy527 in ca_sy527_pool:
        # If a connection with the same IP/serial_imprint (adapter_addr) is already
        # in the pool, get its tcp_id/serial_id (socket)
        if ca_sy527.adapter_addr == adapter_addr:
            link_id = link_id
    # If link_id is not set, it means that any link has already been initialized with that IP or serial device imprint, so do it
    if link_id == "": 
        retcode,res = submod.execcmd("init_%s" % (link_type),adapter_addr)
        if (retcode == 0):
            submod.setres(0,"ca_sy527: Error initializing TCP/serial link <- %s" % (res))
            return
        link_id = res 
        if link_type == "serial":
            retcode,res = submod.execcmd("setattr_%s" % (link_type),link_id,"9600","8","N","1")
            if (retcode == 0):
                retcode2,res2 = submod.execcmd("deinit_%s" % (link_type),link_id)
                submod.setres(0,"ca_sy527: Error setting up attributes of serial link <- %s: %s" % (res,res2))
                return
    for i in range(3):
        retcode,res = submod.execcmd("write_%s" % (link_type),link_id,"Q")
        if (retcode == 0):
            submod.setres(0,"ca_sy527: Error writing to TCP/serial link <- %s" % (res))
            return
        retcode,res = submod.execcmd("expect_%s" % (link_type),link_id,"###", "2")
        if (retcode == 1):
            break;
    if (retcode == 0):
        retcode2,res2 = submod.execcmd("deinit_%s" % (link_type),link_id)
        submod.setres(0,"ca_sy527: Error initializing ca_sy527 PS <- %s: %s" % (res,res2))
        return
    else:
        retcode,res = submod.execcmd("write_%s" % (link_type),link_id,"DD")
        if (retcode == 0):
            submod.setres(0,"ca_sy527: Error writing to TCP/serial link <- %s" % (res))
            return
    # Calculate id based on last used
    if len(ca_sy527_pool)>0:
        ca_sy527_id = ca_sy527_pool[-1].id + 1
    else: ca_sy527_id = 0 
    # Create tuple with the link information and add to the pool
    ca_sy527_pool.append(ca_sy527_tuple(ca_sy527_id, link_type, adapter_addr, link_id))
    submod.setres(1,str(ca_sy527_id))

def deinit_ca_sy527(ca_sy527_id):
    "Deinitialize and deregister ca_sy527 power supply from the pool."
    global ca_sy527_pool
    # Look for id in pool
    for ca_sy527 in ca_sy527_pool:
        if ca_sy527.id == int(ca_sy527_id): break
    if len(ca_sy527_pool)==0 or ca_sy527.id != int(ca_sy527_id):
        submod.setres(0,"ca_sy527: ca_sy527_id %s has not been found in the pool" % (ca_sy527_id))
        return
    retcode,res = submod.execcmd("deinit_%s" % (ca_sy527.link_type),ca_sy527.link_id)
    if (retcode == 0):
        submod.setres(0,"ca_sy527: Error deinitializing TCP/serial link <- %s" % (res))
        return
    else:
        # Remove ca_sy527 from the pool
        ca_sy527_pool.remove(ca_sy527)
        submod.setres(1,"Power supply ca_sy527 successfully deinitialized")

def set_voltage_ca_sy527(ca_sy527_id, voltage, channel, slew_rate="undef"):
    """Set voltage in Volts. channel is a slash-separated string like page/channel, with
    0<=page<=10 and 0<=channel<=15"""
    global ca_sy527_pool
    # Look for id in pool
    for ca_sy527 in ca_sy527_pool:
        if ca_sy527.id == int(ca_sy527_id): break
    if len(ca_sy527_pool)==0 or ca_sy527.id != int(ca_sy527_id):
        submod.setres(0,"ca_sy527: ca_sy527_id %s has not been found in the pool" % (ca_sy527_id))
        return
    if voltage != "undef" and channel != "undef":
        # Verify consistency of parameters
        voltage = round(float(voltage),1)
        page,channel = channel.split("/",1)
        page = int(page)
        channel = int(channel)
        # Seek page/channel
        retcode,res = seek_page_channel(ca_sy527,page,channel)
        if (retcode == 0):
            submod.setres(0,"ca_sy527: Error selecting page/channel : %s" % (res))
            return
        # Convert channel to VT100 terminal row
        channel += 5
        # Go to -More- page and set ramp
        if slew_rate == "undef": slew_rate = 500
        else: slew_rate = int(slew_rate)
        retcode,res = submod.execcmd("write_%s" % (ca_sy527.link_type),ca_sy527.link_id,"M")
        if (retcode == 0):
            submod.setres(0,"ca_sy527: Error writing to TCP/serial link <- %s" % (res))
            return
        # Go right twice, to Rup then right again to Rdwn
        retcode,res = submod.execcmd("write_%s" % (ca_sy527.link_type),ca_sy527.link_id,r"\x1b[C")
        if (retcode == 0):
            submod.setres(0,"ca_sy527: Error writing to TCP/serial link <- %s" % (res))
            return
        column = 20
        for i in range(2):
            retcode,res = submod.execcmd("write_%s" % (ca_sy527.link_type),ca_sy527.link_id,r"\x1b[C")
            if (retcode == 0):
                submod.setres(0,"ca_sy527: Error writing to TCP/serial link <- %s" % (res))
                return
            # Set slew_rate (Rup and Rdwn)
            retcode,res = submod.execcmd("write_%s" % (ca_sy527.link_type),ca_sy527.link_id,r"%d\r" % slew_rate)
            if (retcode == 0):
                submod.setres(0,"ca_sy527: Error writing to TCP/serial link <- %s" % (res))
                return
            retcode,res = submod.execcmd("expect_%s" % (ca_sy527.link_type),ca_sy527.link_id,r"\x1b[%d;%dH\x1b[7m %03d" % (channel,column,slew_rate), "7")
            if (retcode == 0):
                submod.setres(0,"ca_sy527: Error checking operations's (Ramp) result <- %s" % (res))
                return
            column += 5
        retcode,res = submod.execcmd("write_%s" % (ca_sy527.link_type),ca_sy527.link_id,"M")
        if (retcode == 0):
            submod.setres(0,"ca_sy527: Error writing to TCP/serial link <- %s" % (res))
            return
        # Go right to V0set
        retcode,res = submod.execcmd("write_%s" % (ca_sy527.link_type),ca_sy527.link_id,r"\x1b[C")
        if (retcode == 0):
            submod.setres(0,"ca_sy527: Error writing to TCP/serial link <- %s" % (res))
            return
        retcode,res = submod.execcmd("write_%s" % (ca_sy527.link_type),ca_sy527.link_id,r"%.1f\r" % voltage)
        if (retcode == 0):
            submod.setres(0,"ca_sy527: Error writing to TCP/serial link <- %s" % (res))
            return
        column = 41 # voltage column
        retcode,res = submod.execcmd("expect_%s" % (ca_sy527.link_type),ca_sy527.link_id,r"\x1b[%d;%dH\x1b[7m %06.1f" % (channel,column,voltage), "7")
        if (retcode == 0):
            submod.setres(0,"ca_sy527: Error checking operations's (Voltage) result <- %s" % (res))
            return
    submod.setres(1,"ok")

def set_current_ca_sy527(ca_sy527_id, current, channel):
    """Set current in Ampers. channel is a slash-separated string like page/channel, with
    0<=page<=10 and 0<=channel<=15"""
    global ca_sy527_pool
    # Look for id in pool
    for ca_sy527 in ca_sy527_pool:
        if ca_sy527.id == int(ca_sy527_id): break
    if len(ca_sy527_pool)==0 or ca_sy527.id != int(ca_sy527_id):
        submod.setres(0,"ca_sy527: ca_sy527_id %s has not been found in the pool" % (ca_sy527_id))
        return
    if current != "undef" and channel != "undef":
        # Verify consistency of parameters
        current = int(round(float(current)*1e6))
        page,channel = channel.split("/",1)
        page = int(page)
        channel = int(channel)
        # Seek page/channel
        retcode,res = seek_page_channel(ca_sy527,page,channel)
        if (retcode == 0):
            submod.setres(0,"ca_sy527: Error selecting page/channel : %s" % (res))
            return
        # Convert channel to VT100 terminal row
        channel += 5
        # Go right twice
        for i in range(2):
            retcode,res = submod.execcmd("write_%s" % (ca_sy527.link_type),ca_sy527.link_id,r"\x1b[C")
            if (retcode == 0):
                submod.setres(0,"ca_sy527: Error writing to TCP/serial link <- %s" % (res))
                return
        retcode,res = submod.execcmd("write_%s" % (ca_sy527.link_type),ca_sy527.link_id,r"%d\r" % current)
        if (retcode == 0):
            submod.setres(0,"ca_sy527: Error writing to TCP/serial link <- %s" % (res))
            return
        column = 50 # current column
        retcode,res = submod.execcmd("expect_%s" % (ca_sy527.link_type),ca_sy527.link_id,r"\x1b[%d;%dH\x1b[7m %04d" % (channel,column,current), "7")
        if (retcode == 0):
            submod.setres(0,"ca_sy527: Error checking operations's (Current) result <- %s" % (res))
            return
    submod.setres(1,"ok")

def get_voltage_ca_sy527(ca_sy527_id, channel):
    """Get voltage in Volts. channel is a slash-separated string like page/channel, with
    0<=page<=10 and 0<=channel<=15"""
    retcode,res = get_voltage_current("voltage",ca_sy527_id,channel)
    if (retcode==0):
        submod.setres(retcode,"ca_sy527: %s" % (res))
    else:
        submod.setres(retcode,res)

def get_current_ca_sy527(ca_sy527_id, channel):
    """Get current in Ampers. channel is a slash-separated string like page/channel, with
    0<=page<=10 and 0<=channel<=15"""
    retcode,res = get_voltage_current("current",ca_sy527_id,channel)
    if (retcode==0):
        submod.setres(retcode,"ca_sy527: %s" % (res))
    else:
        submod.setres(retcode,res)

def get_voltage_current(mode, ca_sy527_id, channel):
    global ca_sy527_pool
    global read_delay
    # Look for id in pool
    for ca_sy527 in ca_sy527_pool:
        if ca_sy527.id == int(ca_sy527_id): break
    if len(ca_sy527_pool)==0 or ca_sy527.id != int(ca_sy527_id):
        return 0,"ca_sy527_id %s has not been found in the pool" % (ca_sy527_id)
    # Verify consistency of parameters
    page,channel = channel.split("/",1)
    page = int(page)
    channel = int(channel)
    # Seek page/channel
    retcode,res = seek_page_channel(ca_sy527,page,channel)
    if (retcode == 0): return 0,"Error selecting page/channel : %s" % (res)
    # Convert channel to VT100 terminal row
    channel += 5
    column = 1 # voltage column
    retcode,res = submod.execcmd("write_%s" % (ca_sy527.link_type),ca_sy527.link_id,r"U")
    if (retcode == 0): return 0,"Error writing to TCP/serial link <- %s" % (res)
    res = ""
    i = 0
    while (len(str(res)) < 80 and i<3):
        retcode,res = submod.execcmd("expect_%s" % (ca_sy527.link_type),ca_sy527.link_id,r"\x1b[%d;%dH" % (channel,column), "7")
        if (retcode == 0): return 0,"Error while getting voltage <- %s" % (res)
        sleep(read_delay*4)
        retcode,res = submod.execcmd("read_%s" % (ca_sy527.link_type),ca_sy527.link_id,"81", "7")
        if (retcode == 0): return 0,"Error while getting voltage <- %s" % (res)
        i += 1
    if mode == "voltage":
        value = float(res[20:27])
    elif mode == "current":
        value = float(res[29:36])*1e-6
    else: return 0,"Incorrect get mode"
    return 1,str(value)

def set_voltage_limit_ca_sy527(ca_sy527_id, voltage_limit, channel):
    """Set voltage limit (SVMax) in Volts. channel is a slash-separated string like page/channel, with
    0<=page<=10 and 0<=channel<=15"""
    global ca_sy527_pool
    # Look for id in pool
    for ca_sy527 in ca_sy527_pool:
        if ca_sy527.id == int(ca_sy527_id): break
    if len(ca_sy527_pool)==0 or ca_sy527.id != int(ca_sy527_id):
        submod.setres(0,"ca_sy527: ca_sy527_id %s has not been found in the pool" % (ca_sy527_id))
        return
    if voltage_limit != "undef" and channel != "undef":
        # Verify consistency of parameters
        voltage_limit = int(round(float(voltage_limit)))
        page,channel = channel.split("/",1)
        page = int(page)
        channel = int(channel)
        # Seek page/channel
        retcode,res = seek_page_channel(ca_sy527,page,channel)
        if (retcode == 0):
            submod.setres(0,"ca_sy527: Error selecting page/channel : %s" % (res))
            return
        # Convert channel to VT100 terminal row
        channel += 5
        # Go to -More- page
        retcode,res = submod.execcmd("write_%s" % (ca_sy527.link_type),ca_sy527.link_id,"M")
        if (retcode == 0):
            submod.setres(0,"ca_sy527: Error writing to TCP/serial link <- %s" % (res))
            return
        # Go right once, to SVMax
        retcode,res = submod.execcmd("write_%s" % (ca_sy527.link_type),ca_sy527.link_id,r"\x1b[C")
        if (retcode == 0):
            submod.setres(0,"ca_sy527: Error writing to TCP/serial link <- %s" % (res))
            return
        column = 14
        # Set voltage limit (SVMax)
        retcode,res = submod.execcmd("write_%s" % (ca_sy527.link_type),ca_sy527.link_id,r"%d\r" % voltage_limit)
        if (retcode == 0):
            submod.setres(0,"ca_sy527: Error writing to TCP/serial link <- %s" % (res))
            return
        retcode,res = submod.execcmd("expect_%s" % (ca_sy527.link_type),ca_sy527.link_id,r"\x1b[%d;%dH\x1b[7m %04d" % (channel,column,voltage_limit), "7")
        if (retcode == 0):
            submod.setres(0,"ca_sy527: Error checking operations's (Voltage limit) result <- %s" % (res))
            return
        retcode,res = submod.execcmd("write_%s" % (ca_sy527.link_type),ca_sy527.link_id,"M")
        if (retcode == 0):
            submod.setres(0,"ca_sy527: Error writing to TCP/serial link <- %s" % (res))
            return
    submod.setres(1,"ok")

def set_current_limit_ca_sy527(ca_sy527_id, current_limit, channel):
    """Set current in Ampers and trip to 100ms. channel is a slash-separated string like page/channel, with
    0<=page<=10 and 0<=channel<=15"""
    global ca_sy527_pool
    # Look for id in pool
    for ca_sy527 in ca_sy527_pool:
        if ca_sy527.id == int(ca_sy527_id): break
    if len(ca_sy527_pool)==0 or ca_sy527.id != int(ca_sy527_id):
        submod.setres(0,"ca_sy527: ca_sy527_id %s has not been found in the pool" % (ca_sy527_id))
        return
    if current_limit != "undef" and channel != "undef":
        # Verify consistency of parameters
        current_limit = int(round(float(current_limit)*1e6))
        trip = 1.0 # (100ms)
        page,channel = channel.split("/",1)
        page = int(page)
        channel = int(channel)
        # Seek page/channel
        retcode,res = seek_page_channel(ca_sy527,page,channel)
        if (retcode == 0):
            submod.setres(0,"ca_sy527: Error selecting page/channel : %s" % (res))
            return
        # Convert channel to VT100 terminal row
        channel += 5
        # Go right twice
        for i in range(2):
            retcode,res = submod.execcmd("write_%s" % (ca_sy527.link_type),ca_sy527.link_id,r"\x1b[C")
            if (retcode == 0):
                submod.setres(0,"ca_sy527: Error writing to TCP/serial link <- %s" % (res))
                return
        retcode,res = submod.execcmd("write_%s" % (ca_sy527.link_type),ca_sy527.link_id,r"%d\r" % current_limit)
        if (retcode == 0):
            submod.setres(0,"ca_sy527: Error writing to TCP/serial link <- %s" % (res))
            return
        column = 50 # current column
        retcode,res = submod.execcmd("expect_%s" % (ca_sy527.link_type),ca_sy527.link_id,r"\x1b[%d;%dH\x1b[7m %04d" % (channel,column,current_limit), "7")
        if (retcode == 0):
            submod.setres(0,"ca_sy527: Error checking operations's (Current limit) result <- %s" % (res))
            return
        # Go to -More- page
        retcode,res = submod.execcmd("write_%s" % (ca_sy527.link_type),ca_sy527.link_id,"M")
        if (retcode == 0):
            submod.setres(0,"ca_sy527: Error writing to TCP/serial link <- %s" % (res))
            return
        # Go right 4 times, to Trip
        column = 30
        for i in range(4):
            retcode,res = submod.execcmd("write_%s" % (ca_sy527.link_type),ca_sy527.link_id,r"\x1b[C")
            if (retcode == 0):
                submod.setres(0,"ca_sy527: Error writing to TCP/serial link <- %s" % (res))
                return
        # Set Trip
        retcode,res = submod.execcmd("write_%s" % (ca_sy527.link_type),ca_sy527.link_id,r"%.1f\r" % trip)
        if (retcode == 0):
            submod.setres(0,"ca_sy527: Error writing to TCP/serial link <- %s" % (res))
            return
        retcode,res = submod.execcmd("expect_%s" % (ca_sy527.link_type),ca_sy527.link_id,r"\x1b[%d;%dH\x1b[7m %05.1f" % (channel,column,trip), "7")
        if (retcode == 0):
            submod.setres(0,"ca_sy527: Error checking operations's (Trip) result <- %s" % (res))
            return
        retcode,res = submod.execcmd("write_%s" % (ca_sy527.link_type),ca_sy527.link_id,"M")
        if (retcode == 0):
            submod.setres(0,"ca_sy527: Error writing to TCP/serial link <- %s" % (res))
            return
    submod.setres(1,"ok")

def power_on_ca_sy527(ca_sy527_id, channel):
    """Turn on channel. channel is a slash-separated string like page/channel, with
    0<=page<=10 and 0<=channel<=15"""
    global ca_sy527_pool
    global read_delay
    # Look for id in pool
    for ca_sy527 in ca_sy527_pool:
        if ca_sy527.id == int(ca_sy527_id): break
    if len(ca_sy527_pool)==0 or ca_sy527.id != int(ca_sy527_id):
        submod.setres(0,"ca_sy527: ca_sy527_id %s has not been found in the pool" % (ca_sy527_id))
        return
    # Verify consistency of parameters
    page,channel = channel.split("/",1)
    page = int(page)
    channel = int(channel)
    # Seek page/channel
    retcode,res = seek_page_channel(ca_sy527,page,channel)
    if (retcode == 0):
        submod.setres(0,"ca_sy527: Error selecting page/channel : %s" % (res))
        return
    # Convert channel to VT100 terminal row
    channel += 5
    # Go right three times
    for i in range(3):
        retcode,res = submod.execcmd("write_%s" % (ca_sy527.link_type),ca_sy527.link_id,r"\x1b[C")
        if (retcode == 0):
            submod.setres(0,"ca_sy527: Error writing to TCP/serial link <- %s" % (res))
            return
    column = 62 # power column
    retcode,res = submod.execcmd("expect_%s" % (ca_sy527.link_type),ca_sy527.link_id,r"\x1b[%d;%dH\x1b[7m " % (channel,column), "7")
    if (retcode == 0):
        submod.setres(0,"ca_sy527: Error checking PS status <- %s" % (res))
        return
    sleep(read_delay)
    retcode,res = submod.execcmd("read_%s" % (ca_sy527.link_type),ca_sy527.link_id,"3", "7")
    if (retcode == 0):
        submod.setres(0,"ca_sy527: Error checking PS status <- %s" % (res))
        return
    if res == "Off":
        # Change status
        retcode,res = submod.execcmd("write_%s" % (ca_sy527.link_type),ca_sy527.link_id,"C")
        if (retcode == 0):
            submod.setres(0,"ca_sy527: Error writing to TCP/serial link <- %s" % (res))
            return
        retcode,res = submod.execcmd("expect_%s" % (ca_sy527.link_type),ca_sy527.link_id,r"\x1b[%d;%dH\x1b[7m  On" % (channel,column), "7")
        if (retcode == 0):
            submod.setres(0,"ca_sy527: Error checking the operation's (Power on) result <- %s" % (res))
            return
    submod.setres(1,"Channel successfully powered on")

def power_off_ca_sy527(ca_sy527_id, channel):
    """Turn off channel. channel is a slash-separated string like page/channel, with
    0<=page<=10 and 0<=channel<=15"""
    global ca_sy527_pool
    global read_delay
    # Look for id in pool
    for ca_sy527 in ca_sy527_pool:
        if ca_sy527.id == int(ca_sy527_id): break
    if len(ca_sy527_pool)==0 or ca_sy527.id != int(ca_sy527_id):
        submod.setres(0,"ca_sy527: ca_sy527_id %s has not been found in the pool" % (ca_sy527_id))
        return
    # Verify consistency of parameters
    page,channel = channel.split("/",1)
    page = int(page)
    channel = int(channel)
    # Seek page/channel
    retcode,res = seek_page_channel(ca_sy527,page,channel)
    if (retcode == 0):
        submod.setres(0,"ca_sy527: Error selecting page/channel : %s" % (res))
        return
    # Convert channel to VT100 terminal row
    channel += 5
    # Go right three times
    for i in range(3):
        retcode,res = submod.execcmd("write_%s" % (ca_sy527.link_type),ca_sy527.link_id,r"\x1b[C")
        if (retcode == 0):
            submod.setres(0,"ca_sy527: Error writing to TCP/serial link <- %s" % (res))
            return
    column = 62 # power column
    retcode,res = submod.execcmd("expect_%s" % (ca_sy527.link_type),ca_sy527.link_id,r"\x1b[%d;%dH\x1b[7m " % (channel,column), "7")
    if (retcode == 0):
        submod.setres(0,"ca_sy527: Error checking PS status <- %s" % (res))
        return
    sleep(read_delay)
    retcode,res = submod.execcmd("read_%s" % (ca_sy527.link_type),ca_sy527.link_id,"3", "7")
    if (retcode == 0):
        submod.setres(0,"ca_sy527: Error checking PS status <- %s" % (res))
        return
    if res == " On":
        # Change status
        retcode,res = submod.execcmd("write_%s" % (ca_sy527.link_type),ca_sy527.link_id,"C")
        if (retcode == 0):
            submod.setres(0,"ca_sy527: Error writing to TCP/serial link <- %s" % (res))
            return
        retcode,res = submod.execcmd("expect_%s" % (ca_sy527.link_type),ca_sy527.link_id,r"\x1b[%d;%dH\x1b[7m Off" % (channel,column), "7")
        if (retcode == 0):
            submod.setres(0,"ca_sy527: Error checking the operation's (Power off) result <- %s" % (res))
            return
    submod.setres(1,"Channel successfully powered off")

def seek_page_channel(ca_sy527,page,channel):
    "Goes to page/channel"
    global read_delay
    retcode,res = submod.execcmd("write_%s" % (ca_sy527.link_type),ca_sy527.link_id,"NP")
    if (retcode == 0): return 0,"Error writing to TCP/serial link <- %s" % (res)
    retcode,res = submod.execcmd("expect_%s" % (ca_sy527.link_type),ca_sy527.link_id,"Vmax  ", "7")
    if (retcode == 0): return 0,"Error identifying -More- <- %s" % (res)
    sleep(read_delay)
    retcode,res = submod.execcmd("read_%s" % (ca_sy527.link_type),ca_sy527.link_id,"3")
    if (retcode == 0): return 0,"Error identifying -More- <- %s" % (res)
    if res == "Rup":
        retcode,res = submod.execcmd("write_%s" % (ca_sy527.link_type),ca_sy527.link_id,"M")
        if (retcode == 0): return 0,"Error writing to TCP/serial link <- %s" % (res)
        retcode,res = submod.execcmd("expect_%s" % (ca_sy527.link_type),ca_sy527.link_id,"Vmax  ", "7")
        if (retcode == 0): return 0,"Error identifying -More- <- %s" % (res)
        sleep(read_delay)
        retcode,res = submod.execcmd("read_%s" % (ca_sy527.link_type),ca_sy527.link_id,"3")
        if (retcode == 0): return 0,"Error identifying -More- <- %s" % (res)
    elif res != "  V":
        return 0,"Error identifying -More- <- %s" % (res)
    retcode,res = submod.execcmd("expect_%s" % (ca_sy527.link_type),ca_sy527.link_id,r"\x1b[2;70HPage ","7")
    if (retcode == 0): return 0,"Error identifying present page <- %s" % (res)
    sleep(read_delay)
    retcode,res = submod.execcmd("read_%s" % (ca_sy527.link_type),ca_sy527.link_id,"1")
    if (retcode == 0): return 0,"Error reading to TCP/serial link <- %s" % (res)
    current_page = int(res)
    delta_page = page - current_page
    # Assure reset channel
    for i in range(15):
        retcode,res = submod.execcmd("write_%s" % (ca_sy527.link_type),ca_sy527.link_id,r"\x1b[A")
        if (retcode == 0): return 0,"Error writing to TCP/serial link <- %s" % (res)
    retcode,res = submod.execcmd("expect_%s" % (ca_sy527.link_type),ca_sy527.link_id,r"\x1b[5;1H\x1b[7m", "7")
    if (retcode == 0): return 0,"Error resetting channel <- %s" % (res)
    # Validate page/channel
    if delta_page < 0: page_command = "P"
    else: page_command = "N"
    if abs(delta_page) not in range(10):
        return 0,"page %d out of range" % (page)
    if channel not in range(16):
        return 0,"channel %d out of range" % (channel)
    # Seek page
    if delta_page != 0:
        for i in range(abs(delta_page)):
            # Go to next/previous
            retcode,res = submod.execcmd("write_%s" % (ca_sy527.link_type),ca_sy527.link_id,page_command)
            if (retcode == 0): return 0,"Error writing to TCP/serial link <- %s" % (res)
            retcode,res = submod.execcmd("expect_%s" % (ca_sy527.link_type),ca_sy527.link_id,r"\x1b[2;70HPage %d" % (current_page+copysign(i+1,delta_page)), "7")
            if (retcode == 0): return 0,"Error while seeking page <- %s" % (res)
    # Seek channel
    for i in range(channel):
        # Go down
        retcode,res = submod.execcmd("write_%s" % (ca_sy527.link_type),ca_sy527.link_id,r"\x1b[B")
        if (retcode == 0): return 0,"Error writing to TCP/serial link <- %s" % (res)
        retcode,res = submod.execcmd("expect_%s" % (ca_sy527.link_type),ca_sy527.link_id,r"\x1b[%d;1H\x1b[7m" % (i+1+5), "7")
        if (retcode == 0): return 0,"Error setting channel <- %s" % (res)
    return 1,""
