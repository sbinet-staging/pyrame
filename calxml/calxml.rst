=================
The calxml module
=================

The calxml module is dedicated to spread a set of parameters on different hardware of the system.
To achieve this goal, it reads a file in the :doc:`calxml format <calxml_format>`. It extracts the name of the required parameters from the modules API and extracts the values of the parameters from the xml file.

How does it works?
==================

The calxml function takes four arguments : 

- the phase name : this parameters is used to know what function has to be called in the different modules
- the xml configuration in :doc:`calxml format <calxml_format>`
- the default values filename
- the ports table filename

Here is the global algorithm : 

Parse the xml configuration : 
  Every time a new module is discovered : 

    - search in the module API for the name phasename_modulename
    - get the parameters name of this function
    - get the parameters values from the xml configuration or from the defaults file.
    - execute the function on the corresponding module with the parameters
    - continue with all the child modules 
    - search in the module API for the name phasename_fin_modulename
    - execute the function on the corresponding module with the parameters

As you can see, two different functions are called for every module : one at the discover of the module and one after the discovery of all its child modules.

An example
==========

Imagine we want to initialize a setup with a network switch and two connected cards. We have to initialize the switch with its port number as a parameter, then set the ip address for the two cards and then calculate the mac table on the switch. We will implement three functions.

.. code-block:: python

   def init_switch(switch_nb_port):
     init_ports(nb_port)

   def init_nic(nic_ip):
     setup_ip(nic_ip)

   def init_fin_switch():
     calc_mac_table()

Then create an xml file like that

.. code-block:: xml

   <switch name="sw">
     <param name="switch_nb_port">6</param>
     <nic name="nic1">
       <param name="nic_ip">192.168.0.1</param>
     </nic>
     <nic name="nic2">
       <param name="nic_ip">192.168.0.2</param>
     </nic>
   </switch>

When calling calxml with the init phase the function will be called in this order : 

- init_switch("6")
- init_nic("192.168.0.1")
- init_nic("192.168.0.1")
- init_fin_switch()

Note that all parameters are strings. If a function does not exists (like init_fin_nic in the example), it is simply ignored.

How to use it?
==============

Two possibility : 

- From the command line : 

.. code-block:: bash

   calxml phase_name config_file default_file port_table
 
- From a python script

.. code-block:: python

   import xmlConf
   y=xmlConf.XmlParserConf(phase_name,config,defaults_file_name,ports_table_file_name,False)
    retcode,res = y.parserConf()
    if retcode==0:
        res="cant apply phase %s : %s"%(phase_name,res)
    return retcode,res
