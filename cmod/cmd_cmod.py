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

class node:
    def __init__(self,dev_id,dev_name,dev_type,parent):
        self.id=dev_id
        self.name=dev_name
        self.type=dev_type
        self.childs=[]
        self.params={}
        self.parent=parent

root=node("0","root","root",None)
id_counter=1

def deinit_cmod():
    "Deinitialize cmod"
    global root
    root.childs=[]
    root.params={}
    submod.setres(1,"ok")

def get_new_id():
    """allocate a new id for a new device"""
    global id_counter
    res=str(id_counter)
    id_counter=id_counter+1
    return res

def find_by_id(node,id):
    """search a node with a specified id in a subtree"""
    if id==node.id:
        return node
    for child in node.childs:
        if child.id==id:
            return child
    for child in node.childs:
        res=find_by_id(child,id)
        if res!=-1:
            return res
    return -1

def find_by_name(node,name):
    """search a node with a specified name in a subtree"""
    if name==node.name:
        return node
    for child in node.childs:
        if child.name==name:
            return child
    for child in node.childs:
        res=find_by_name(child,name)
        if res!=-1:
            return res
    return -1

def gener_config_node(node):
    res="<%s name=\"%s\">"%(node.type,node.name)
    for name,value in node.params.items():
        res=res+"<param name=\"%s\">%s</param>"%(name,value)
    for child in node.childs:
        res=res+gener_config_node(child)
    res=res+"</%s>"%(node.type)
    return res
            
def gener_config_cmod():
    """extract the configuration from the tree and aggregate it in a XML file"""
    global root
    res="<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    #res=res+gener_config_node(root)
    for child in root.childs:
        res=res+gener_config_node(child)
    submod.setres(1,res)

def new_device_cmod(dev_type,dev_name,parent_id):
    """add a device in the tree"""
    global root
    double=find_by_name(root,dev_name)
    if double!=-1:
        submod.setres(0,"cmod: there is already a device with that name %s"%(dev_name))
        return 
    parent=find_by_id(root,parent_id)
    if parent==-1:
        submod.setres(0,"cmod: unknown parent_id %s"%(parent_id))
        return
    newid=get_new_id()
    newnode=node(newid,dev_name,dev_type,parent)
    parent.childs.append(newnode)
    submod.setres(1,newid)
                
def set_param_cmod(id,param_name,param_value):
    """add a param to a device"""
    global root
    device=find_by_id(root,id)
    if device==-1:
        submod.setres(0,"cmod: unknown device id %s"%(id))
        return
    device.params[param_name]=param_value
    submod.setres(1,"ok")

def get_param_cmod(dev_name,param_name):
    """get a param for a device"""
    global root
    device=find_by_name(root,dev_name)
    if device==-1:
        submod.setres(0,"cmod: unknown device id %s"%(id))
        return
    if param_name in device.params:
        submod.setres(1,device.params[param_name])
    else:
        submod.setres(0,"cmod: unknown param")

def get_id_cmod(dev_name):
    """find the id of a device by its name"""
    global root
    device=find_by_name(root,dev_name)
    if device==-1:
        submod.setres(0,"cmod: unknown device name %s"%(dev_name))
        return
    submod.setres(1,device.id)

def get_type_cmod(dev_name):
    """find the type of a device by its name"""
    global root
    device=find_by_name(root,dev_name)
    if device==-1:
        submod.setres(0,"cmod: unknown device name %s"%(dev_name))
        return
    submod.setres(1,device.type)

def get_ip_byname_cmod(dev_name):
    """find the ip of a device by its name"""
    global root
    device=find_by_name(root,dev_name)
    if device==-1:
        submod.setres(0,"cmod: unknown device name %s"%(dev_name))
        return
    parent=device.parent
    while parent!=None and parent.type!="domain":
        parent=parent.parent
    if parent==None:
        submod.setres(0,"cmod: no domain found")
        return
    submod.setres(1,parent.params["domain_ip"])
  
def get_ip_byid_cmod(dev_id):
    """find the ip of a device by its id"""
    global root 
    device=find_by_id(root,dev_id)
    if device==-1:
        submod.setres(0,"cmod: unknown device id %s"%(dev_id))
        return
    parent=device.parent
    while parent!=None and parent.type!="domain":
        parent=parent.parent
    if parent==None:
        submod.setres(0,"cmod: no domain found")
        return
    submod.setres(1,parent.params["domain_ip"])

def get_name_list_node(node,dev_type):
    """get the list of device names of a *dev_type* type in a subtree"""
    res=""
    if node.type==dev_type:
        res="%s"%(node.name)
    for child in node.childs:
        tmp=get_name_list_node(child,dev_type)
        if tmp!="":
            if res=="":
                res=tmp
            else:
                res=res+",%s"%(tmp)
    return res

def get_id_list_node(node,dev_type):
    """get the list of device id of a *dev_type* type in a subtree"""
    res=""
    if node.type==dev_type:
        res="%s"%(node.id)
    for child in node.childs:
        tmp=get_id_list_node(child,dev_type)
        if tmp!="":
            if res=="":
                res=tmp
            else:
                res=res+",%s"%(tmp)
    return res

def get_name_sublist_cmod(dev_type,parent_name):
    """get the list of device names of a *dev_type* type with *parent_name* parent"""
    global root
    parent=find_by_name(root,parent_name)
    if parent==-1:
        submod.setres(0,"cmod: unknown parent name %s"%(parent_name))
        return
    submod.setres(1,get_name_list_node(parent,dev_type))

def get_id_sublist_cmod(dev_type,parent_id):
    """get the list of device id of a *dev_type* type with *parent_name* parent"""
    global root
    parent=find_by_id(root,parent_id)
    if parent==-1:
        submod.setres(0,"cmod: unknown parent id %s"%(parent_id))
        return
    submod.setres(1,get_id_list_node(parent,dev_type))

def get_name_list_cmod(dev_type):
    """get the list of all device names of a *dev_type*"""
    global root
    submod.setres(1,get_name_list_node(root,dev_type))

def get_id_list_cmod(dev_type):
    """get the list of all device id of a *dev_type*"""
    global root
    submod.setres(1,get_id_list_node(root,dev_type))
