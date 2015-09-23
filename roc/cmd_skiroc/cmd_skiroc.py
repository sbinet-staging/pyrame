#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Copyright 2012-2015 Frédéric Magniette, Miguel Rubio-Roy, LLR
#

import pools

import common_roc
if __name__=='__main__':
    common_roc.submod = submod

skiroc_pool=pools.pool("skiroc")

skiroc_bs_length=616

#************************* BITSTREAM MANIPULATION FUNCTIONS ***************

# **************************************************************************
# trigger mode
# **************************************************************************

def set_trigmode_reg(skiroc,mode):
    "set the trigger mode of a skiroc"
    if mode!="undef":
        if mode=="ext":
            return common_roc.apply_mask(skiroc,9,common_roc.split_bin(1,1))
        if mode=="int":
            return common_roc.apply_mask(skiroc,9,common_roc.split_bin(0,1))
    return 0,"Unknown mode %s. Supported mode are int or ext"%(mode)

def set_trigmode(skiroc_id,mode):
    "set the trigger mode of a skiroc"
    return common_roc.apply_to_roc(skiroc_pool,skiroc_id,set_trigmode_reg,"set trigger mode",mode)

def set_trigmode_skiroc(skiroc_id,mode):
    "set the trigger mode of a skiroc"
    retcode,res=set_trigmode(skiroc_id,mode)
    if retcode==0:
        submod.setres(0,"skiroc: %s"%(res))
        return
    submod.setres(1,res)

# **************************************************************************
# trigger threshold
# **************************************************************************

def set_gtrigger_reg(skiroc,gtrigger):
    "set the trigger threshold of a skiroc"
    if gtrigger!="undef":
        return common_roc.apply_inv_mask(skiroc,41,common_roc.split_bin(int(gtrigger),10))
    return 1,"ok"

def set_gtrigger(skiroc_id,gtrigger):
    "set the trigger threshold of a skiroc"
    return common_roc.apply_to_roc(skiroc_pool,skiroc_id,set_gtrigger_reg,"set trigger threshold",gtrigger)

def set_gtrigger_skiroc(skiroc_id,gtrigger):
    "set the trigger threshold of a skiroc"
    retcode,res=set_gtrigger(skiroc_id,gtrigger)
    if retcode==0:
        submod.setres(0,"skiroc: %s"%(res))
        return
    submod.setres(1,res)

# **************************************************************************
# hold delay
# **************************************************************************

def set_delay_reg(skiroc,delay):
    "set the hold delay of a skiroc"
    if delay!="undef":
        return common_roc.apply_inv_mask(skiroc,63,common_roc.split_bin(int(delay),8))
    return 1,"ok"

def set_delay(skiroc_id,delay):
    "set the hold delay of a skiroc"
    return common_roc.apply_to_roc(skiroc_pool,skiroc_id,set_delay_reg,"set hold delay",delay)

def set_delay_skiroc(skiroc_id,delay):
    "set the hold delay of a skiroc"
    retcode,res=set_delay(skiroc_id,delay)
    if retcode==0:
        submod.setres(0,"skiroc: %s"%(res))
        return
    submod.setres(1,res)

# **************************************************************************
# compensation capacitance
# **************************************************************************

cpcap_strings=["0pF","1pF","2pF","3pF","4pF","5pF","6pF","7pF"]

def set_cpcap_reg(skiroc,cpcap):
    "set the compensation capacitance of a skiroc"
    if cpcap!="undef":
        for i in range(len(cpcap_strings)):
            if cpcap_strings[i]==cpcap:
                return common_roc.apply_inv_mask(skiroc,611,common_roc.split_bin(i,3))
    else:
        return 1,"ok"
    return 0,"unknown value %s. accepted values are 0pF,1pF,2pF,3pF,4pF,5pF,6pF,7pF"%(cpcap)

def set_cpcap(skiroc_id,cpcap):
    "set the compensation capacitance of a skiroc"
    return common_roc.apply_to_roc(skiroc_pool,skiroc_id,set_cpcap_reg,"set feedback capacitance",cpcap)

def set_cpcap_skiroc(skiroc_id,cpcap):
    "set the compensation capacitance of a skiroc"
    retcode,res=set_cpcap(skiroc_id,cpcap)
    if retcode==0:
        submod.setres(0,"skiroc: %s"%(res))
        return
    submod.setres(1,res)

# **************************************************************************
# feedback capacitance
# **************************************************************************

fbcap_strings=["0pF","0.4pF","0.8pF","1.2pF","1.6pF","2pF","2.4pF","2.8pF","3.2pF","3.6pF","4pF","4.4pF","4.8pF","5.2pF","5.6pF","6pF"]

def set_fbcap_reg(skiroc,fbcap):
    "set the feedback capacitance of a skiroc"
    if fbcap!="undef":
        for i in range(len(fbcap_strings)):
            if fbcap_strings[i]==fbcap:
                return common_roc.apply_inv_mask(skiroc,607,common_roc.split_bin(i,4))
    else:
        return 1,"ok"
    return 0,"unknown value %s. accepted values are 0pF,0.4pF,0.8pF,1.2pF,1.6pF,2pF,2.4pF,2.8pF,3.2pF,3.6pF,4pF,4.4pF,4.8pF,5.2pF,5.6pF,6pF"%(fbcap)

def set_fbcap(skiroc_id,fbcap):
    "set the feedback capacitance of a skiroc"
    return common_roc.apply_to_roc(skiroc_pool,skiroc_id,set_fbcap_reg,"set feedback capacitance",fbcap)

def set_fbcap_skiroc(skiroc_id,fbcap):
    "set the feedback capacitance of a skiroc"
    retcode,res=set_fbcap(skiroc_id,fbcap)
    if retcode==0:
        submod.setres(0,"skiroc: %s"%(res))
        return
    submod.setres(1,res)

# **************************************************************************
# readout set
# **************************************************************************

def set_start_ro_reg(skiroc,start_ro):
    "start the readout set"
    if int(start_ro)==1:
        return common_roc.apply_mask(skiroc,5,common_roc.split_bin(1,1))
    elif int(start_ro)==2:
        return common_roc.apply_mask(skiroc,5,common_roc.split_bin(0,1))
    elif start_ro=="undef":
        return 1,"ok"
    return 0,"invalid value: %s"%(start_ro)


def set_start_ro(skiroc_id,start_ro):
    "start the readout set"
    return common_roc.apply_to_roc(skiroc_pool,skiroc_id,set_start_ro_reg,"start the readout set",start_ro)

def set_start_ro_skiroc(skiroc_id,start_ro):
    "start the readout set" 
    retcode,res=set_start_ro(skiroc_id,start_ro)
    if retcode==0:
        submod.setres(0,"skiroc: %s"%(res))
        return
    submod.setres(1,res)

# **************************************************************************

def set_end_ro_reg(skiroc,end_ro):
    "end the readout set"
    if int(end_ro)==1:
        return common_roc.apply_mask(skiroc,6,common_roc.split_bin(1,1))
    elif int(end_ro)==2:
        return common_roc.apply_mask(skiroc,6,common_roc.split_bin(0,1))
    elif end_ro=="undef":
        return 1,"ok"
    return 0,"invalid value: %s"%(end_ro)

def set_end_ro(skiroc_id,end_ro):
    "end the readout set"
    return common_roc.apply_to_roc(skiroc_pool,skiroc_id,set_end_ro_reg,"end the readout set",end_ro)

def set_end_ro_skiroc(skiroc_id,end_ro):
    "end the readout set"
    retcode,res=set_end_ro(skiroc_id,end_ro)
    if retcode==0:
        submod.setres(0,"skiroc: %s"%(res))
        return
    submod.setres(1,res)

# **************************************************************************
# chipid
# **************************************************************************

def set_chipid(skiroc_id,skiroc):
    "set the chipid of a skiroc chip on its bitstream"
    idbin=common_roc.split_bin(common_roc.bin2gray(int(skiroc["chipid"])),8)
    retcode,res=common_roc.apply_to_roc(skiroc_pool,skiroc_id,common_roc.apply_mask,"set chipid",10,idbin)
    if retcode==0:
        return 0,res
    retcode,res=submod.execcmd("set_param_cmod",skiroc_id,"skiroc_chipid",skiroc["chipid"])
    if retcode==0:
        return 0,res
    return 1,"ok"

def set_chipid_param_skiroc(skiroc_id,chipid):
    "set the chipid of a skiroc chip on the pool"
    try:
        skiroc = skiroc_pool.get(skiroc_id)
    except Exception as e:
        submod.setres(0,"skiroc: skiroc_%s" % (str(e)))
        return
    if chipid!="undef":
        skiroc["chipid"]=chipid
    submod.setres(1,"ok")

def get_chipid_skiroc(skiroc_id):
    "get the chipid of a skiroc"
    try:
        skiroc = skiroc_pool.get(skiroc_id)
    except Exception as e:
        submod.setres(0,"skiroc: skiroc_%s" % (str(e)))
        return
    submod.setres(1,"chipid=%s"%(skiroc["chipid"]))

# **************************************************************************
# preamps
# **************************************************************************

def enable_preamp_chan(skiroc,chan):
    "enable the preamplifier of a channel"
    return common_roc.apply_mask(skiroc,417+(63-int(chan))*3,common_roc.split_bin(0,1))

def enable_preamp_chans(skiroc_id,chans):
    "enable the preamplifier on channels"
    return common_roc.apply_to_chans(skiroc_pool,skiroc_id,chans,enable_preamp_chan,"enable preamp")

def enable_preamp_chans_skiroc(skiroc_id,chans):
    "enable the preamplifier on channels"
    retcode,res=enable_preamp_chans(skiroc_id,chans)
    if retcode==0:
        submod.setres(0,"skiroc: %s"%(res))
        return
    submod.setres(1,"ok")

# **************************************************************************

def disable_preamp_chan(skiroc,chan):
    "disable the preamplifier of a channel"
    return common_roc.apply_mask(skiroc,417+(63-int(chan))*3,common_roc.split_bin(1,1))

def disable_preamp_chans(skiroc_id,chans):
    "disable the preamplifier on channels"
    return common_roc.apply_to_chans(skiroc_pool,skiroc_id,chans,disable_preamp_chan,"disable preamp")

def disable_preamp_chans_skiroc(skiroc_id,chans):
    "disable the preamplifier on channels"
    retcode,res=disable_preamp_chans(skiroc_id,chans)
    if retcode==0:
        submod.setres(0,"skiroc: %s"%(res))
        return
    submod.setres(1,"ok")

# **************************************************************************
# calibration capacitor
# **************************************************************************

def enable_calib_chan(skiroc, chan):
    "enable the calibration for a channel"
    return common_roc.apply_mask(skiroc,416 +(63-int(chan))*3,common_roc.split_bin(1,1))


def enable_calib_chans(skiroc_id,chans): 
    "enable calibration capacitor on channels"
    return common_roc.apply_to_chans(skiroc_pool,skiroc_id,chans,enable_calib_chan,"enable calibration capacitor")

def enable_calib_chans_skiroc(skiroc_id,chans): 
    "enable calibration capacitor on channels"
    retcode,res=enable_calib_chans(skiroc_id,chans)
    if retcode==0:
        submod.setres(0,"skiroc: %s"%(res))
        return
    submod.setres(1,"ok")

# **************************************************************************

def disable_calib_chan(skiroc, chan):
    "disable the calibration for a channel"
    return common_roc.apply_mask(skiroc, 416+(63-int(chan))*3,common_roc.split_bin(0,1))

def disable_calib_chans(skiroc_id,chans): 
    "disable calibration capacitor on channels" 
    return common_roc.apply_to_chans(skiroc_pool,skiroc_id,chans,disable_calib_chan,"disable calibration capacitor")

def disable_calib_chans_skiroc(skiroc_id,chans): 
    "disable calibration capacitor on channels"
    retcode,res=disable_calib_chans(skiroc_id,chans)
    if retcode==0:
        submod.setres(0,"skiroc: %s"%(res))
        return
    submod.setres(1,"ok")

# **************************************************************************
# high leakage
# **************************************************************************

def select_leak_chan(skiroc, chan):
    "select the high leakage for a channel"
    return common_roc.apply_mask(skiroc,415+(63-int(chan))*3,common_roc.split_bin(1,1))

def select_leak_chans(skiroc_id,chans):  
    "select high leakage current on channels"
    return common_roc.apply_to_chans(skiroc_pool,skiroc_id,chans,select_leak_chan,"select high leakage current")

def select_leak_chans_skiroc(skiroc_id,chans):  
    "select high leakage current on channels"
    retcode,res=select_leak_chans(skiroc_id,chans)
    if retcode==0:
        submod.setres(0,"skiroc: %s"%(res))
        return
    submod.setres(1,"ok")

# **************************************************************************

def unselect_leak_chan(skiroc, chan):
    "unselect the high leakage for a channel"
    return common_roc.apply_mask(skiroc,415+(63-int(chan))*3,common_roc.split_bin(0,1))

def unselect_leak_chans(skiroc_id,chans):  
    "unselect high leakage current on channels"
    return common_roc.apply_to_chans(skiroc_pool,skiroc_id,chans,unselect_leak_chan,"unselect high leakage current")

def unselect_leak_chans_skiroc(skiroc_id,chans):  
    "unselect high leakage current on channels"
    retcode,res=unselect_leak_chans(skiroc_id,chans)
    if retcode==0:
        submod.setres(0,"skiroc: %s"%(res))
        return
    submod.setres(1,"ok")

# **************************************************************************
# triggers
# **************************************************************************

def allow_trig(skiroc,chan):
    "allow a channel to trig"
    return common_roc.apply_mask(skiroc,73+int(chan),common_roc.split_bin(0,1))

def allow_trig_chans(skiroc_id, chans):
    "allow trigger on channels"
    return common_roc.apply_to_chans(skiroc_pool,skiroc_id,chans,allow_trig,"allow trigger")

def allow_trig_chans_skiroc(skiroc_id, chans):
    "allow trigger on channels"
    retcode,res=allow_trig_chans(skiroc_id, chans)
    if retcode==0:
        submod.setres(0,"skiroc: %s"%(res))
        return
    submod.setres(1,"ok")

# **************************************************************************

def disallow_trig(skiroc,chan):
    "disallow a channel to trig"
    return common_roc.apply_mask(skiroc,73+int(chan),common_roc.split_bin(1,1))

def disallow_trig_chans(skiroc_id,chans):
    "disallow trigger on channels"
    return common_roc.apply_to_chans(skiroc_pool,skiroc_id,chans,disallow_trig,"disallow trigger")

def disallow_trig_chans_skiroc(skiroc_id,chans):
    "disallow trigger on channels"
    retcode,res=disallow_trig_chans(skiroc_id,chans)
    if retcode==0:
        submod.setres(0,"skiroc: %s"%(res))
        return
    submod.setres(1,"ok")

# **************************************************************************
# dac adjustment
# **************************************************************************

def set_dacadj(skiroc,chan,dacadj):
    "set the dac adjustment of a channel"
    if dacadj!="undef":
        return common_roc.apply_mask(skiroc,137+int(chan),common_roc.split_bin(int(dacadj),4))
    return 1,"ok"

def set_dacadj_chans(skiroc_id, chans, dacadj):
    "set the dac adjustment to channels"
    return common_roc.apply_to_chans(skiroc_pool,skiroc_id,chans,set_dacadj,"set dac adjustment",dacadj)

def set_dacadj_chans_skiroc(skiroc_id, chans, dacadj):
    "set the dac adjustment to channels"
    retcode,res=set_dacadj_chans(skiroc_id, chans, dacadj)
    if retcode==0:
        submod.setres(0,"skiroc: %s"%(res))
        return
    submod.setres(1,"ok")

#********************************** GENERAL PUBLIC FUNCTIONS ***************

def dump_sc_skiroc(skiroc_id):
    "Returns bitstream of *skiroc_id* in binary format"
    try:
        skiroc = skiroc_pool.get(skiroc_id)
    except Exception as e:
        submod.setres(0,"skiroc: skiroc_%s" % (str(e)))
        return
    #return the bitstream
    bitstream = skiroc["bitstream"] if not skiroc["missing"] else ""
    submod.setres(1,bitstream)

def set_missing_skiroc(skiroc_id,missing):
    "Set skiroc missing state"
    try:
        skiroc = skiroc_pool.get(skiroc_id)
    except Exception as e:
        submod.setres(0,"skiroc: skiroc_%s" % (str(e)))
        return
    skiroc["missing"] = True if missing=="1" else False
    submod.setres(1,"ok")

def explain_sc_skiroc(skiroc_id):
    "Explains the content of a bitsteam in human readable form"
    try:
        skiroc = skiroc_pool.get(skiroc_id)
    except Exception as e:
        submod.setres(0,"skiroc: skiroc_%s" % (str(e)))
        return

    print("hexa bitstream: ")
    print(common_roc.bin2hexa(skiroc["bitstream"]).upper())

    print("binary bitstream: ")
    print(skiroc["bitstream"])

    print("channel preamp  cal capa leak trig    dacadj")
    for channel in range(64):
        if skiroc["bitstream"][417+(63-channel)*3]=="0":
            print_preamp="enabled"
        else:
            print_preamp="disabled"
        if skiroc["bitstream"][416 +(63-channel)*3]=="0":
            print_cal_capa="disabled"
        else:
            print_cal_capa="enabled"
        if skiroc["bitstream"][415+(63-channel)*3]=="0":
            print_leak="low"
        else:
            print_leak="high"
        if skiroc["bitstream"][73+channel]=="0":
            print_trig="allowed"
        else:
            print_trig="masked"
        print_dacadj=skiroc["bitstream"][137+channel:141+channel]
        print("{0:<8d}{1:8s}{2:9s}{3:5s}{4:8s}{5:4s}({6:1s})".format(channel,print_preamp,print_cal_capa,print_leak,print_trig,print_dacadj,common_roc.bin2hexa(print_dacadj)))

    chipid=skiroc["bitstream"][10:18]
    print("Chipid in gray: %s"%(chipid))

    bdelay=skiroc["bitstream"][63:71]
    #print("binary delay: %s"%(bdelay))
    delay=common_roc.bin2hexa(bdelay[::-1])
    idelay=int("0x"+delay,16)
    print("Delay for the trigger signals: %d(0x%s)"%(idelay,delay))

    btrig=skiroc["bitstream"][41:51]
    #print("binary trigth: %s"%(btrig))
    trig=common_roc.bin2hexa(btrig[::-1])
    itrig=int("0x"+trig,16)
    print("Trigger Threshold: %d(0x%s) "%(itrig,trig))

    bfbcap=skiroc["bitstream"][607:611]
    fbcap=common_roc.bin2hexa(bfbcap[::-1])
    ifbcap=int("0x"+fbcap,16)
    print("Feedback capacitance: %d(0x%s) value=%s "%(ifbcap,fbcap,fbcap_strings[ifbcap]))

    bcpcap=skiroc["bitstream"][611:614]
    cpcap=common_roc.bin2hexa(bcpcap[::-1])
    icpcap=int("0x"+cpcap,16)
    print("Compensation capacitance: %d(0x%s) value=%s "%(icpcap,cpcap,cpcap_strings[icpcap]))

    if skiroc["bitstream"][9]=="0":
        print("Internal trigger")
    else:
        print("External trigger only")

    submod.setres(1,"ok") 

#****************************** PHASES *************************************

def init_skiroc(parent_device,dev_name):
    "Initialize a skiroc"
    #register in the config module
    retcode,res=submod.execcmd("new_device_cmod","skiroc",dev_name,parent_device)
    if retcode==0:
        submod.setres(0,"skiroc: cant register in cmod <- %s"%(res))
        return
    skiroc_id=res
    skiroc_pool.new({"name":dev_name,"missing":False},skiroc_id)
    submod.setres(1,skiroc_id)

def deinit_skiroc(skiroc_id):
    "Deinitialize skiroc *skiroc_id*"
    try:
        skiroc = skiroc_pool.get(skiroc_id)
    except Exception as e:
        submod.setres(1,"skiroc: skiroc_%s" % (str(e)))
        return
    skiroc_pool.remove(skiroc_id)
    submod.setres(1,"ok")

def config_skiroc(skiroc_id,file,bitstream,gtrigger,delay,fbcap,start_ro,end_ro,preamp,nopreamp,calcap,nocalcap,leak,noleak,masktrig,nomasktrig):
    "Prepare the bitstream for configuring a chip"
    try:
        skiroc = skiroc_pool.get(skiroc_id)
    except Exception as e:
        submod.setres(0,"skiroc: skiroc_%s" % (str(e)))
        return
    #empty the bitstream
    skiroc["bitstream"]=""
    #load bitstream
    if bitstream!="undef":
        retcode,res=common_roc.load_str(bitstream,skiroc_bs_length)
        if retcode==0:
            submod.setres(0,"skiroc: cant parse bitstream: %s"%(res))
            return
        skiroc["bitstream"]=res
    #load bitstream from file
    if file!="undef":
        retcode,res=common_roc.load_file(file,skiroc_bs_length)
        if retcode==0:
            submod.setres(0,"skiroc: cant open config file: %s"%(res))
            return
        skiroc["bitstream"]=res
    if skiroc["bitstream"]=="":
        submod.setres(0,"skiroc: no bitstream defined for skiroc %s"%(skiroc_id))
        return
    #set chip id
    retcode,res=set_chipid(skiroc_id,skiroc)
    if retcode==0:
        submod.setres(0,"skiroc: cant set chipid: %s"%(res))
        return
    #set global trigger threshold
    retcode,res=set_gtrigger(skiroc_id,gtrigger)
    if retcode==0:
        submod.setres(0,"skiroc: cant set trigger threshold: %s"%(res))
        return
    #set delay
    retcode,res=set_delay(skiroc_id,delay)
    if retcode==0:
        submod.setres(0,"skiroc: cant set delay: %s"%(res))
        return
    #set fbcap
    retcode,res=set_fbcap(skiroc_id,fbcap)
    if retcode==0:
        submod.setres(0,"skiroc: cant set fbcap: %s"%(res))
        return
    #set start_ro
    retcode,res=set_start_ro(skiroc_id,start_ro)
    if retcode==0:
        submod.setres(0,"skiroc: cant set start_ro: %s"%(res))
        return
    #set end_ro
    retcode,res=set_end_ro(skiroc_id,end_ro)
    if retcode==0:
        submod.setres(0,"skiroc: cant set end_ro: %s"%(res))
        return
    #enable charge preamp
    retcode,res=enable_preamp_chans(skiroc_id,preamp)
    if retcode==0:
        submod.setres(0,"skiroc: cant enable preamp: %s"%(res))
        return
    # enable calibration capacitor
    retcode,res=enable_calib_chans(skiroc_id,calcap)
    if retcode==0:
        submod.setres(0,"skiroc: cant enable calcap: %s"%(res))
        return
    # allows to mask trigger
    retcode,res=allow_trig_chans(skiroc_id,masktrig)
    if retcode==0:
        submod.setres(0,"skiroc: cant allow to mask masktrig: %s"%(res))
        return
    # disallows to mask trigger
    retcode,res=disallow_trig_chans(skiroc_id,nomasktrig)
    if retcode==0:
        submod.setres(0,"skiroc: cant disallows to mask nomasktrig: %s"%(res))
        return
    # disable charge preamp
    retcode,res=disable_preamp_chans(skiroc_id,nopreamp)
    if retcode==0:
        submod.setres(0,"skiroc: cant disable nopreamp: %s"%(res))
        return
    # disable calibration capacitor
    retcode,res=disable_calib_chans(skiroc_id,nocalcap)
    if retcode==0:
        submod.setres(0,"skiroc: cant enable nocalcap: %s"%(res))
        return
    # select high leakage current channel
    retcode,res=select_leak_chans(skiroc_id,leak)
    if retcode==0:
        submod.setres(0,"skiroc: cant select leak: %s"%(res))
        return
    # unselect high leakage current channel
    retcode,res=unselect_leak_chans(skiroc_id,noleak)
    if retcode==0:
        submod.setres(0,"skiroc: cant select unleak: %s"%(res))
        return   
    #return result
    submod.setres(1,"ok")
