

def init_domain(parent_device,dev_name,ip):
    #register in the config module
    retcode,res=submod.execcmd("new_device_cmod","domain",dev_name,parent_device)
    if retcode==0:
        submod.setres(0,"domain: cant register in cmod <- %s"%(res))
        return
    config_id=res

    retcode,res=submod.execcmd("set_param_cmod",config_id,"domain_ip",ip)
    
    #return config_id
    submod.setres(1,config_id)
