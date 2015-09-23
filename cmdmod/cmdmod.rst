==================
The cmdmod wrapper
==================

cmdmod is a wrapper that simplifies the development of Pyrame modules by mutualizing the network server and client, the XML and :doc:`Pyrame protocol <protocol>` parsing and the control of public/private functions among others.

Figure 1 summarizes the inner workings of cmdmod.


.. figure:: cmdmod.doc.png
    :align: center
    :scale: 35%

    Figure 1: Example of module Y interacting with modules X and Z. Module Y is run inside :doc:`cmdmod <cmdmod>`

      
cmdmod's usage is:

.. code-block:: bash

    cmdmod config_file [-c cmod_ip]

On the following the :ref:`config_file <cmdmod_config_file>` and the :ref:`cmod functionality <cmdmod_cmod>` are described.

.. _cmdmod_config_file:

The XML config_file
===================

*config_file* is an XML file with a main `<config>` tag describing a number of parameters of the module. The required parameters are the Python implementation file and the TCP listening port :

.. code-block:: xml

    <config>
        <file>/opt/pyrame/cmd_test.py</file>
        <listen_port>9212</listen_port>
    </config>

Optionally, a ports file (via the *<port_base>* tag) or functions (via the *<cmd>* tag) can be included. The ports file is usually */opt/pyrame/ports.txt*, which includes all the stock Pyrame distribution ports. When the ports file is indicated, a non-numeric port can be used:

.. code-block:: xml

    <config>
        <file>/opt/pyrame/cmd_test.py</file>
        <port_base>/opt/pyrame/ports.txt</port_base>
        <listen_port>CMD_TEST</listen_port>
    </config>

Regarding the functions, depending on the functionality of the module and its comunication needs with others, a list of *script* or *host* functions can be included:

.. code-block:: xml

    <config>
        <file>/opt/pyrame/cmd_test.py</file>
        <listen_port>CMD_TEST</listen_port>
        <port_base>/opt/pyrame/ports.txt</port_base>
        <cmd name="test_test" type="script">
            <function>test_test</function>
        </cmd>
        <cmd name="setvar_varmod" type="host">
            <host>localhost</host>
            <port>VARMOD_PORT</port>
        </cmd>
    </config>

Script functions
----------------

The *script* functions are those that exist in the module and are intended to be public and thus callable from other modules. The *<cmd>* tag must include a public *name* and be of *type=script*. Inside the *<cmd>* tag a *<function>* tag must be included with the name of function on the Python implementation file. In most cases both will coincide for simplicity.

Host functions
--------------

The *host* functions are those that are implemented in other Pyrame modules and that the module might need to call at some point of its execution. The *<cmd>* tag must include the public *name* of the function on the external module. Inside the *<cmd>* tag, *<host>* and *<port>* tags must be included with the hostname (or IP) and the port of the external module. The port can be of text-type, if a *<port_base>* ports file is given and the desired port name is included on it.


cmdmod Python's API
===================

cmdmod provides two functions to the code run on its Python interpreter:

.. function:: submod.execcmd(function[,parameter1[,...]])

    It allows the code to call an external Pyrame function on another module. The first parameter is the function name and the rest is the optional list of parameters.

    Once the Pyrame command has been sent to the external module, the function waits for a response indefinetely. The response can be of any size within the system's memory constrains.
      
    The return value is None in case of error, or a tuple of retcode and return string in case of success.

.. function::  submod.setres(retcode,res)

    It allows to set the Pyrame return values of the function. The first argument is the return code, and the second the return string (see :doc:`protocol`). The return string will always be inside a :code:`<![CDATA[]]>` block.

    The return value is None in case of error or 1 in case in success.

    Note that this function only sets the result in cmdmod. Multiple calls to it will override the return values. The return will only be sent through the network when the Python function ends. For this reason, *submod.setres* is most usually followed by a *return* statement.


.. _cmdmod_cmod:

CMOD functionality
==================

cmdmod allows to extend further the *host* functions functionality provided by the XML by using the :doc:`cmod <cmd_cmod>` module. It is therefore only used when calling external functions via *submod.execcmd*. It is enabled by using the *-c cmod_ip* command-line argument, with *cmod_ip* being the IP or hostname where cmod runs.

When using cmod, the hostname of the module receiving the function call is determined in realtime (and cached for subsequent calls) based on the first parameter of call, which must be the device_id assigned by cmod. The module being called must coincide in name with substring of the function after the last "_" character.

Example:

A module called *chip* is present in two network nodes and each manages different physical devices of the same type. The module *chip* registers their devices on cmod with type *chip*. The module implements a function *init_chip(dev_id)*.

On this situation the *host* function scheme of the XML *config_file* is no longer valid, as the same function *init_chip* exists on two network nodes, and the selection of it depends on the first parameter of the function call.

When a Python code running on cmdmod wants to call *init_chip(3)*, cmdmod will detect that this function is not present on the XML *config_file* and, if the cmod functionality has been enabled, it will try to resolve from cmod the network node to which address that function call, based on the first parameter (3) and the type of device ("chip"). The type of device is extracted from the function name, as the substring after the last "_". Note that this forbids this functionality to work with modules that have "_" characters on their name.

