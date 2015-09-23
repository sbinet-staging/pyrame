
config_id=0


#***************************** CALXML FUNCTIONS *****************************

def init_detector(dev_name):
    """initialize the detector memory structure"""
    global config_id

    #register in the config module
    retcode,res=submod.execcmd("new_device_cmod","detector",dev_name,"0")
    if retcode==0:
        submod.setres(0,"detector: cant register in cmod : %s"%(res))
        return

    config_id=res
    #return config_id
    submod.setres(1,config_id)


