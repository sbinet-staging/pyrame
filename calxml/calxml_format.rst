=================
The calxml format
=================

This format, based on XML allows to represent a complete system and all its necessary parameters. 

Basics
======

The principle of the calxml format is to declare objects to describe the harware.

For example if you want to describe an arduino module named ard1 with a parameter named frequency with value 50 and an ip address of 10.220.0.97, you have to write :  

.. code-block:: xml

   <arduino name="ard1">
     <param name="arduino_frequency">50</param>
     <param name="arduino_ip">10.220.0.97</param>
   </arduino>

Note that the parameters contains the name of the object. It has to be like that for calxml to know which parameter is for what object.

Arborescence
============

Very often, the hardware is organized following a tree structure and must be initialized following this organization. In order to reflect this state, objects can be declared in a tree way : 

.. code-block:: xml

    <master_hw name="mhw1">
      <param name="master_hw">value1</param>
      <slave_hw name="shw1">
        <param name="slave_hw">value2</param>
      </slave_hw>
      <slave_hw name="shw2">
        <param name="slave_hw">value3</param>
      </slave_hw>
    </master_hw>

This way calxml will know in wich order it should initialized this hardware. See :doc:`calxml <calxml>` phases for details.



Default values
==============

Calxml use a file describing all the possible parameters of the system and also a default value for each. Thus if the default value is correct for your use, you dont need to declare the corresponding parameters.

Note that if you use a parameter name that has no default value, an error will occurs.

Shared parameters
=================

If you want to declare several modules with the same values for a parameter, you have the possibility to share the declaration between the different hardware.
For example : 

.. code-block:: xml

    <master_hw name="mhw_">
      <param name="master_hw">value1</param>
      <slave_hw name="shw_">
        <param name="slave_hw">value2</param>
      </slave_hw>
      <slave_hw name="shw_">
        <param name="slave_hw">value2</param>
      </slave_hw>
    </master_hw>

The value2 is shared by the two slave_hw modules. You have the possibility to declare it before the defininition of the two modules : 

.. code-block:: xml

    <master_hw name="mhw_">
      <param name="master_hw">value1</param>
      <param name="slave_hw">value2</param>
      <slave_hw name="shw_">
      </slave_hw>
      <slave_hw name="shw_">
      </slave_hw>
    </master_hw>

This format is then more compact. This is why every parameter has to contains the name of its reffering object.

Implicit declaration
====================

In order to get an even more compact format. We can replace the declaration of the modules by just their number (if no specific parameter is needed).

Let's rewrite again the previous example : 

.. code-block:: xml

    <master_hw name="mhw_1>
      <param name="master_hw">value1</param>
      <param name="master_hw_nb_slave_hw">2</param>
      <param name="slave_hw">value2</param>
    </master_hw>

the "nb" parameter tells the system that two slave_hw are implicitly declared. They will use the default or previously declared parameters.

In that case, they will be named slave_hw_1_1 and slave_hw_1_2. The first 1 refers to the mhw_1 number.

Use of module name in values
============================

When the name of the modules follows the rule: module_x_y_z where x in the grandparent, y is the parent and z is the number of the module itself, the numbers x, y and z are accessible for use in a value of a parameter.

For example, a configuration file has 22 acquisition pc's. Each of them has an IP address which is successive starting on 10.220.0.100. In order to declare it in the most compact way, the following code can be used:

.. code-block:: xml

    <detector name="mydetector_1">
      <param name="detector_nb_acqpc">22</param>
      <param name="acqpc_ip">10.220.0.${100+nd2}</param>
    </detector>

The delimiters `${}` will tell calxml to evaluate whats inside, first replacing all substrings `ndi` and `nxi` (where `i` is a number) by the i^th number on its name. Then, for acqpc_1_4, calxml would evaluate 100+4, i.e. it will have an ip=10.220.0.104. When `nx` is used, the result of the evaluation is converted to hexadecimal value, without the leading "0x". This variant can be used for successive MAC addresses.

The detector
============

The global file has to cope with the XML specification : 

- XML header
- only one object in the file

This is why we have to begin the file with a header like 

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>

All the declaration has to be enclosed in a single object. We choose to call it "detector".

.. code-block:: xml

   <detector name="mydetector">
   put all hardware declaration here
   </detector>

The domain
==========

As Pyrame is a distributed system, it is necessary that calxml know where to find the modules. That's why the hardware declaration can be grouped under "domain" tags.  

.. code-block:: xml

   <domain name="name_or_IP_of_the_machine">
   put all hardware declaration belonging to this machine here
   </domain>

A real example
==============

This is a real example describing the SiW-Ecal prototype for future ILC distributed on two machines. 

.. code-block:: xml

   <?xml version="1.0" encoding="UTF-8"?>
   <detector name="ecal_2pc">
     <param name="dif_nb_skiroc">4</param>
     <param name="dif_alim">PP</param>
     <param name="dif_roctype">skiroc2</param>
     <param name="dif_dcc_nibble">0</param>
     <domain name="llrcaldaq2">
       <param name="domain_ip">10.220.0.4</param>
       <varmod name="varmod"></varmod>
       <acqpc name="pcacq_1">
         <lda name="lda_1_1">
           <param name="lda_mac_addr">00:0a:35:01:fe:02</param>
	   <param name="lda_pc_dev">em2</param>
	   <dif name="dif_1_1_1">
	     <param name="dif_lda_port">1</param>
	   </dif>
	   <dif name="dif_1_1_2">
             <param name="dif_lda_port">2</param>
	   </dif>
	   <dif name="dif_1_1_3">
	     <param name="dif_lda_port">3</param>
	   </dif>
         </lda>
       </acqpc>
       <sigpulse name="spill">
         <param name="sigpulse_fe">min</param>
         <param name="sigpulse_hl">4</param>
         <param name="sigpulse_freq">10</param>
         <param name="sigpulse_re">min</param>
	 <param name="sigpulse_channel">1</param>
	 <param name="sigpulse_pw">0.09</param>
	 <param name="sigpulse_conf_string">ag_33500/10.220.0.3:5025</param>
	 <param name="sigpulse_ll">0</param>
	 <param name="sigpulse_phase">undef</param>
       </sigpulse>
     </domain>
     <domain name="llrcaldaq1">
       <param name="domain_ip">10.220.0.2</param>
       <acqpc name="pcacq_2">
         <lda name="lda_2_1">
	   <param name="lda_mac_addr">00:0a:35:01:fe:03</param>
	   <param name="lda_pc_dev">em2</param>
	   <dif name="dif_2_1_1">
	     <param name="dif_lda_port">1</param>
	   </dif>
	   <dif name="dif_2_1_2">
	     <param name="dif_lda_port">2</param>
	   </dif>
	   <dif name="dif_2_1_3">
	     <param name="dif_lda_port">3</param>
	   </dif>
	 </lda>
       </acqpc>
     </domain>
   </detector>




