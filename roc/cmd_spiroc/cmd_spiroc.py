#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Copyright 2012-2015 Frédéric Magniette, Miguel Rubio-Roy, LLR
#

import pools

import common_roc
if __name__=='__main__':
    common_roc.submod = submod

spiroc_pool=pools.pool("spiroc")

spiroc_bs_length=929

#************************* BITSTREAM MANIPULATION FUNCTIONS ***************

# **************************************************************************
# trigger threshold
# **************************************************************************

def set_gtrigger(spiroc_id,gtrigger):
    "set the trigger threshold of a spiroc"
    if gtrigger!="undef":
        return common_roc.apply_to_roc(spiroc_pool,spiroc_id,common_roc.apply_inv_mask,"set trigger threshold",239,common_roc.split_bin(int(gtrigger),10))
    return 1,"ok"

def set_gtrigger_spiroc(spiroc_id,gtrigger):
    "set the trigger threshold of a spiroc"
    retcode,res = set_gtrigger(spiroc_id,gtrigger)
    if retcode==0:
        submod.setres(0,"spiroc: %s"%(res))
        return
    submod.setres(1,"ok")

# **************************************************************************
# chipid
# **************************************************************************

def set_chipid(spiroc_id,spiroc):
    "set the chipid of a spiroc chip on its bitstream"
    idbin = common_roc.split_bin(common_roc.bin2gray(int(spiroc["chipid"])),8)
    retcode,res=common_roc.apply_to_roc(spiroc_pool,spiroc_id,common_roc.apply_mask,"set chipid",905,idbin)
    if retcode==0:
        return 0,res
    retcode,res = submod.execcmd("set_param_cmod",spiroc_id,"spiroc_chipid",spiroc["chipid"])
    if retcode==0:
        return 0,res
    return 1,"ok"

def set_chipid_param_spiroc(spiroc_id,chipid):
    "set the chipid of a spiroc chip on the pool"
    try:
        spiroc = spiroc_pool.get(spiroc_id)
    except Exception as e:
        submod.setres(0,"spiroc: spiroc_%s" % (str(e)))
        return
    if chipid!="undef":
        spiroc["chipid"] = chipid
    submod.setres(1,"ok")

def get_chipid_spiroc(spiroc_id):
    "get the chipid of a spiroc"
    try:
        spiroc = spiroc_pool.get(spiroc_id)
    except Exception as e:
        submod.setres(0,"spiroc: spiroc_%s" % (str(e)))
        return
    submod.setres(1,"chipid=%s"%(spiroc["chipid"]))

# **************************************************************************
# triggers
# **************************************************************************

def allow_trig(spiroc,chan):
    "allow a channel to trig"
    common_roc.apply_mask(spiroc,73+int(chan),common_roc.split_bin(0,1))
    return 1,"ok"

def allow_trig_chans(spiroc_id,chans):
    "allow trigger on channels"
    return common_roc.apply_to_chans(spiroc_pool,spiroc_id,chans,allow_trig,"allow trigger")
    
def allow_trig_chans_spiroc(spiroc_id,chans):
    "allow trigger on channels"
    retcode,res = allow_trig_chans(spiroc_id,chans)
    if retcode==0:
        submod.setres(0,"spiroc: %s"%(res))
        return
    submod.setres(1,"ok")

# **************************************************************************

def disallow_trig(spiroc,chan):
    "disallow a channel to trig"
    common_roc.apply_mask(spiroc,73+int(chan),common_roc.split_bin(1,1))
    return 1,"ok"

def disallow_trig_chans(spiroc_id,chans):
    "disallow trigger on channels"
    return common_roc.apply_to_chans(spiroc_pool,spiroc_id,chans,disallow_trig,"disallow trigger")

def disallow_trig_chans_spiroc(spiroc_id,chans):
    "disallow trigger on channels"
    retcode,res = disallow_trig_chans(spiroc_id,chans)
    if retcode==0:
        submod.setres(0,"spiroc: %s"%(res))
        return
    submod.setres(1,"ok")

#********************************** GENERAL PUBLIC FUNCTIONS ***************

def dump_sc_spiroc(spiroc_id):
    "Returns bitstream of *spiroc_id* in binary format"
    try:
        spiroc = spiroc_pool.get(spiroc_id)
    except Exception as e:
        submod.setres(0,"spiroc: spiroc_%s" % (str(e)))
        return
    #return the bitstream
    bitstream = spiroc["bitstream"] if not spiroc["missing"] else ""
    submod.setres(1,bitstream)

def set_missing_spiroc(spiroc_id,missing):
    "Set spiroc missing state"
    try:
        spiroc = spiroc_pool.get(spiroc_id)
    except Exception as e:
        submod.setres(0,"spiroc: spiroc_%s" % (str(e)))
        return
    spiroc["missing"] = True if missing=="1" else False
    submod.setres(1,"ok")

#****************************** PHASES *************************************

def init_spiroc(parent_device,dev_name):
    "Initialize a spiroc"
    #register in the config module
    retcode,res = submod.execcmd("new_device_cmod","spiroc",dev_name,parent_device)
    if retcode==0:
        submod.setres(0,"spiroc: cant register in cmod <- %s"%(res))
        return
    spiroc_id=res
    spiroc_pool.new({},spiroc_id)
    #send back the id
    submod.setres(1,spiroc_id)

def deinit_spiroc():
    "Deinitialize *spiroc_id*"
    try:
        spiroc = spiroc_pool.get(spiroc_id)
    except Exception as e:
        submod.setres(1,"spiroc: spiroc_%s" % (str(e)))
        return
    spiroc_pool.remove(spiroc_id)
    submod.setres(1,"ok")

def config_spiroc(spiroc_id,file,bitstream,gtrigger,masktrig,nomasktrig):
    "prepare the bitstream for configuring a chip"
    try:
        spiroc = spiroc_pool.get(spiroc_id)
    except Exception as e:
        submod.setres(0,"spiroc: spiroc_%s" % (str(e)))
        return
    spiroc["missing"]=False
    #empty the bitstream
    spiroc["bitstream"]=""
    #load bitstream
    if bitstream!="undef":
        retcode,res = common_roc.load_str(bitstream,spiroc_bs_length)
        if retcode==0:
            submod.setres(0,"spiroc: cant parse bitstream: %s"%(res))
            return
        spiroc["bitstream"]=res
    #load bitstream from file
    if file!="undef":
        retcode,res = common_roc.load_file(file,spiroc_bs_length)
        if retcode==0:
            submod.setres(0,"spiroc: cant open config file: %s"%(res))
            return
        spiroc["bitstream"]=res
    if spiroc["bitstream"]=="":
        submod.setres(0,"spiroc: no bitstream defined for spiroc %s"%(spiroc_id))
        return
    #set chip id
#    retcode,res = set_chipid(spiroc_id,spiroc)
#    if retcode==0:
#        submod.setres(0,"cant set chipid: %s"%(res))
#        return
    #set global trigger threshold
    retcode,res = set_gtrigger(spiroc_id,gtrigger)
    if retcode==0:
        submod.setres(0,"spiroc: cant set trigger threshold: %s"%(res))
        return
    # allows to mask trigger
    retcode,res = allow_trig_chans(spiroc_id,masktrig)
    if retcode==0:
        submod.setres(0,"spiroc: cant allow to mask masktrig: %s"%(res))
        return
    # disallows to mask trigger
    retcode,res = disallow_trig_chans(spiroc_id,nomasktrig)
    if retcode==0:
        submod.setres(0,"spiroc: cant disallows to mask nomasktrig: %s"%(res))
        return
    #return result
    submod.setres(1,"ok")
