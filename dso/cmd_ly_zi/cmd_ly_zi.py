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

from re import sub,search
import getapi,pools,vicp

ly_zi_pool = pools.pool()

# Available channels
valid_channels = ["M1","M2","M3","M4","C1","C2","C3","C4","F1","F2","F3","F4","F5","F6","F7","F8"]

# Put serialized API in memory if not called via import
if __name__ == '__main__':
    global api; api = getapi.load_api(__file__)

# Functions
def getapi_ly_zi():
    submod.setres(1,api)

def init_ly_zi(dso_hostname):
    """Initialize ly_zi DSO. *dso_hostname* is the IP address or resolvable network name

    Returns ly_zi_id"""
    # Initialize TCP link
    link = vicp.device()
    link.deviceAddress = dso_hostname
    if not link.connect():
        submod.setres(0,"ly_zi: Error initializing TCP link <- %s" % (link.LastErrorMsg))
        return
    # Turn on error logging
    if not link.write("CHLP EO\n",True,True):
        link.disconnect()
        submod.setres(0,"ly_zi: Error setting up error logging <- VICP error")
        return
    # Flush error queue
    retcode,res = get_error_queue(link)
    if retcode == 0:
        submod.setres(0,"ly_zi: %s" % (res))
        return
    # Turn on headers in responses
    if not link.write("CHDR SHORT\n"):
        submod.setres(0,"ly_zi: Error turning on headers in responses")
        return
    # Set datapoints to be recovered
    if not link.write("WFSU SP,0,NP,0,SN,0,FP,0\n"):
        submod.setres(0,"ly_zi: Error setting up waveform")
        return
    ly_zi_id=ly_zi_pool.new({"link":link})
    submod.setres(1,ly_zi_id)

def deinit_ly_zi(ly_zi_id):
    "Deregister an ly_zi from the pool"
    try:
        ly_zi = ly_zi_pool.get(ly_zi_id)
    except Exception as e:
        submod.setres(1,"ly_zi: ly_zi_%s" % (str(e)))
        return
    # Deinitialize TCP link
    if not ly_zi["link"].disconnect():
        submod.setres(0,"ly_zi: Error deinitializing TCP link %s <- %s" % (ly_zi["link"].LastErrorMsg))
        return
    # Remove ly_zi from the pool
    ly_zi_pool.remove(ly_zi_id)
    submod.setres(1,"ok")

def get_data_ly_zi(ly_zi_id,acq_stream,sparsing,channel):
    """Get waveform of *channel*. *channel* can be 'C1', 'C2', 'C3', 'C4', 'M1', 'M2', 'M3', 'M4', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7' or 'F8', or a comma-separated list of channels. e.g.: C1,C2,F3. Data is sent to *acq_stream* of the acquisition chain. The *sparsing* parameter defines the interval between data points. *sparsing* =4 gets every 4th datapoint."""
    try:
        ly_zi = ly_zi_pool.get(ly_zi_id)
    except Exception as e:
        submod.setres(0,"ly_zi: ly_zi_%s" % (str(e)))
        return
    # Expand channels
    channels = list(set(channel.split(",")))
    # Verify consistency of parameters
    for channel in channels:
        if channel not in valid_channels:
            submod.setres(0,"ly_zi: invalid channel %d" % (channel))
            return
    # Send the command
    if not ly_zi["link"].write("",True,True):
        submod.setres(0,"ly_zi: Error flushing queue <- VICP Error")
        return
    if not ly_zi["link"].write("*CLS; INE 1; *SRE 1\n"):
        submod.setres(0,"ly_zi: Error asking for SRQ <- VICP Error")
        return
    retcode,res = ly_zi["link"].serialPoll()
    if retcode == 1 and res == '1':
        wavedesc_total = ""
        for channel in channels:
            # Turn off headers in responses
            if not ly_zi["link"].write("CHDR OFF\n"):
                submod.setres(0,"ly_zi: Error turning off headers in responses <- VICP Error")
                return
            # Set datapoints to be recovered
            if not ly_zi["link"].write("WFSU SP,{0},NP,0,SN,0,FP,0\n".format(sparsing)):
                submod.setres(0,"ly_zi: Error setting up waveform <- VICP Error")
                return
            # Get waveform
            retcode,res = ly_zi["link"].wrnrd("{0}:INSP? \"SIMPLE\",FLOAT\n".format(channel))
            if retcode == 0:
                submod.setres(0,"ly_zi: Error getting the data <- %s" % (res))
                return
            # Clean up
            wave = sub(r'[ \n\r]+','\n',res).strip("\"\n")
            # Get wave descriptor
            retcode,res = ly_zi["link"].wrnrd("{0}:INSP? \"WAVEDESC\"\n".format(channel))
            if retcode == 0:
                submod.setres(0,"ly_zi: Error getting the vertical scale <- %s" % (res))
                return
            wavedesc = res
            wavedesc_total += wavedesc
            print(wavedesc)
            # Extract horizontal step
            h_step = float(search(r"HORIZ_INTERVAL *: ([0-9\.e+-]+)",wavedesc).expand(r"\1"))
            # Extract horizontal offset
            h_offset = float(search(r"HORIZ_OFFSET *: ([0-9\.e+-]+)",wavedesc).expand(r"\1"))
            # Extract sparsing factor
            sparsing = float(search(r"SPARSING_FACTOR *: ([0-9\.e+-]+)",wavedesc).expand(r"\1"))
            # Turn on headers in responses again
            if not ly_zi["link"].write("CHDR SHORT\n"):
                submod.setres(0,"ly_zi: Error turning on headers in responses <- VICP error")
                return
            # Rescale and add abscises
            x = 0
            y = 0
            output = ""
            wave = wave.split("\n")
            for i in range(len(wave)):
                x = i*h_step*sparsing + h_offset
                y = float(wave[i])
                output += "{0} {1}\n".format(x,y)
            # Encode for inject_data_acq
            # max packet size:
            # 4096 minus nul-byte is the buffer size of the acquisition chain
            # 20 is <cmd name=""></cmd>\n
            # 15 is inject_data_acq
            # 15 is <param></param>
            # we reserve len(str(2**32))=10 for acq_stream
            # and another 10 character for margin for the last character
            # (up to 4 characters) and to cover our asses...
            max_pkt_s = 4095 - 20 - 15 - 15*2 - 10 - 10
            packet = ""
            for i in range(len(output)):
                packet += str(ord(output[i])) + ","
                if len(packet)>=max_pkt_s or i==len(output)-1:
                    retcode,res = submod.execcmd("inject_data_acq",acq_stream,packet.rstrip(","))
                    if retcode == 0:
                        submod.setres(0,"ly_zi: Error injecting data in the acquisition chain <- %s"%res)
                        return
                    packet = ""
            # Separate channels with two newlines
            retcode,res = submod.execcmd("inject_data_acq",acq_stream,"10,10")
            if retcode == 0:
                submod.setres(0,"ly_zi: Error injecting data in the acquisition chain <- %s"%res)
                return
        wavedesc_total = wavedesc_total.strip("\"").strip().replace("\r\n",";").strip(";").strip()
        submod.setres(1,wavedesc_total)
        return
    submod.setres(0,"ly_zi: Error getting ready state from DSO (serialPoll) <- %s" % (ly_zi["link"].LastErrorMsg))

def set_v_offset_ly_zi(ly_zi_id,v_offset,channel):
    "Set *v_offset* vertical offset for *channel*"
    try:
        ly_zi = ly_zi_pool.get(ly_zi_id)
    except Exception as e:
        submod.setres(0,"ly_zi: ly_zi_%s" % (str(e)))
        return
    # Verify consistency of parameters
    if channel not in valid_channels:
        submod.setres(0,"ly_zi: Error: invalid channel %d" % (channel))
        return
    if not ly_zi["link"].write("%s:OFST %f\n"%(channel,float(v_offset))):
        submod.setres(0,"ly_zi: Error setting vertical offset <- %s" % (res))
        return
    submod.setres(1,"ok")

def set_v_div_ly_zi(ly_zi_id,v_div,channel):
    "Set *v_div* vertical volts per division for *channel*"
    try:
        ly_zi = ly_zi_pool.get(ly_zi_id)
    except Exception as e:
        submod.setres(0,"ly_zi: ly_zi_%s" % (str(e)))
        return
    # Verify consistency of parameters
    if channel not in valid_channels:
        submod.setres(0,"ly_zi: invalid channel %d" % (channel))
        return
    print("%s:VDIV %f\n"%(channel,float(v_div)))
    if not ly_zi["link"].write("%s:VDIV %f\n" % (channel,float(v_div))):
        submod.setres(0,"ly_zi: Error setting vertical volts per division <- %s" % (res))
        return
    submod.setres(1,"ok")

def clear_sweep_ly_zi(ly_zi_id):
    "Clear sweep on DSO"
    try:
        ly_zi = ly_zi_pool.get(ly_zi_id)
    except Exception as e:
        submod.setres(0,"ly_zi: ly_zi_%s" % (str(e)))
        return
    if not ly_zi["link"].write("CLSW\n"):
        submod.setres(0,"ly_zi: Error clearing sweep <- %s" % (res))
        return
    submod.setres(1,"ok")

def get_error_queue_ly_zi(ly_zi_id):
    "Read error queue"
    try:
        ly_zi = ly_zi_pool.get(ly_zi_id)
    except Exception as e:
        submod.setres(0,"ly_zi: ly_zi_%s" % (str(e)))
        return
    retcode,res=get_error_queue(ly_zi["link"])
    if retcode==0:
        submod.setres(retcode,"ly_zi: %s" % (res))
        return
    submod.setres(1,res)
    
def get_error_queue(link):
    retcode,res = link.wrnrd("CHL? CLR\n")
    res = res.replace("\r\n",";").strip("\r\n")
    if retcode == 0:
        return 0,res
    elif res != "CHL \"\"":
        return 1,res
    else: return 1,""
