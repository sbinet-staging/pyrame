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

ly_lt344_pool = pools.pool()

# Available channels
valid_channels = ["M1","M2","M3","M4","C1","C2","C3","C4","TA","TB","TC","TD"]

# Put serialized API in memory if not called via import
if __name__ == '__main__':
    global api; api = getapi.load_api(__file__)

# Functions
def getapi_ly_lt344():
    submod.setres(1,api)

def init_ly_lt344(dso_hostname):
    """Initialize ly_lt344 DSO. *dso_hostname* is the IP address or resolvable network name

    Returns ly_lt344_id"""
    # Initialize TCP link
    link = vicp.device()
    link.deviceAddress = dso_hostname
    if not link.connect():
        submod.setres(0,"ly_lt344: Error initializing TCP link <- %s" % (link.LastErrorMsg))
        return
    # Turn on error logging
    if not link.write("CHLP EO\n",True,True):
        link.disconnect()
        submod.setres(0,"ly_lt344: Error setting up error logging <- VICP error")
        return
    # Turn on headers in responses
    if not link.write("CHDR SHORT\n"):
        submod.setres(0,"ly_lt344: Error turning on headers in responses <- VICP error")
        return
    ly_lt344_id=ly_lt344_pool.new({"link":link})
    submod.setres(1,ly_lt344_id)

def deinit_ly_lt344(ly_lt344_id):
    "Deregister an ly_lt344 from the pool"
    try:
        ly_lt344 = ly_lt344_pool.get(ly_lt344_id)
    except Exception as e:
        submod.setres(1,"ly_lt344: ly_lt344_%s" % (str(e)))
        return
    # Deinitialize TCP link
    if not ly_lt344["link"].disconnect():
        submod.setres(0,"ly_lt344: Error deinitializing TCP link %s <- VICP error" % (ly_lt344["link"].LastErrorMsg))
        return
    # Remove ly_lt344 from the pool
    ly_lt344_pool.remove(ly_lt344_id)
    submod.setres(1,"ok")

def get_data_ly_lt344(ly_lt344_id,acq_stream,sparsing,channel):
    """Get waveform of *channel*. *channel* can be 'C1', 'C2', 'C3', 'C4', 'M1', 'M2', 'M3', 'M4', 'TA', 'TB', 'TC' or 'TD', or a comma-separated list of channels. e.g.: C1,C2,TA. Data is sent to *acq_stream* of the acquisition chain. The *sparsing* parameter defines the interval between data points. *sparsing* =4 gets every 4th datapoint."""
    try:
        ly_lt344 = ly_lt344_pool.get(ly_lt344_id)
    except Exception as e:
        submod.setres(0,"ly_lt344: ly_lt344_%s" % (str(e)))
        return
    # Expand channels
    channels = list(set(channel.split(",")))
    # Verify consistency of parameters
    for channel in channels:
        if channel not in valid_channels:
            submod.setres(0,"ly_lt344: invalid channel %d"%(channel))
            return
    # Send the command
    if not ly_lt344["link"].write("",True,True):
        submod.setres(0,"ly_lt344: Error flushing queue <- VICP error")
        return
    if not ly_lt344["link"].write("*CLS; INE 1; *SRE 1\n"):
        submod.setres(0,"ly_lt344: Error asking for SRQ <- VICP error")
        return
    retcode,res = ly_lt344["link"].serialPoll()
    if retcode == 1 and res == '1':
        for channel in channels:
            # Turn off headers in responses
            if not ly_lt344["link"].write("CHDR OFF\n"):
                submod.setres(0,"ly_lt344: Error turning off headers in responses <- VICP error")
                return
            # Set datapoints to be recovered
            if not ly_lt344["link"].write("WFSU SP,{0},NP,0,SN,0,FP,0\n".format(sparsing)):
                submod.setres(0,"ly_lt344: Error turning off headers in responses <- VICP error")
                return
            # Get waveform
            retcode,res = ly_lt344["link"].wrnrd("{0}:INSP? \"SIMPLE\",FLOAT\n".format(channel))
            if retcode == 0:
                submod.setres(0,"ly_lt344: Error getting the data <- %s" % (res))
                return
            # Clean up
            wave = sub(r'[ \n\r]+','\n',res).strip("\"\n")
            # Get wave descriptor
            retcode,res = ly_lt344["link"].wrnrd("{0}:INSP? \"WAVEDESC\"\n".format(channel))
            if retcode == 0:
                submod.setres(0,"ly_lt344: Error getting the vertical scale <- %s" % (res))
                return
            wavedesc = res
            # Extract vertical gain
            v_gain = float(search(r"VERTICAL_GAIN *: *([0-9\.e+-]+)",wavedesc).expand(r"\1"))
            # Extract vertical offset
            v_offset = float(search(r"VERTICAL_OFFSET *: *([0-9\.e+-]+)",wavedesc).expand(r"\1"))
            # Extract horizontal step
            h_step = float(search(r"HORIZ_INTERVAL *: *([0-9\.e+-]+)",wavedesc).expand(r"\1"))
            # Extract horizontal offset
            h_offset = float(search(r"HORIZ_OFFSET *: *([0-9\.e+-]+)",wavedesc).expand(r"\1"))
            # Extract sparsing factor
            sparsing = float(search(r"SPARSING_FACTOR *: *([0-9\.e+-]+)",wavedesc).expand(r"\1"))
            # Turn on headers in responses again
            if not ly_lt344["link"].write("CHDR SHORT\n"):
                submod.setres(0,"ly_lt344: Error turning on headers in responses <- VICP error")
                return
            # Rescale and add abscises
            x = 0
            y = 0
            output = ""
            wave = wave.split("\n")
            for i in range(len(wave)):
                x = i*h_step*sparsing + h_offset
                y = float(wave[i])
                #y = float(wave[i])*v_gain - v_offset
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
                        submod.setres(0,"ly_lt344: Error injecting data in the acquisition chain <- %s" % (res))
                        return
                    packet = ""
            # Separate channels with two newlines
            retcode,res = submod.execcmd("inject_data_acq",acq_stream,"10,10")
            if retcode == 0:
                submod.setres(0,"ly_lt344: Error injecting data in the acquisition chain <- %s" % (res))
                return
        submod.setres(1,"")
        return
    submod.setres(0,"ly_lt344: Error getting ready state from DSO (serialPoll) <- %s" % (ly_lt344["link"].LastErrorMsg))

def clear_sweep_ly_lt344(ly_lt344_id):
    "Clear sweep on DSO"
    try:
        ly_lt344 = ly_lt344_pool.get(ly_lt344_id)
    except Exception as e:
        submod.setres(0,"ly_lt344: ly_lt344_%s" % (str(e)))
        return
    if not ly_lt344["link"].write("CLSW\n"):
        submod.setres(0,"ly_lt344: Error clearing sweep <- %s" % (res))
        return
    submod.setres(1,"ok")

def get_error_queue_ly_lt344(ly_lt344_id):
    "Read error queue"
    try:
        ly_lt344 = ly_lt344_pool.get(ly_lt344_id)
    except Exception as e:
        submod.setres(0,"ly_lt344: ly_lt344_%s" % (str(e)))
        return
    retcode,res=get_error_queue(ly_lt344["link"])
    if retcode==0:
        submod.setres(retcode,"ly_lt344: %s" % (res))
        return
    submod.setres(1,res)
    
def get_error_queue(link):
    retcode,res = link.wrnrd("CHL? CLR\n")
    return retcode,res.replace("\n","").replace("\r","")
