#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Copyright 2012-2015 Frédéric Magniette, Miguel Rubio-Roy, LLR
#

import pools

import common_roc
if __name__=='__main__':
    common_roc.submod = submod

maroc3_pool=pools.pool("maroc3")

maroc3_bs_length=829

#************************* BITSTREAM MANIPULATION FUNCTIONS ***************

# **************************************************************************
# Powerpulsing bandgap
# **************************************************************************

def set_pp_bandgap(maroc3_id,value):
    return common_roc.apply_to_roc(maroc3_pool,maroc3_id,common_roc.on_off_bit,"enable/disable power pulsing for bandgap",0,value)

def set_pp_bandgap_maroc3(maroc3_id,value):
    "Activate (ON or 1) or desactivate (OFF or 0) power pulsing (pp) for bandgap"
    retcode,res = set_pp_bandgap(maroc3_id,value)
    if retcode==0:
        submod.setres(0,"maroc3: %s"%(res))
    submod.setres(1,res)

# **************************************************************************
# Powerpulsing DACs
# **************************************************************************

def set_pp_dacs(maroc3_id,value):
    return common_roc.apply_to_roc(maroc3_pool,maroc3_id,common_roc.on_off_bit,"enable/disable power pulsing for all DACs",1,value)

def set_pp_dacs_maroc3(maroc3_id,value):
    "Activate (ON or 1) or desactivate (OFF or 0) power pulsing (pp) for all DACs"
    retcode,res = set_pp_dacs(maroc3_id,value)
    if retcode==0:
        submod.setres(0,"maroc3: %s"%(res))
    submod.setres(1,res)

# **************************************************************************
# Small DAC
# **************************************************************************

def set_small_dac(maroc3_id,value):
    return common_roc.apply_to_roc(maroc3_pool,maroc3_id,common_roc.on_off_bit,"decrease/keep slope of DAC0",2,value)

def set_small_dac_maroc3(maroc3_id,value):
    "Decrease (ON or 1) or not (OFF or 0) the slope of DAC0 to have better accuracy."
    retcode,res = set_small_dac(maroc3_id,value)
    if retcode==0:
        submod.setres(0,"maroc3: %s"%(res))
    submod.setres(1,res)

# **************************************************************************
# DAC values
# **************************************************************************

def set_dac0(maroc3_id,value):
    if value!="undef":
        return common_roc.apply_to_roc(maroc3_pool,maroc3_id,common_roc.apply_mask,"set DAC0 value",13,common_roc.split_bin(int(value),10))
    return 1,"ok"

def set_dac0_maroc3(maroc3_id,value):
    "Set DAC0 (first discriminator) *value* (integer in 10-bit)"
    retcode,res = set_dac0(maroc3_id,value)
    if retcode==0:
        submod.setres(0,"maroc3: %s"%(res))
    submod.setres(1,res)

# **************************************************************************

def set_dac1(maroc3_id,value):
    if value!="undef":
        return common_roc.apply_to_roc(maroc3_pool,maroc3_id,common_roc.apply_mask,"set DAC1 value",3,common_roc.split_bin(int(value),10))
    return 1,"ok"

def set_dac1_maroc3(maroc3_id,value):
    "Set DAC1 (second discriminator) *value* (integer in 10-bit)"
    retcode,res = set_dac1(maroc3_id,value)
    if retcode==0:
        submod.setres(0,"maroc3: %s"%(res))
    submod.setres(1,res)

# **************************************************************************
# Wilkinson ADC
# **************************************************************************

def set_data_output_wlk(maroc3_id,value):
    return common_roc.apply_to_roc(maroc3_pool,maroc3_id,common_roc.on_off_bit,"set ADC data output",23,value)

def set_data_output_wlk_maroc3(maroc3_id,value):
    "Enable (ON or 1) or disable (OFF or 0) data output. Must be OFF to use the Wilkinson ADC"
    retcode,res = set_data_output_wlk(maroc3_id,value)
    if retcode==0:
        submod.setres(0,"maroc3: %s"%(res))
    submod.setres(1,res)

# **************************************************************************

def set_inv_start_counter_wlk(maroc3_id,value):
    return common_roc.apply_to_roc(maroc3_pool,maroc3_id,common_roc.on_off_bit,"set start counter polarity switching",24,value)

def set_inv_start_counter_wlk_maroc3(maroc3_id,value):
    "Set the start counter polarity switching"
    retcode,res = set_inv_start_counter_wlk(maroc3_id,value)
    if retcode==0:
        submod.setres(0,"maroc3: %s"%(res))
    submod.setres(1,res)

# **************************************************************************

def set_8bit_ramp_wlk(maroc3_id,value):
    return common_roc.apply_to_roc(maroc3_pool,maroc3_id,common_roc.on_off_bit,"set 8bit ramp slope",25,value)

def set_8bit_ramp_wlk_maroc3(maroc3_id,value):
    "Set 8bit ramp slope"
    retcode,res = set_8bit_ramp_wlk(maroc3_id,value)
    if retcode==0:
        submod.setres(0,"maroc3: %s"%(res))
    submod.setres(1,res)

# **************************************************************************

def set_10bit_ramp_wlk(maroc3_id,value):
    return common_roc.apply_to_roc(maroc3_pool,maroc3_id,common_roc.on_off_bit,"set 10bit ramp slope",26,value)

def set_10bit_ramp_wlk_maroc3(maroc3_id,value):
    "Set 10bit ramp slope"
    retcode,res = set_10bit_ramp_wlk(maroc3_id,value)
    if retcode==0:
        submod.setres(0,"maroc3: %s"%(res))
    submod.setres(1,res)

# **************************************************************************
# Discriminator outputs
# **************************************************************************

def mask_or1(maroc3,chan):
    return common_roc.on_off_bit(maroc3,28+(63-chan)*2,1)

def mask_or1_chans(maroc3_id,chans):
    return common_roc.apply_to_chans(maroc3_pool,maroc3_id,chans,mask_or1,"mask OR1")

def mask_or1_chans_maroc3(maroc3_id,chans):
    "Mask channels *chans* (no trigger output) on the first discriminator (OR1)"
    retcode,res = mask_or1_chans(maroc3_id,chans)
    if retcode==0:
        submod.setres(0,"maroc3: %s"%(res))
    submod.setres(1,res)

# **************************************************************************

def unmask_or1(maroc3,chan):
    return common_roc.on_off_bit(maroc3,28+(63-chan)*2,0)

def unmask_or1_chans(maroc3_id,chans):
    return common_roc.apply_to_chans(maroc3_pool,maroc3_id,chans,unmask_or1,"unmask OR1")

def unmask_or1_maroc3(maroc3_id,chans):
    "Unmask channels *chans* (trigger output visible) on the first discriminator (OR1)"
    retcode,res = unmask_or1_chans(maroc3_id,chans)
    if retcode==0:
        submod.setres(0,"maroc3: %s"%(res))
    submod.setres(1,res)

# **************************************************************************

def mask_or2(maroc3,chan):
    return common_roc.on_off_bit(maroc3,27+(63-chan)*2,1)

def mask_or2_chans(maroc3_id,chans):
    return common_roc.apply_to_chans(maroc3_pool,maroc3_id,chans,mask_or2,"mask OR2")

def mask_or2_chans_maroc3(maroc3_id,chans):
    "Mask channels *chans* (no trigger output) on the first discriminator (OR2)"
    retcode,res = mask_or2_chans(maroc3_id,chans)
    if retcode==0:
        submod.setres(0,"maroc3: %s"%(res))
    submod.setres(1,res)

# **************************************************************************

def unmask_or2(maroc3,chan):
    return common_roc.on_off_bit(maroc3,27+(63-chan)*2,0)

def unmask_or2_chans(maroc3_id,chans):
    return common_roc.apply_to_chans(maroc3_pool,maroc3_id,chans,unmask_or2,"unmask OR2")

def unmask_or2_maroc3(maroc3_id,chans):
    "Unmask channels *chans* (trigger output visible) on the first discriminator (OR2)"
    retcode,res = unmask_or2_chans(maroc3_id,chans)
    if retcode==0:
        submod.setres(0,"maroc3: %s"%(res))
    submod.setres(1,res)

# **************************************************************************
# 33 bits 156 to 188
# **************************************************************************

def set_156_to_188(maroc3_id,value):
    if value=="undef":
        return 1,"ok"
    retcode,res = common_roc.load_str(value,33,True)
    if retcode==0:
        return 0,"Error reading value to be applied: %s"%(res)
    return common_roc.apply_to_roc(maroc3_pool,maroc3_id,common_roc.apply_mask,"set 156 to 188 bits",156,res)

def set_156_to_188_maroc3(maroc3_id,value):
    "Set value of the 33bits ranging from the bit 156 to 188. *value* has bitstream format (hexadecimal preceded by 0x, binary by 0b or decimal integer."
    retcode,res = set_156_to_188(maroc3_id,value)
    if retcode==0:
        submod.setres(0,"maroc3: %s"%(res))
    submod.setres(1,res)

# **************************************************************************
# Preamps gains
# **************************************************************************

def set_preamp_gain(maroc3,chan,value):
    return common_roc.apply_mask(maroc3,190+(63-chan)*9,common_roc.split_bin(value,8))

def set_preamp_gain_chans(maroc3_id,chans,value):
    return common_roc.apply_to_chans(maroc3_pool,maroc3_id,chans,set_preamp_gain,"preamp gain",value)

def set_preamp_gain_chans_maroc3(maroc3_id,chans,value):
    "Set preamp gain for channels *chans*. 8-bit *value*"
    retcode,res = set_preamp_gain_chans(maroc3_id,chans,value)
    if retcode==0:
        submod.setres(0,"maroc3: %s"%(res))
    submod.setres(1,res)

# **************************************************************************

def enable_sum(maroc3,chan):
    return common_roc.on_off_bit(maroc3,189+(63-chan)*9,1)

def enable_sum_chans(maroc3_id,chans):
    return common_roc.apply_to_chans(maroc3_pool,maroc3_id,chans,enable_sum,"enable signal for sum")

def enable_sum_chans_maroc3(maroc3_id,chans):
    "Enable signal from channel *chan* for sum"
    retcode,res = enable_sum_chans(maroc3_id,chans)
    if retcode==0:
        submod.setres(0,"maroc3: %s"%(res))
    submod.setres(1,res)

# **************************************************************************

def disable_sum(maroc3,chan):
    return common_roc.on_off_bit(maroc3,189+(63-chan)*9,0)

def disable_sum_chans(maroc3_id,chans):
    return common_roc.apply_to_chans(maroc3_pool,maroc3_id,chans,disable_sum,"disable signal for sum")

def disable_sum_chans_maroc3(maroc3_id,chans):
    "Disable signal from channel *chan* for sum"
    retcode,res = disable_sum_chans(maroc3_id,chans)
    if retcode==0:
        submod.setres(0,"maroc3: %s"%(res))
    submod.setres(1,res)

# **************************************************************************
# Ctest input
# **************************************************************************

def enable_ctest(maroc3,chan):
    return common_roc.on_off_bit(maroc3,765+(63-chan),1)

def enable_ctest_chans(maroc3_id,chans):
    return common_roc.apply_to_chans(maroc3_pool,maroc3_id,chans,enable_ctest,"enable signal in ctest input")

def enable_ctest_chans_maroc3(maroc3_id,chans):
    "Enable signal from channel *chan* in Ctest input"
    retcode,res = enable_ctest_chans(maroc3_id,chans)
    if retcode==0:
        submod.setres(0,"maroc3: %s"%(res))
    submod.setres(1,res)

# **************************************************************************

def disable_ctest(maroc3,chan):
    return common_roc.on_off_bit(maroc3,765+(63-chan),0)

def disable_ctest_chans(maroc3_id,chans):
    return common_roc.apply_to_chans(maroc3_pool,maroc3_id,chans,disable_ctest,"disable signal in ctest input")

def disable_ctest_chans_maroc3(maroc3_id,chans):
    "Disable signal from channel *chan* in Ctest input"
    retcode,res = disable_ctest_chans(maroc3_id,chans)
    if retcode==0:
        submod.setres(0,"maroc3: %s"%(res))
    submod.setres(1,res)

#********************************** GENERAL PUBLIC FUNCTIONS ***************

def dump_sc_maroc3(maroc3_id):
    "Returns bitstream of *maroc3_id* in binary format"
    try:
        maroc3 = maroc3_pool.get(maroc3_id)
    except Exception as e:
        submod.setres(0,"maroc3: maroc3_%s" % (str(e)))
        return
    #return the bitstream
    bitstream = maroc3["bitstream"] if not maroc3["missing"] else ""
    print("bitstream length: %d"%(len(bitstream)))
    bitstream = "0"*107 + bitstream
    print("padding to match spiroc length...")
    print("bitstream length: %d"%(len(bitstream)))
    submod.setres(1,bitstream)

def set_missing_maroc3(maroc3_id,missing):
    "Set maroc3 missing state"
    try:
        maroc3 = maroc3_pool.get(maroc3_id)
    except Exception as e:
        submod.setres(0,"maroc3: maroc3_%s" % (str(e)))
        return
    maroc3["missing"] = True if missing=="1" else False
    submod.setres(1,"ok")

#****************************** PHASES *************************************

def init_maroc3(parent_device,dev_name):
    "Initialize a maroc3"
    #register in the config module
    retcode,res=submod.execcmd("new_device_cmod","maroc3",dev_name,parent_device)
    if retcode==0:
        submod.setres(0,"maroc3: cant register in cmod <- %s"%(res))
        return
    maroc3_id=res
    maroc3_pool.new({},maroc3_id)
    #send back the id
    submod.setres(1,maroc3_id)

def deinit_maroc3(maroc3_id):
    "Deinitialize *maroc3_id*"
    try:
        maroc3 = maroc3_pool.get(maroc3_id)
    except Exception as e:
        submod.setres(1,"maroc3: maroc3_%s" % (str(e)))
        return
    maroc3_pool.remove(maroc3_id)
    submod.setres(1,"ok")

def config_maroc3(maroc3_id,file,bitstream,pp_bandgap,pp_dacs,small_dac,dac0,dac1,wlk_out_adc,wlk_inv_counter,wlk_ramp_8bit,wlk_ramp_10bit,from_156_to_188):
    "Prepare the bitstream for configuring a chip"
    try:
        maroc3 = maroc3_pool.get(maroc3_id)
    except Exception as e:
        submod.setres(0,"maroc3: maroc3_%s" % (str(e)))
        return
    maroc3["missing"] = False
    #empty the bitstream
    maroc3["bitstream"]=""
    #load bitstream
    if bitstream!="undef":
        retcode,res=common_roc.load_str(bitstream,maroc3_bs_length,True)
        if retcode==0:
            submod.setres(0,"maroc3: cant parse bitstream: %s"%(res))
            return
        maroc3["bitstream"]=res
    #load bitstream from file
    if file!="undef":
        retcode,res=common_roc.load_file(file,maroc3_bs_length,True)
        if retcode==0:
            submod.setres(0,"maroc3: cant open config file: %s"%(res))
            return
        maroc3["bitstream"]=res
    if maroc3["bitstream"]=="":
        submod.setres(0,"maroc3: no bitstream defined for maroc3 %s"%(maroc3_id))
        return
    # set pp gandagp
    retcode,res = set_pp_bandgap(maroc3_id,pp_bandgap)
    if retcode==0:
        submod.setres(0,"maroc3: %s"%(res))
        return
    # set pp dacs
    retcode,res = set_pp_dacs(maroc3_id,pp_dacs)
    if retcode==0:
        submod.setres(0,"maroc3: %s"%(res))
        return
    # set small dac value 
    retcode,res = set_small_dac(maroc3_id,small_dac)
    if retcode==0:
        submod.setres(0,"maroc3: %s"%(res))
        return
    # set dac0 value 
    retcode,res = set_dac0(maroc3_id,dac0)
    if retcode==0:
        submod.setres(0,"maroc3: %s"%(res))
        return
    # set dac1 value 
    retcode,res = set_dac1(maroc3_id,dac1)
    if retcode==0:
        submod.setres(0,"maroc3: %s"%(res))
        return
    # set Wilkinson data output 
    retcode,res = set_data_output_wlk(maroc3_id,wlk_out_adc)
    if retcode==0:
        submod.setres(0,"maroc3: %s"%(res))
        return
    # set Wilkinson invert counter 
    retcode,res = set_inv_start_counter_wlk(maroc3_id,wlk_inv_counter)
    if retcode==0:
        submod.setres(0,"maroc3: %s"%(res))
        return
    # set 8bit Wilkinson ramp
    retcode,res = set_8bit_ramp_wlk(maroc3_id,wlk_ramp_8bit)
    if retcode==0:
        submod.setres(0,"maroc3: %s"%(res))
        return
    # set 10bit Wilkinson ramp
    retcode,res = set_10bit_ramp_wlk(maroc3_id,wlk_ramp_10bit)
    if retcode==0:
        submod.setres(0,"maroc3: %s"%(res))
        return
    # set bits from 156 to 188 (33bits)
    retcode,res = set_156_to_188(maroc3_id,from_156_to_188)
    if retcode==0:
        submod.setres(0,"maroc3: %s"%(res))
        return
    #return result
    submod.setres(1,"ok")
