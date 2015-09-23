#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Copyright 2012-2015 Frédéric Magniette, Miguel Rubio-Roy, LLR
#

import math

def split_bin(n,size):
    "translate an integer in binary string"
    if not size:
        return ""
    return ("{0:0%sb}"%size).format(n)[-size:]

def is_hexa(s):
    "test if a string represent an hexadecimal number"
    try:
        int("0x%s" % s,16)
        return True
    except ValueError:
        return False

def load_file(filename,bs_length,inverse=False):
    "Load a bitstream from a file. If the file content starts with '0x' or '0b ' (note the whitespace), it is considered to be hexadecimal or binary respectively. Otherwise it is considered hexadecimal."
    try:
        fd = open(filename,"r")
    except:
        return 0,"can't open file %s"%(filename)
    try:
        bitstream = fd.read()
    finally:
        fd.close()
    return load_str(bitstream,bs_length,inverse)

def load_str(bs,bs_length,inverse=False):
    "Load a bitstream from string. If the string starts with '0x' or '0b' (case sensitive), it is considered to be hexadecimal or binary respectively. Otherwise it is considered a decimal integer."
    bs = bs.strip()
    if bs[:2]=="0b":
        try:
            int(bs[2:],2)
        except Exception as e:
            return 0,"invalid binary bitstream: %s"%(str(e))
        bs_b = bs[2:]
    elif bs[:2]=="0x":
        bs = bs[2:]
        try:
            bs_b = split_bin(int(bs,16),4*len(bs))
        except Exception as e:
            return 0,"invalid hexadecimal bitstream: %s"%(str(e))
    else:
        try:
            bs = int(bs)
            if bs!=0:
                bs_b = split_bin(bs,int(math.ceil(math.log(bs,2))))
            else:
                bs_b = "0"
        except Exception as e:
            return 0,"invalid decimal bitstream: %s"%(str(e))
    if len(bs_b)>bs_length:
        bs_b = bs_b[:bs_length]
        print("\n\nWarning: trimming bitstream to %d. It was %d\n\n"%(bs_length,len(bs_b)))
    if len(bs_b)<bs_length:
        return 0,"Invalid bitstream length %d. Should be %d"%(len(bs_b),bs_length)
    if inverse:
        bs_b = bs_b[::-1]
    return 1,bs_b

def apply_mask(roc,pos,src):
    "apply a pattern in a bitstream at fixed position"
    if src!="undef":
        lpart=roc["bitstream"][0:pos]
        rpart=roc["bitstream"][pos+len(src):len(roc["bitstream"])]
        roc["bitstream"]=lpart+src+rpart
    return 1,"ok"

def apply_inv_mask(roc,pos,src):
    "the same but with inverse order"
    #reverse the pattern
    apat=src[::-1]
    return apply_mask(roc,pos,apat)

def bin2gray(num):
    "convert to gray"
    return (num>>1)^num

def bin2hexa(binstr):
    "convert a binary string in hexadecimal padding with zeroes on MSB if necessary"
    return ("{0:0%dx}"%(int(math.ceil(len(binstr)/4.0)))).format(int(binstr,2))

def parse_channel_list(channel_list):
    "Parse comma-separated channel list with dash-defined ranges accepted. e.g.: 1,3,7-12,5"

    if channel_list=="undef" or channel_list=="":
        return []

    if channel_list=="all":
        channel_list="0-63"

    channel_list = channel_list.split(",")
    channels = []
    for channel in channel_list:
        if len(channel.split("-")) > 1:
            channels += range(int(channel.split("-")[0]),int(channel.split("-")[1])+1)
        else:
            channels.append(int(channel))
    return list(set(channels))

def on_off_bit(maroc3,pos,value):
    value = str(value).upper().strip()
    if value=="ON" or value=="1":
        value = "1"
    elif value=="OFF" or value=="0":
        value = "0"
    elif value=="UNDEF":
        return 1,"ok"
    elif value!="UNDEF":
        return 0,"invalid value: %s"%(value)
    return apply_mask(maroc3,pos,str(value))

def apply_to_chans(roc_pool,roc_id,chans,func,msg,*params):
    "generic application of a function to multiple channels of a roc"
    try:
        roc = roc_pool.get(roc_id)
    except Exception as e:
        return 0,"roc_%s" % (str(e))
    if chans=="undef":
        return 1,"ok"
    #apply the bitstream modification
    for c in parse_channel_list(chans):
        retcode,res=func(roc,c,*params)
        if retcode==0:
            return 0,"can't %s on roc %s channel %s : %s"%(msg,roc_id,c,res)
    #update the bitstream in cmod
    retcode,res=submod.execcmd("set_param_cmod",roc_id,roc_pool.name+"_bitstream",bin2hexa(roc["bitstream"]))
    if retcode==0:
        return 0,"can't update bitstream in cmod"
    return 1,"ok"

def apply_to_roc(roc_pool,roc_id,func,msg,*params):
    "generic application of a function to roc"
    retcode,res = roc_pool.call(roc_id,func,*params)
    if retcode==0:
        return 0,"can't %s on roc %s : %s"%(msg,roc_id,res)
    #update the bitstream in cmod
    try:
        roc = roc_pool.get(roc_id)
    except Exception as e:
        return 0,"roc_%s" % (str(e))
    retcode,res=submod.execcmd("set_param_cmod",roc_id,roc_pool.name+"_bitstream",bin2hexa(roc["bitstream"]))
    if retcode==0:
        return 0,"can't update bitstream in cmod"
    return 1,"ok"

