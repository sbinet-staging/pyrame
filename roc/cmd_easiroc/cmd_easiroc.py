#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Copyright 2012-2015 Frédéric Magniette, Miguel Rubio-Roy, LLR
#

import pools

import common_roc
if __name__=='__main__':
    common_roc.submod = submod

easiroc_pool=pools.pool("easiroc")

easiroc_bs_length=456

#************************* BITSTREAM MANIPULATION FUNCTIONS ***************

# **************************************************************************
# D OUTPUT
# **************************************************************************

def set_d_output(easiroc_id,value):
    return common_roc.apply_to_roc(easiroc_pool,easiroc_id,common_roc.on_off_bit,"enable/disable d output",6,value)

def set_d_output_easiroc(easiroc_id):
    "Enable digital multiplexed output (Hit mux out)"
    retcode,res = enable_d_output(easiroc_id)
    if retcode==0:
        submod.setres(0,"easiroc: %s"%(res))
        return
    submod.setres(1,res)

# **************************************************************************
# DAC CODE
# **************************************************************************

def set_dac_code(easiroc_id,dac_code):
    if dac_code!="undef":
        return common_roc.apply_to_roc(easiroc_pool,easiroc_id,common_roc.apply_mask,"set DAC code",20,common_roc.split_bin(int(dac_code),10))
    return 1,"ok"

def set_dac_code_easiroc(easiroc_id,dac_code):
    "Set 10-bit DAC code"
    retcode,res = set_dac_code(easiroc_id,dac_code)
    if retcode==0:
        submod.setres(0,"easiroc: %s"%(res))
        return
    submod.setres(1,res)

# **************************************************************************
# High gain and low gain tau
# **************************************************************************

def set_hg_tau(easiroc_id,hg_tau):
    hg_tau = int(hg_tau)
    if (hg_tau % 25) == 0 and hg_tau>=0 and hg_tau<=175:
        hg_tau = hg_tau/25
        return common_roc.apply_to_roc(easiroc_pool,easiroc_id,common_roc.apply_inv_mask,"set hg tau",71,common_roc.split_bin(hg_tau,3))
    return 0,"high-gain time constant must be a multiple of 25ns between 0 and 175ns"

def set_hg_tau_easiroc(easiroc_id,hg_tau):
    "Set high-gain time constant in ns"
    retcode,res = set_hg_tau(easiroc_id,hg_tau)
    if retcode==0:
        submod.setres(0,"easiroc: %s"%(res))
        return
    submod.setres(1,res)

# **************************************************************************

def set_lg_tau(easiroc_id,lg_tau):
    lg_tau = int(lg_tau)
    if (lg_tau % 25) == 0 and lg_tau>=0 and lg_tau<=175:
        lg_tau = lg_tau/25
        return common_roc.apply_to_roc(easiroc_pool,easiroc_id,common_roc.apply_inv_mask,"set lg tau",76,common_roc.split_bin(lg_tau,3))
    return 0,"low-gain time constant must be a multiple of 25ns between 0 and 175ns"

def set_lg_tau_easiroc(easiroc_id,lg_tau):
    "Set low-gain time constant in ns"
    retcode,res = set_lg_tau(easiroc_id,lg_tau)
    if retcode==0:
        submod.setres(0,"easiroc: %s"%(res))
        return
    submod.setres(1,res)

# **************************************************************************
# High gain compensation capacity
# **************************************************************************

def set_hg_comp_capa(easiroc_id,hg_comp_capa):
    hg_comp_capa = float(hg_comp_capa)
    if (hg_comp_capa % 0.5) == 0 and hg_comp_capa>=0 and hg_comp_capa<=7:
        hg_comp_capa = int(2 * hg_comp_capa)
        return common_roc.apply_to_roc(easiroc_pool,easiroc_id,common_roc.apply_mask,157,"set hg comp capa",common_roc.split_bin(hg_comp_capa,4))
    return 0,"high-gain preamp compensation capacitance must be a multiple of 0.5pF between 0 and 7"

def set_hg_comp_capa_easiroc(easiroc_id,hg_comp_capa):
    "Set high-gain preamp compensation capacitance in pF"
    retcode,res = set_hg_comp_capa(easiroc_id,hg_comp_capa)
    if retcode==0:
        submod.setres(0,"easiroc: %s"%(res))
        return
    submod.setres(1,res)

# **************************************************************************
# High gain feedback capacity
# **************************************************************************

def set_hg_fb_capa(easiroc_id,hg_fb_capa):
    hg_fb_capa = float(hg_fb_capa)
    if (hg_fb_capa % 0.1) == 0 and hg_fb_capa>=0.1 and hg_fb_capa<=1.5:
        hg_fb_capa = int(15 - 10 * hg_fb_capa)
        return common_roc.apply_to_roc(easiroc_pool,easiroc_id,common_roc.apply_mask,153,"set hg feedback capa",common_roc.split_bin(hg_fb_capa,4))
    return 0,"high-gain preamp feedback capacitance must be a multiple of 0.1pF between 0.1pF and 1.5pF"

def set_hg_fb_capa_easiroc(easiroc_id,hg_fb_capa):
    "Set high-gain preamp feedback capacitance in pF"
    retcode,res = set_hg_fb_capa(easiroc_id,hg_fb_capa)
    if retcode==0:
        submod.setres(0,"easiroc: %s"%(res))
        return
    submod.setres(1,res)

# **************************************************************************
# Low gain compensation capacity
# **************************************************************************

def set_lg_comp_capa(easiroc_id,lg_comp_capa):
    lg_comp_capa = float(lg_comp_capa)
    if (lg_comp_capa % 0.5) == 0 and lg_comp_capa>=0 and lg_comp_capa<=7:
        lg_comp_capa = int(2 * lg_comp_capa)
        return common_roc.apply_to_roc(easiroc_pool,easiroc_id,common_roc.apply_inv_mask,145,"set lg comp capa",common_roc.split_bin(lg_comp_capa,4))
    return 0,"low-gain preamp compensation capacitance must be a multiple of 0.5pF between 0pF and 7pF"

def set_lg_comp_capa_easiroc(easiroc_id,lg_comp_capa):
    "Set low-gain preamp compensation capacitance in pF"
    retcode,res = set_lg_comp_capa(easiroc_id,lg_comp_capa)
    if retcode==0:
        submod.setres(0,"easiroc: %s"%(res))
        return
    submod.setres(1,res)

# **************************************************************************
# Low gain feedback capacity
# **************************************************************************

def set_lg_fb_capa(easiroc_id,lg_fb_capa):
    lg_fb_capa = float(lg_fb_capa)
    if (lg_fb_capa % 0.1) == 0 and lg_fb_capa>=0.1 and lg_fb_capa<=1.5:
        lg_fb_capa = int(15 - 10 * lg_fb_capa)
        return common_roc.apply_to_roc(easiroc_pool,easiroc_id,common_roc.apply_inv_mask,149,common_roc.split_bin(lg_fb_capa,4))
    return 0,"low-gain preamp feedback capacitance must be a multiple of 0.1pF between 0.1pF and 1.5pF"

def set_lg_fb_capa_easiroc(easiroc_id,lg_fb_capa):
    "Set low-gain preamp feedback capacitance in pF"
    retcode,res = set_lg_fb_capa(easiroc_id,lg_fb_capa)
    if retcode==0:
        submod.setres(0,"easiroc: %s"%(res))
        return
    submod.setres(1,res)

# **************************************************************************
# Low gain preamp bias
# **************************************************************************

def set_lg_preamp_bias(easiroc_id,value):
    if value=="undef":
        return 1,"ok"
    if value=="high":
        value = "0"
    elif value=="weak":
        value = "1"
    else:
        return 0,"invalid state of lg preamp bias (high/weak): %s"%(value)
    return common_roc.apply_to_roc(easiroc_pool,easiroc_id,common_roc.apply_mask,"set state of lg preamp bias",165,value)

def set_lg_preamp_bias_easiroc(easiroc_id):
    "Set low gain preamp bias to high"
    retcode,res = set_lg_preamp_bias(easiroc_id)
    if retcode==0:
        submod.setres(0,"easiroc: %s"%(res))
        return
    submod.setres(1,res)

# **************************************************************************
# DAC data
# **************************************************************************

def set_dac_data(easiroc,chan,value):
    common_roc.apply_mask(easiroc,166+288-9*(int(chan)+1)+1,common_roc.split_bin(dac_data_value,8))
    return 1,"ok"

def set_dac_data_chans(easiroc_id,chans,value):
    return common_roc.apply_to_chans(easiroc_pool,easiroc_id,chans,set_dac_data,"set dac data",value)

def set_dac_data_chans_easiroc(easiroc_id,chans,value):
    "Set DAC data for one or several channels"
    retcode,res = set_dac_data_chans(easiroc_id,chans,value)
    if retcode==0:
        submod.setres(0,"easiroc: %s"%(res))
        return
    submod.setres(1,res)

# **************************************************************************

def enable_dac_data(easiroc,chan):
    return common_roc.on_off_bit(easiroc,166+288-9*(int(chan)+1),1)

def enable_dac_data_chans(easiroc_id,chans):
    return common_roc.apply_to_chans(easiroc_pool,easiroc_id,chans,enable_dac_data,"enable dac data")

def enable_dac_data_chans_easiroc(easiroc_id,chans):
    "Enable DAC data for one or several channels"
    retcode,res = enable_dac_data_chans(easiroc_id,chans)
    if retcode==0:
        submod.setres(0,"easiroc: %s"%(res))
        return
    submod.setres(1,res)

# **************************************************************************

def disable_dac_data(easiroc_id,chan):
    return common_roc.on_off_bit(easiroc,166+288-9*(int(chan)+1),0)

def disable_dac_data_chans(easiroc_id,chans):
    return common_roc.apply_to_chans(easiroc_pool,easiroc_id,chans,disable_dac_data,"disable dac data")

def disable_dac_data_chans_easiroc(easiroc_id,chans):
    "Disable DAC data for one or several channels"
    retcode,res = disable_dac_data_chans(easiroc_id,chans)
    if retcode==0:
        submod.setres(0,"easiroc: %s"%(res))
        return
    submod.setres(1,res)

#********************************** GENERAL PUBLIC FUNCTIONS ***************

def dump_sc_easiroc(easiroc_id):
    "Returns bitstream of *easiroc_id* in binary format"
    try:
        easiroc = easiroc_pool.get(easiroc_id)
    except Exception as e:
        submod.setres(0,"easiroc: easiroc_%s" % (str(e)))
        return
    #return the bitstream
    bitstream = easiroc["bitstream"] if not easiroc["missing"] else ""
    submod.setres(1,bitstream)

def set_missing_easiroc(easiroc_id,missing):
    "Set easiroc missing state"
    try:
        easiroc = easiroc_pool.get(easiroc_id)
    except Exception as e:
        submod.setres(0,"easiroc: easiroc_%s" % (str(e)))
        return
    easiroc["missing"] = True if missing=="1" else False
    submod.setres(1,"ok")

def explain_sc_easiroc(easiroc_id):
    "Give meaningful strings of the configurable portions of the bitstream"
    try:
        easiroc = easiroc_pool.get(easiroc_id)
    except Exception as e:
        submod.setres(0,"easiroc: easiroc_%s" % (str(e)))
        return

    print("Binary values are printed as they are in the chip (reverse of injected)")

    state = "enabled (1)" if easiroc["bitstream"][6] == "1" else "disabled (0)"
    print("Digital multiplexed output (hit mux out): " + state)
    
    value = ""
    for i in range(10): value += easiroc["bitstream"][29-i]
    print("10-bit DAC = {0} ({1} LSB-MSB)".format(int(value[::-1],2),value))
    
    value = ""
    for i in range(3):  value += easiroc["bitstream"][73-i]
    print("High gain shaper time constant = {0} ns ({1} MSB-LSB)".format(int(value,2)*25,value))

    value = ""
    for i in range(3):  value += easiroc["bitstream"][78-i]
    print("Low gain shaper time constant = {0} ns ({1} MSB-LSB)".format(int(value,2)*25,value))

    value = ""
    for i in range(4):  value += easiroc["bitstream"][148-i]
    print("Low gain preamp compensation capacitances = {0} pF ({1} MSB-LSB)".format(int(value,2)*0.5,value))

    value = ""
    for i in range(4):  value += easiroc["bitstream"][152-i]
    print("Low gain preamp feedback capacitances = {0} pF ({1} MSB-LSB)".format(1.5-int(value,2)*0.1,value))

    value = ""
    for i in range(4):  value += easiroc["bitstream"][156-i]
    print("High gain preamp feedback capacitances = {0} pF ({1} LSB-MSB)".format(1.5-int(value[::-1],2)*0.1,value))

    value = ""
    for i in range(4):  value += easiroc["bitstream"][160-i]
    print("High gain preamp compensation capacitances = {0} pF ({1} LSB-MSB)".format(int(value[::-1],2)*0.5,value))

    state = "weak (1)" if easiroc["bitstream"][6] == "1" else "high (0)"
    print("Low gain preamp bias: " + state)
    
    submod.setres(1,"ok")

#****************************** PHASES *************************************

def init_easiroc(parent_device,dev_name):
    "Initialize an easiroc"
    #register in the config module
    retcode,res=submod.execcmd("new_device_cmod","easiroc",dev_name,parent_device)
    if retcode==0:
        submod.setres(0,"easiroc: cant register in cmod <- %s"%(res))
        return
    easiroc_id=res
    easiroc_pool.new({},easiroc_id)
    #send back the id
    submod.setres(1,easiroc_id)

def deinit_easiroc(easiroc_id):
    "Deinitialize *easiroc_id*"
    try:
        easiroc = easiroc_pool.get(easiroc_id)
    except Exception as e:
        submod.setres(1,"easiroc: easiroc_%s" % (str(e)))
        return
    easiroc_pool.remove(easiroc_id)
    submod.setres(1,"ok")

def config_easiroc(easiroc_id,filename,bitstream,d_output,dac_code,hg_tau,lg_tau,hg_comp_capa,hg_fb_capa,lg_comp_capa,lg_fb_capa,lg_preamp_bias):
    "Prepare the bitstream for configuring a chip"
    try:
        easiroc = easiroc_pool.get(easiroc_id)
    except Exception as e:
        submod.setres(0,"easiroc: easiroc_%s" % (str(e)))
        return
    easiroc["missing"] = False
    #empty the bitstream
    easiroc["bitstream"]=""
    #load bitstream
    if bitstream!="undef":
        retcode,res=common_roc.load_str(bitstream,easiroc_bs_length)
        if retcode==0:
            submod.setres(0,"easiroc: cant parse bitstream: %s"%(res))
            return
        easiroc["bitstream"]=res
    #load bitstream from file
    if file!="undef":
        retcode,res=common_roc.load_file(file,easiroc_bs_length)
        if retcode==0:
            submod.setres(0,"easiroc: cant open config file: %s"%(res))
            return
        easiroc["bitstream"]=res
    if easiroc["bitstream"]=="":
        submod.setres(0,"easiroc: no bitstream defined for easiroc %s"%(easiroc_id))
        return

    retcode,res=set_d_output(easiroc_id,d_output)
    if retcode==0:
        submod.setres(0,"easiroc: %s"%(res))
        return

    retcode,res=set_dac_code(easiroc_id,dac_code)
    if retcode==0:
        submod.setres(0,"easiroc: %s"%(res))
        return

    retcode,res=set_hg_tau(easiroc_id,hg_tau)
    if retcode==0:
        submod.setres(0,"easiroc: %s"%(res))
        return

    retcode,res=set_lg_tau(easiroc_id,lg_tau)
    if retcode==0:
        submod.setres(0,"easiroc: %s"%(res))
        return

    retcode,res=set_hg_comp_capa(easiroc_id,hg_comp_capa)
    if retcode==0:
        submod.setres(0,"easiroc: %s"%(res))
        return

    retcode,res=set_hg_fb_capa(easiroc_id,hg_fb_capa)
    if retcode==0:
        submod.setres(0,"easiroc: %s"%(res))
        return

    retcode,res=set_lg_comp_capa(easiroc_id,lg_comp_capa)
    if retcode==0:
        submod.setres(0,"easiroc: %s"%(res))
        return

    retcode,res=set_lg_fb_capa(easiroc_id,lg_fb_capa)
    if retcode==0:
        submod.setres(0,"easiroc: %s"%(res))
        return

    retcode,res=set_high_lg_preamp_bias(easiroc_id)
    if retcode==0:
        submod.setres(0,"easiroc: %s"%(res))
        return

    submod.setres(1,"ok")
