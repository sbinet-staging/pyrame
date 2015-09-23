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

import pools, getapi, conf_strings

import struct
from time import sleep

# UTILITIES ######################################################

def decode_string(string):
    return string.decode("hex")
def encode_string(string):
    return string.encode("hex")
def decode_byte(string): # unsigned 8 bits
    return struct.unpack("<B",string.decode("hex"))[0]
def encode_byte(integer): # unsigned 8 bits
    return struct.pack("<B",integer).encode("hex")
def decode_word(string): # unsigned 16 bits
    return struct.unpack("<H",string.decode("hex"))[0]
def encode_word(integer): # unsigned 16 bits
    return struct.pack("<H",integer).encode("hex")
def decode_short(string): # signed 16 bits
    return struct.unpack("<h",string.decode("hex"))[0]
def decode_dword(string): # unsigned 32 bits
    return struct.unpack("<I",string.decode("hex"))[0]
def decode_long(string): # signed 32 bits
    return struct.unpack("<i",string.decode("hex"))[0]
def encode_long(integer): # signed 32 bits
    return struct.pack("<i",integer).encode("hex")

# TH_APT #########################################################

class th_apt(object):
    def __init__(self):
        self.th_apt_pool = pools.pool()

    class th_apt_Exception(Exception):
        pass

    # correspondance of messages and codes
    cmds_code = {
        "MGMSG_HW_NO_FLASH_PROGRAMMING": 0x0018,
        "MGMSG_HW_STOP_UPDATEMSGS": 0x0012,
        "MGMSG_HW_REQ_INFO": 0x0005,
        "MGMSG_HW_GET_INFO": 0x0006,
        "MGMSG_RACK_REQ_BAYUSED": 0x0060,
        "MGMSG_RACK_GET_BAYUSED": 0x0061,
        "MGMSG_MOD_SET_CHANENABLESTATE": 0x0210,
        "MGMSG_MOT_SET_LIMSWITCHPARAMS": 0x0423,
        "MGMSG_MOT_REQ_STATUSUPDATE": 0x0480,
        "MGMSG_MOT_GET_STATUSUPDATE": 0x0481,
        "MGMSG_MOT_SET_HOMEPARAMS": 0x0440,
        "MGMSG_MOT_MOVE_HOME": 0x0443,
        "MGMSG_MOT_MOVE_HOMED": 0x0444,
        "MGMSG_MOT_MOVE_RELATIVE": 0x0448,
        "MGMSG_MOT_MOVE_COMPLETED": 0x0464,
        "MGMSG_MOT_MOVE_STOPPED": 0x0466,
        "MGMSG_MOT_SET_VELPARAMS": 0x0413,
        "MGMSG_MOT_SET_POSCOUNTER": 0x0410,
        "MGMSG_MOT_REQ_POSCOUNTER": 0x0411,
        "MGMSG_MOT_GET_POSCOUNTER": 0x0412,
        "MGMSG_HW_RESPONSE": 0x0080,
        }
    # inverse cmds_code to find command from code
    code_cmds = dict((v,k) for k, v in cmds_code.iteritems())
    # extract data from messages
    def cmd(self,message):
        return decode_word(message[0:4])
    def data_length(self,message):
        return decode_word(message[4:8])
    def param1(self,message):
        return decode_byte(message[4:6])
    def param2(self,message):
        return decode_byte(message[6:8])
    def long_message(self,message):
        return True if ((decode_byte(message[8:10]) & 0x80) << 7) else False
    def source(self,message):
        return decode_byte(message[10:12])
    def message_data(self,message):
        return message[12:]

    BSC2_DRV014={}
    BSC2_DRV014["usteps_per_mm_p"] = 409600
    BSC2_DRV014["usteps_per_mm_v"] = 21987328
    BSC2_DRV014["usteps_per_mm_a"] = 4506
    BSC2_DRV014["limitswitch"] = "0300"
    BSC2_DRV014["need_completed"] = False
    BSC_DRV014={}
    BSC_DRV014["usteps_per_mm_p"] = 25600
    BSC_DRV014["usteps_per_mm_v"] = 25600
    BSC_DRV014["usteps_per_mm_a"] = 25600
    BSC_DRV014["limitswitch"] = "0200"
    BSC_DRV014["need_completed"] = True

    # methods
    def send_message(self,th_apt,cmd,destination,param1=None,param2=None,data=None):
        "Compose a message for the TH_APT controller. *cmd* is a string starting with \"MGMSG\". *destination* is an 8-bit integer. Either *param1* and *param2, or *data* must be provided. *param1* and *param2* are 8-bit integers. *data* is string of variable length up to 255 bytes."
        message =  encode_word(self.cmds_code[cmd]) # cmd code
        if param1!=None or param2!=None:
            if param1==None or param2==None:
                return 0,"Both param1 and param2 must be provided to send_message"
            message += encode_byte(param1) # param1
            message += encode_byte(param2) # param2
            message += encode_byte(destination) # destination
            message += "01" # source
        elif data!=None:
            if len(data)>255:
                return 0,"Data is too long at %d bytes. Maximum is 255"%(len(data))
            if len(data)%2!=0:
                return 0,"Data length must be multiple of 2. Now it's %d"%(len(data))
            message += encode_word(len(data)/2) # data length
            message += encode_byte(0x80|destination) # destination
            message += "01" # source
            message += data
        else:
            return 0,"Incorrect number of parameters for compose"
        retcode,res = submod.execcmd("write_bin_"+th_apt["bus"],th_apt["bus_id"],message)
        if retcode==0:
            return 0,"Error writing <- %s" % (res)
        return 1,"ok"
    
    def recv_message(self,th_apt):
        retcode,res = submod.execcmd("read_bin_"+th_apt["bus"],th_apt["bus_id"],"6")
        if retcode==0:
            return 0,"Error reading <- %s" % (res)
        message = res
        if self.code_cmds[self.cmd(message)]=="MGMSG_HW_RESPONSE":
            return 0,"Please, power cycle the Thorlabs controller"
        if self.long_message(message):
            retcode,res = submod.execcmd("read_bin_"+th_apt["bus"],th_apt["bus_id"],str(self.data_length(message)))
            if retcode==0:
                return 0,"Error reading further <- %s" % (res)
            message += res
        return 1,message

    def get_statusupdate(self,th_apt):
        retcode,res = self.send_message(th_apt,"MGMSG_MOT_REQ_STATUSUPDATE",th_apt["chan_addr"],param1=1,param2=0)
        if retcode==0:
            raise self.th_apt_Exception((0,"Error asking for status update: %s" % (res)))
        retcode,res = self.recv_message(th_apt)
        if retcode==0:
            raise self.th_apt_Exception((0,"Error getting status update: %s" % (res)))
        message = res
        res = {}
        res["completed"] = False
        if self.code_cmds[self.cmd(message)]!="MGMSG_MOT_GET_STATUSUPDATE":
            if th_apt["need_completed"] and self.code_cmds[self.cmd(message)] in ["MGMSG_MOT_MOVE_COMPLETED","MGMSG_MOT_MOVE_STOPPED","MGMSG_MOT_MOVE_HOMED"]:
                res["completed"] = True
            _,message = self.recv_message(th_apt)
            if self.code_cmds[self.cmd(message)]!="MGMSG_MOT_GET_STATUSUPDATE":
                raise self.th_apt_Exception((0,"Error checking status update: wrong message received"))
        res["position"] = decode_long(message[16:24])
        status = decode_dword(message[32:40])
        if (status & 0x0010) << 4 or \
           (status & 0x0020) << 5 or \
           (status & 0x0040) << 6 or \
           (status & 0x0080) << 7:
            res["motion"] = True
        else:
            res["motion"] = False
        res["motion_homing"] = True if (status & 0x0200) << 9 else False
        res["homed"] = True if (status & 0x0400) << 10 else False
        return res

    def init(self,conf_string):
        try:
            conf = conf_strings.parse(conf_string)
        except Exception as e:
            return 0,str(e)
        if conf.name!="th_apt":
            return 0,"Invalid module name %s in conf_string instead of th_apt"%(conf.name)
        if not conf.has("bus","model"):
            return 0,"Error: some of the required parameters (bus,model) in conf_string are not present"
        chan = "undef"
        if conf.has("chan"):
            chan = int(conf.params["chan"])
        try:
            conf_bus = conf_strings.parse(conf.params["bus"])
        except Exception as e:
            return 0,str(e)
        if not conf_bus.has("vendor"):
            conf_bus.params["vendor"]="0403"
        if not conf_bus.has("product"):
            conf_bus.params["product"]="faf0"
        if not conf_bus.has("baudrate"):
            conf_bus.params["baudrate"]="115200"
        retcode,res = submod.execcmd("init_"+conf_bus.name,conf_strings.unparse(conf_bus))
        if retcode==0:
            return 0,"Error initializing link <- %s" % (res)
        th_apt_id = self.th_apt_pool.new({"bus": conf_bus.name, "bus_id": res, "chan": chan, "model": conf.params["model"]})
        return 1,th_apt_id

    def deinit(self,th_apt_id):
        try:
            th_apt = self.th_apt_pool.get(th_apt_id)
        except Exception as e:
            return 1,"th_apt_%s" % (str(e))
        retcode,res = submod.execcmd("deinit_"+th_apt["bus"],th_apt["bus_id"])
        if retcode==0:
            return 0,"Error deinitializing link <- %s" % (res)
        try:
            self.th_apt_pool.remove(th_apt_id)
        except Exception as e:
            return 0,str(e)
        return 1,"ok"

    def config(self,th_apt_id,pos_max,pos_min):
        try:
            th_apt = self.th_apt_pool.get(th_apt_id)
        except Exception as e:
            return 0,"th_apt_%s" % (str(e))
        if "configured" in th_apt:
            return 1,"already configured"
        retcode,res = submod.execcmd("config_"+th_apt["bus"],th_apt["bus_id"])
        if retcode==0:
            return 0,"Error configuring link <- %s" % (res)
        try:
            # Verify consistency of parameters
            pos_max = float(pos_max)
            pos_min = float(pos_min)
            if pos_max<=pos_min:
                raise self.th_apt_Exception((0,"pos_max must be higher than pos_min"))
            if pos_max<0 or pos_min<0:
                raise self.th_apt_Exception((0,"neither pos_max nor pos_min can be negative"))
            # Init communication
            if th_apt["chan"]!="undef":
                th_apt["chan_addr"] = 0x20 + th_apt["chan"]
                th_apt["mb_addr"] = 0x11
            else:
                th_apt["chan_addr"] = 0x50
                th_apt["mb_addr"] = 0x50
            retcode,res = self.send_message(th_apt,"MGMSG_HW_NO_FLASH_PROGRAMMING",th_apt["mb_addr"],param1=0,param2=0)
            if retcode==0:
                raise self.th_apt_Exception((0,"Error initializing communication: %s" % (res)))
            retcode,res = self.send_message(th_apt,"MGMSG_HW_STOP_UPDATEMSGS",th_apt["mb_addr"],param1=0,param2=0)
            if retcode==0:
                raise self.th_apt_Exception((0,"Error stopping update messages: %s" % (res)))
            retcode,res = self.send_message(th_apt,"MGMSG_HW_REQ_INFO",th_apt["mb_addr"],param1=0,param2=0)
            if retcode==0:
                raise self.th_apt_Exception((0,"Error requesting hw info: %s" % (res)))
            retcode,res = self.recv_message(th_apt)
            if retcode==0:
                raise self.th_apt_Exception((0,"Error getting hw info: %s" % (res)))
            message = res
            if self.code_cmds[self.cmd(message)]!="MGMSG_HW_GET_INFO":
                raise self.th_apt_Exception((0,"Error checking hw info: wrong message received"))
            if decode_word(message[176:180])>1:
                if th_apt["chan"]=="undef":
                    raise self.th_apt_Exception((0,"Channel is needed for this controller"))
                # Check if bay is used
                retcode,res = self.send_message(th_apt,"MGMSG_RACK_REQ_BAYUSED",th_apt["mb_addr"],param1=th_apt["chan"]-1,param2=0)
                if retcode==0:
                    raise self.th_apt_Exception((0,"Error sending check of chan: %s" % (res)))
                retcode,res = self.recv_message(th_apt)
                if retcode==0:
                    raise self.th_apt_Exception((0,"Error getting check of chan: %s" % (res)))
                message = res
                if self.code_cmds[self.cmd(message)]!="MGMSG_RACK_GET_BAYUSED" or self.param1(message)!=th_apt["chan"]-1:
                    raise self.th_apt_Exception((0,"Error checking chan: wrong message received"))
                if self.param2(message)!=0x01:
                    raise self.th_apt_Exception((0,"Bay not connected in controller"))
            else:
                if th_apt["chan"]!="undef":
                    raise self.th_apt_Exception((0,"Only one channel on this controller"))
            # Enable channel
            retcode,res = self.send_message(th_apt,"MGMSG_MOD_SET_CHANENABLESTATE",th_apt["chan_addr"],param1=1,param2=1)
            if retcode==0:
                raise self.th_apt_Exception((0,"Error enabling channel: %s" % (res)))
            # Set axis scaling parameters
            if th_apt["model"]=="BSC2_LNR50":
                th_apt.update(self.BSC2_DRV014)
            elif th_apt["model"]=="LTS300":
                th_apt.update(self.BSC_DRV014)
            else:
                raise self.th_apt_Exception((0,"Unknown model %s. Please, contact the developers to implement support."%(th_apt["model"])))
            # Limits for 32b fields
            th_apt["p_lim"] = float(2147483648)/th_apt["usteps_per_mm_p"]
            th_apt["v_lim"] = float(2147483648)/th_apt["usteps_per_mm_v"]
            th_apt["a_lim"] = float(2147483648)/th_apt["usteps_per_mm_a"]
            print("Maximum protocol velocity: {0:.1f} mm/s".format(th_apt["v_lim"]))
            print("Maximum protocol acceleration: {0:.1f} mm/s**2".format(th_apt["a_lim"]))
            # Set axis limits
            data =  "0100"
            data += th_apt["limitswitch"]*2
            data += encode_long(int(round(th_apt["usteps_per_mm_p"]*pos_max)))
            data += encode_long(int(round(th_apt["usteps_per_mm_p"]*pos_min)))
            data += "0300"
            retcode,res = self.send_message(th_apt,"MGMSG_MOT_SET_LIMSWITCHPARAMS",th_apt["chan_addr"],data=data)
            if retcode==0:
                raise self.th_apt_Exception((0,"Error setting limits on axis: %s" % (res)))
            th_apt["pos_max"] = pos_max
            th_apt["pos_min"] = pos_min
            # Get status update message (at least it lights up the channel LED)
            res = self.get_statusupdate(th_apt)
        except self.th_apt_Exception as e:
            _,_ = submod.execcmd("inval_"+th_apt["bus"],th_apt["bus_id"])
            return e[0]
        th_apt["configured"] = True
        return 1,"ok"

    def inval(self,th_apt_id):
        try:
            th_apt = self.th_apt_pool.get(th_apt_id)
        except Exception as e:
            return 0,"th_apt_%s" % (str(e))
        if not "configured" in th_apt:
            return 1,"not configured"
        # Disable channel
        retcode,res = self.send_message(th_apt,"MGMSG_MOD_SET_CHANENABLESTATE",th_apt["chan_addr"],param1=1,param2=2)
        if retcode==0:
            return 0,"Error disabling channel in chan: %s" % (res)
        # Get status update message (at least it lights down the channel LED)
        try:
            self.get_statusupdate(th_apt)
        except self.th_apt_Exception as e:
            return e[0]
        # Invalidate bus
        retcode,res = submod.execcmd("inval_"+th_apt["bus"],th_apt["bus_id"])
        if retcode==0:
            return 0,"Error invalidating link <- %s" % (res)
        # Remove parameters set during config
        del th_apt["usteps_per_mm_p"]
        del th_apt["usteps_per_mm_v"]
        del th_apt["usteps_per_mm_a"]
        del th_apt["p_lim"]
        del th_apt["v_lim"]
        del th_apt["a_lim"]
        del th_apt["pos_max"]
        del th_apt["pos_min"] 
        del th_apt["chan_addr"]
        del th_apt["mb_addr"]
        del th_apt["limitswitch"]
        del th_apt["configured"]
        return 1,"ok"

    def reset(self,th_apt_id,direction,velocity):
        try:
            th_apt = self.th_apt_pool.get(th_apt_id)
        except Exception as e:
            return 0,"th_apt_%s" % (str(e))
        if not "configured" in th_apt:
            return 0,"not configured"
        # Set axis limits
        data =  "0100"
        data += th_apt["limitswitch"]*2
        data += encode_long(int(round(th_apt["usteps_per_mm_p"]*th_apt["pos_max"])))
        data += encode_long(int(round(th_apt["usteps_per_mm_p"]*th_apt["pos_min"])))
        data += "0300"
        retcode,res = self.send_message(th_apt,"MGMSG_MOT_SET_LIMSWITCHPARAMS",th_apt["chan_addr"],data=data)
        if retcode==0:
            return 0,"Error setting limits on axis: %s" % (res)
        # Set homing params
        if abs(float(velocity))>th_apt["v_lim"]:
            return 0,"Velocity is over the allowed limit of {0:.1f} mm/s".format(th_apt["v_lim"])
        v = int(round(float(velocity)*th_apt["usteps_per_mm_v"]))
        if direction=="r":
            data = "010002000100" # channel (16b), direction (16b), limit (16b)
        elif direction=="f":
            data = "010001000400" # channel (16b), direction (16b), limit (16b)
        data += encode_long(v) # velocity
        data += "00a00000" # offset
        retcode,res = self.send_message(th_apt,"MGMSG_MOT_SET_HOMEPARAMS",th_apt["chan_addr"],data=data)
        if retcode==0:
            return 0,"Error setting homing params: %s" % (res)
        # Send home command
        retcode,res = self.send_message(th_apt,"MGMSG_MOT_MOVE_HOME",th_apt["chan_addr"],param1=1,param2=0)
        if retcode==0:
            return 0,"Error sending home command: %s" % (res)
        res = {}
        res["homed"] = False
        while not (res["homed"] and res["completed"]==th_apt["need_completed"]):
            try:
                res = self.get_statusupdate(th_apt)
            except self.th_apt_Exception as e:
                return e[0]
            sleep(1)
        return 1,"ok"

    def is_reset(self,th_apt_id):
        try:
            th_apt = self.th_apt_pool.get(th_apt_id)
        except Exception as e:
            return 0,"th_apt_%s" % (str(e))
        if not "configured" in th_apt:
            return 0,"not configured"
        try:
            res = self.get_statusupdate(th_apt)
        except self.th_apt_Exception as e:
            return e[0]
        return 1,str(int(res["homed"]))

    def move(self,th_apt_id,displacement,velocity,acceleration):
        try:
            th_apt = self.th_apt_pool.get(th_apt_id)
        except Exception as e:
            return 0,"th_apt_%s" % (str(e))
        if not "configured" in th_apt:
            return 0,"not configured"
        # Check destination
        retcode,res = self.get_pos(th_apt_id)
        if displacement.upper() not in ["MAX","MIN"]:
            displacement = float(displacement)
            if float(res)+displacement > th_apt["pos_max"] or float(res)+displacement < th_apt["pos_min"]:
                return 0,"Refusing to move from %f to %f. Would end out of the axis limits"%(float(res),float(res)+displacement)
        elif displacement.upper()=="MIN":
            displacement = th_apt["pos_min"]-float(res)
        elif displacement.upper()=="MAX":
            displacement = th_apt["pos_max"]-float(res)
        # Set velocity params
        if abs(float(velocity))>th_apt["v_lim"]:
            return 0,"Velocity is over the allowed limit of {0:.1f} mm/s".format(th_apt["v_lim"])
        if abs(float(acceleration))>th_apt["a_lim"]:
            return 0,"Acceleration is over the allowed limit of {0:.1f} mm/s**2".format(th_apt["a_lim"])
        v_max = int(round(float(velocity)*th_apt["usteps_per_mm_v"]))
        accel = int(round(float(acceleration)*th_apt["usteps_per_mm_a"]))
        data =  "0100" # channel
        data += "00000000" # v_min
        data += encode_long(accel)
        data += encode_long(v_max)
        retcode,res = self.send_message(th_apt,"MGMSG_MOT_SET_VELPARAMS",th_apt["chan_addr"],data=data)
        if retcode==0:
            return 0,"Error setting velocity params: %s" % (res)
        # Move
        usteps = int(round(float(displacement)*th_apt["usteps_per_mm_p"]))
        data =  "0100" # channel
        data += encode_long(usteps)
        retcode,res = self.send_message(th_apt,"MGMSG_MOT_MOVE_RELATIVE",th_apt["chan_addr"],data=data)
        if retcode==0:
            return 0,"Error setting velocity params: %s" % (res)
        res = {}
        res["motion"] = True
        res["completed"] = not th_apt["need_completed"]
        while res["motion"] or res["completed"]!=th_apt["need_completed"]:
            try:
                res = self.get_statusupdate(th_apt)
            except self.th_apt_Exception as e:
                return e[0]
            sleep(0.1)
        return 1,"ok"

    def get_pos(self,th_apt_id):
        try:
            th_apt = self.th_apt_pool.get(th_apt_id)
        except Exception as e:
            return 0,"th_apt_%s" % (str(e))
        if not "configured" in th_apt:
            return 0,"not configured"
        # Get position
        retcode,res = self.send_message(th_apt,"MGMSG_MOT_REQ_POSCOUNTER",th_apt["chan_addr"],param1=1,param2=0)
        if retcode==0:
            raise self.th_apt_Exception((0,"Error asking for position: %s" % (res)))
        retcode,res = self.recv_message(th_apt)
        if retcode==0:
            raise self.th_apt_Exception((0,"Error getting position: %s" % (res)))
        message = res
        if self.code_cmds[self.cmd(message)]!="MGMSG_MOT_GET_POSCOUNTER":
            raise self.th_apt_Exception((0,"Error checking position: wrong message received"))
        position = float(decode_long(message[16:]))/th_apt["usteps_per_mm_p"]
        return 1,str(position)

    def go_min(self,th_apt_id,velocity,acceleration):
        return self.move(th_apt_id,"MIN",velocity,acceleration)

    def go_max(self,th_apt_id,velocity,acceleration):
        return self.move(th_apt_id,"MAX",velocity,acceleration)

# CREATE TH_APT POOL #############################################

me = th_apt()

# COMMANDS #######################################################

# Put serialized API in memory if not called via import
if __name__ == '__main__':
    global api; api = getapi.load_api(__file__)

def getapi_th_apt():
    submod.setres(1,api)

def init_th_apt(conf_string):
    """Initialize TH_APT motion controller chanel.
    
    conf_string must contain the parameters:

        - bus: a conf_string for cmd_serial or cmd_tcp
        - chan: channel where the motor to control is attached

    Returns id of TH_APT, th_apt_id"""
    retcode,res = me.init(conf_string)
    if retcode==0:
        submod.setres(retcode,"th_apt: %s" % (res))
        return
    submod.setres(retcode,res) 
    
def deinit_th_apt(th_apt_id):
    "Deinitialize *th_apt_id* motion controller channel."
    retcode,res = me.deinit(th_apt_id)
    if retcode==0:
        submod.setres(retcode,"th_apt: %s" % (res))
        return
    submod.setres(retcode,res)

def config_th_apt(th_apt_id,pos_max,pos_min):
    "Configure *th_apt_id* motion controller channel."
    retcode,res = me.config(th_apt_id,pos_max,pos_min)
    if retcode==0:
        submod.setres(retcode,"th_apt: %s" % (res))
        return
    submod.setres(retcode,res)

def inval_th_apt(th_apt_id):
    "Invalidate *th_apt_id* motion controller channel."
    retcode,res = me.inval(th_apt_id)
    if retcode==0:
        submod.setres(retcode,"th_apt: %s" % (res))
        return
    submod.setres(retcode,res)

def reset_th_apt(th_apt_id,direction="r",velocity="1"):
    "Reset *th_apt_id* channel by moving the motor to its home position. Do it in the reverse (r) or forward (r) *direction* with *velocity*."
    retcode,res = me.reset(th_apt_id,direction,velocity)
    if retcode==0:
        submod.setres(retcode,"th_apt: %s" % (res))
        return
    submod.setres(retcode,res)

def is_reset_th_apt(th_apt_id):
    "Check if channel been homed."
    retcode,res = me.is_reset(th_apt_id)
    if retcode==0:
        submod.setres(retcode,"th_apt: %s" % (res))
        return
    submod.setres(retcode,res)

def move_th_apt(th_apt_id,displacement,velocity,acceleration):
    "Move channel by *displacement* mm with the specified *velocity*. A ramp up from zero with *acceleration* is used to get to velocity. Units are mm, mm/s and mm/s**2."
    retcode,res = me.move(th_apt_id,displacement,velocity,acceleration)
    if retcode==0:
        submod.setres(retcode,"th_apt: %s" % (res))
        return
    submod.setres(retcode,res)

def get_pos_th_apt(th_apt_id):
    "Get position of channel. Result is returned in mm."
    retcode,res = me.get_pos(th_apt_id)
    if retcode==0:
        submod.setres(retcode,"th_apt: %s" % (res))
        return
    submod.setres(retcode,res)

def go_min_th_apt(th_apt_id,velocity,acceleration):
    "Go to the minimum position defined during the configuration of the channel"
    retcode,res = me.go_min(th_apt_id,velocity,acceleration)
    if retcode==0:
        submod.setres(retcode,"th_apt: %s" % (res))
        return
    submod.setres(retcode,res)

def go_max_th_apt(th_apt_id,velocity,acceleration):
    "Go to the maximum position defined during the configuration of the channel"
    retcode,res = me.go_max(th_apt_id,velocity,acceleration)
    if retcode==0:
        submod.setres(retcode,"th_apt: %s" % (res))
        return
    submod.setres(retcode,res)
