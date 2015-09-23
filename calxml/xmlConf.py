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

import re
import xml.parsers.expat
import apc

_verbose=False

def strip_file(filename):
    try:
        file = open(filename,'read')
            
        #create the String structure to get the file content
        Str=""

        #read data from file and strip it
        for line in file.readlines():
            line_stripped = line.lstrip(' ').rstrip(' ')
            line_stripped = line_stripped.lstrip(' \t')
            line_stripped = line_stripped.rstrip(' \n')
            Str=Str+line_stripped
            
        file.close()
        return Str
    except:
        return ""


class EmptyStackException(Exception):
    def __init__(self, comment):
        Exception.__init__(self)
        self.comment = comment
	
class XmlParamException(Exception):
    def __init__(self, value,comment):
        Exception.__init__(self)
	self.value = value
        self.comment = comment
	self.comment = self.comment+ self.value
	
class AcqException(Exception):
    def __init__(self,comment):
        Exception.__init__(self)
        self.comment = comment
   

class Stack:
    #constructeur pile
    def __init__(self):
        self.items = []

    def push(self, item) :
        self.items.append(item)
	tag,attrName,level = self.getLastItem()
	#flag = True
	#if flag:
	if _verbose:
	    if not 'completed' in tag and type(level)==int:
	        print 'stack = ',tag,attrName,level

    def pop(self) :
        if self.isEmpty():
            raise EmptyStackException("stack empty - pop action unavailable")
        return self.items.pop()

    def isEmpty(self) :
        return (self.items == []) 
	
    def getLastItem(self):
        return self.items[-1] 
		
	
	 
class Configuration:
    #constructeur : initialise les attributs
    def __init__(self,title) :
        self.name = title
        self.allDicos = {}

    
	

    def addDict(self,dico,dicoLevel):
	self.allDicos[dicoLevel ] = dico
	#if dicoLevel == 1 :   
	if _verbose :
	    self.printDico(dicoLevel)
	    
	
	
    def getLastDico(self,key):
        import copy
        copyDico = copy.deepcopy(self.allDicos[key])
	printFlag = False
	if printFlag :
	    print '---------------------------------getLastDico----key =',key
	    self.printDico(key)
	    print '------------------fin copyDico ------------'
	return copyDico



	       	   
    def printDico(self,dicoLevel) :
        for key,value in self.allDicos.items() :
	   if key == dicoLevel :
	      print '-----------DICO LEVEL = ',dicoLevel
	      for keyy in sorted(value.iterkeys()) :
	         print "%s: %s" % (keyy,value[keyy]) 
		 
    def printAll(self) :
	print '&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&'
	print self.allDicos
	print '&&&&&&&&&&&&&&&&&&&&&&&&&end myprint&&&&&&&&&&&&&&&&&&&&&&&&&&&'
		 
    def removeDico(self,key) :
        if _verbose:
            print 'in removeDico', key
	del self.allDicos[key]
	
#main class		   
class XmlParserConf:
    def __init__(self, phase,xmlCurrentStr,xmlDefaultFile,portTable,verbose):
        global _verbose
	_verbose = verbose
        self.xmlCurrentStr = xmlCurrentStr
        self.xmlDefaultFile = xmlDefaultFile

        apc.submod=submod

        self.apc = apc.APC(phase,portTable)
	self.stack = Stack()
	self.apcStack = Stack()
	self.attrNameList = []
	self.dicoLevel=0
	self.endNode=False
        self.lastTag=None
	self.newNode=None
	self.lastNode = None
	self.updated=False
        self.defaultConfig = ['defaultConfig']
 	self.dico = {}
	self.retCode = 1
	self.errmsg="ok"
        self.regexp = re.compile("\$\{(.*?)\}")

    def parserConf(self) :
        """parse the values and call the apc"""
        try :	
	    #evaluates implicit syntax
	    #self.regexp = re.compile("\$\{(.*?)\}")  


            # ************ parse the default values file *********************

            #create a parser for default values
            default_parser = xml.parsers.expat.ParserCreate()
            default_parser.StartElementHandler = self.start_element
            default_parser.EndElementHandler = self.end_element
            default_parser.CharacterDataHandler = self.send_data  
	
            
            #create the String structure to get the file content
            defaultStr=strip_file(self.xmlDefaultFile)
	     
            #parse the data
	    default_parser.Parse(defaultStr,True)
	    
            # ************** parse the actual values string ******************

            #create a parser
            values_parser = xml.parsers.expat.ParserCreate()
            values_parser.StartElementHandler = self.start_element
            values_parser.EndElementHandler = self.end_element
            values_parser.CharacterDataHandler = self.send_data  
            
            #parse the values
            values_parser.Parse(self.xmlCurrentStr)

            #call the procedure with the values
	    self.sendToAcq()
	
        #catch the errors
	except IOError,s:     
	    self.errmsg = s		    
	    self.retCode = 0
	    
	except AttributeError,s:
	    self.errmsg = s
	    self.retCode = 0
	    
        except NameError,s :
	    self.errmsg = s	    
	    self.retCode = 0
	except EmptyStackException,s:
	    self.errmsg = s.comment	    
	    self.retCode = 0
        except XmlParamException,s:
	    self.errmsg = s.comment	    
	    self.retCode = 0
	except AcqException,s:
	    self.errmsg = s.comment	    
	    self.retCode = 0
	        
	    
	return self.retCode,self.errmsg
        
	
    def start_element(self,tag,title):
	self.createElem(tag,title)
	self.lastTag=tag
	
    def createElem(self,tag,title):
	attrNames = title.values()      #attrNames : type list
	if attrNames  :
	    self.attributeName = attrNames[0]
	else :
	    self.attributeName = None
	    	    
	if tag in self.defaultConfig: 
	    self.newNode = tag
	    self.implicit = True 
	    #if _verbose:   
	    #    print '--------------------createNew Node :',self.newNode,self.attributeName,self.dicoLevel
	    self.config = Configuration(self.attributeName)
	    self.lastNode = tag
	    self.nodeName = self.attributeName
	    
	elif tag == "param" or len(attrNames)==0:
	    pass
	 
	else :
	    self.createNewNode(tag,title)    
	              
	    	    
	    
    def createNewNode(self,tag,title):
        if not self.endNode : 
	    #save structure before new Node
	    self.config.addDict(self.dico,self.dicoLevel)
	    self.dico = self.config.getLastDico(self.dicoLevel)
	         	
	else :
	    self.endNode = False       #traitement dico fait dans end-element
	  
	self.dicoLevel = self.dicoLevel+1  
	self.newNode = tag
	#into stack (read should mark the end of the node
	endFlag = "%s_completed"%(tag)
	apcStackItem = endFlag,self.attributeName,self.dicoLevel
	self.apcStack.push(apcStackItem)
   
	self.lastNode = tag
	self.nodeName = self.attributeName
	self.attrNameList.append(self.attributeName)
	stackItem = self.newNode,self.nodeName,self.dicoLevel
	self.stack.push(stackItem)
	
    def send_data(self,data) :
        if self.lastTag == "param" :
	    #print '--------dans send_data-------',self.newNode,self.lastNode
	    if self.newNode in self.defaultConfig:
	        self.updateCurrentDico(data)   #create default structure
	    else :
 	        if self.dico.has_key(self.attributeName) : 
	            self.updateCurrentDico(data)
                else  :
		    raise XmlParamException(self.attributeName,"XmlParser - ERROR !!!! param name unknown :")
	  
	   
    def updateCurrentDico(self,data):
        self.updated = True
	self.dico[self.attributeName]=data
	
	
    def end_element(self,tag):
        if tag == self.lastNode :
	    self.implicit = True
	else :
	    self.implicit = False 
	    
	    
	if tag in self.defaultConfig :   #'DefaultConfiguration'
	    self.config.addDict(self.dico,self.dicoLevel)
	    self.endNode = True
	    self.dico = self.config.getLastDico(self.dicoLevel)
	    
	     
	elif tag =="param" or self.attributeName==None:
	    pass 
	        
	else:
	    self.config.addDict(self.dico,self.dicoLevel)
	    self.sendAcqDevices(tag,self.nodeName,self.dico,self.implicit,self.dicoLevel)
	    self.config.removeDico(self.dicoLevel) 
	    self.endNode = True
	    self.stack.pop()                           
	    if not self.stack.isEmpty():
	        self.newNode,self.nodeName,self.dicoLevel = self.stack.getLastItem()
	        if _verbose:
	            print '------stack apres pop :'
	            print '------',self.newNode,self.nodeName,self.dicoLevel
	        self.dico = self.config.getLastDico(self.dicoLevel)
	   	        
	    
    """ traitement des donnees """	    
	    	    
    
    def sendAcqDevices(self,tagName,attributeName,dico,implicitFlag,level):
        if _verbose:
            print '---sendAcqDevices----------    ',tagName,'   ',attributeName,'   ',implicitFlag
	    print ' DICO LEVEL : ',level 
            for key in sorted(dico.iterkeys()) :
	        print "%s: %s" % (key,dico[key]) 
	device="%s_"%(tagName)
	
	if implicitFlag :
	    self.implicitTreatment(tagName,attributeName,dico)
	    
	else :    
	    dicoToApc = self.getNodeValues(dico,device)
	    infoDevice = attributeName.split('_')
	
	    if len(infoDevice)>1 : # !root                     
	        dicoToApc=self.lookupImplicitValues(dicoToApc,infoDevice)
	    apcStackItem = tagName,attributeName,dicoToApc
	    self.apcStack.push(apcStackItem)
	    endFlag = "%s_completed"%(attributeName)
	    self.attrNameList.append(endFlag)	    
	    
  
    def getNodeValues(self,dico,chaine):
        dicoToApc = {}
        for key in sorted(dico.iterkeys()) :
            if chaine in key[0:len(chaine)] :
	       dicoToApc[key]=dico[key]
	return dicoToApc 
    
    def sendToAcq(self):
        
	self.toApcList = [0]*len(self.attrNameList)
	#print 'size of toApcList:', len(self.toApcList)
	
	while not self.apcStack.isEmpty() :
	    tagName,attributeName,dicoToApc = self.apcStack.pop()
	    if 'completed' in tagName :
	        compar = attributeName+'_completed' 
		indx = self.attrNameList.index(compar)
	    else :
	        indx = self.attrNameList.index(attributeName)
	    apcItem = tagName,attributeName,dicoToApc
	    self.toApcList[indx]=apcItem
		    
	for i in self.toApcList:
	    if 'completed' in i[0] :
	        device = i[0].split('_')
		err,msg = self.apc.finalize_apc(device[0],i[1])
		if err == 0:
		    raise AcqException(msg)
            else:
		err,msg =self.apc.init_apc(i[0],i[1],i[2])
		if err == 0:
		    raise AcqException(msg)
		    
		
    def implicitTreatment(self,tagName,attributeName,dico) :
        #print "=========== input implicit treatment : ",tagName,attributeName
        previousAttrName = attributeName
        device = "%s_"%(tagName)	
	dicoToApc = self.getNodeValues(dico,device)
	infoDevice = attributeName.split('_')
	infoSize = len(infoDevice)
	
	if len(infoDevice)>1 : # !root                     
	   dicoToApc=self.lookupImplicitValues(dicoToApc,infoDevice)
	apcStackItem = tagName,attributeName,dicoToApc
	self.apcStack.push(apcStackItem)

	#search nb of subDevices
	for key,value in dicoToApc.items():
            if '_nb_' in key: 
	        subdev=key.split('_')
		newDev = subdev[2]
		new_dev_nb = value
	        if new_dev_nb :
	            for i in range (0,int(new_dev_nb)):
		        attributeName = newDev
		        for j in range (1,infoSize) :
		            attributeName += '_'+infoDevice[j]
		        attributeName+='_'+str(i+1)
			endTag = newDev+'_completed'
			apcStackItem = endTag,attributeName,self.dicoLevel
	                self.apcStack.push(apcStackItem)
			self.attrNameList.append(attributeName)
		        self.implicitTreatment(newDev,attributeName,dico)
	endTag = previousAttrName +'_completed'
	self.attrNameList.append(endTag)
	    

    def lookupImplicitValues(self,dicoToApc,infoDevice):
        for key,value in dicoToApc.items() :
            #print("lookupImplicitValues: %s: %s" % (key,value))
	    if '${' in value:
	        newVal= self.evaluate(value,infoDevice)
	        dicoToApc[key] = newVal
	return dicoToApc      
	       
		
 
    def evaluate(self,rawdata,infoDevice):    
	found = self.regexp.search(rawdata) 
	while found:
	    if _verbose:
	        print found.group(0)
		print found.group(1)
	    val = found.group(1)
	    hexa = False
	    for i in range(1,len(infoDevice)) :
                if val.find('nx')>-1  or val.find('0x')>-1:
	            hexa=True 
                val = val.replace(("nd%s" %i),infoDevice[i])
                val = val.replace(("nx%s" %i),infoDevice[i])
	    if hexa: 
                rawdata=rawdata.replace(found.group(0),str(hex(eval(val))))
            else:
	        rawdata=rawdata.replace(found.group(0),str(eval(val)))
		    
	    #print 'raw data apres evaluation : ', rawdata	
	    hexa = False
	    found = self.regexp.search(rawdata)
	    
        rawdata=rawdata.replace('0x','')    
	#print 'evaluation completed :',rawdata    	 	         	    
	return rawdata 
	
        
