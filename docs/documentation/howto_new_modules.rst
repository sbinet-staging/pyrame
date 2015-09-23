
===========================================
How to write a new Pyrame module for cmdmod
===========================================

This document describes how to implement a new module in Python and how to use it with cmdmod.

A module is a piece of software used to drive a piece of hardware or an abstract entity. We typically use a module to manage multiple devices of the same flavour. It is composed of two files: a description file in XML and an implementation file in Python. The :doc:`cmdmod <cmdmod>` tool is used to run it.

In the following, we create from scratch a new module named "test".

Creating the description file
=============================

The description file contains all the information needed by the module for running:
 
- the Python file
- the listening port of the module
- the functions used in the underlying modules and the IP address of their host
- the functions provided by this module

The smallest description file
-----------------------------

Let's begin with a minimalistic file. It should look like this :

.. code-block:: xml

   <config>
     <file>/opt/pyrame/cmd_test.py</file>
     <listen_port>9212</listen_port>
   </config>

It just contains a reference to the Python implementation file with its path and the value of the port on which cmdmod should listen on.

So far, the module does not export any function, thus it will answer "unknown function" to any command.

Using a file for port description
---------------------------------

It is a bit boring the manage the port number by just knowing them. It is often better to use some basic DB. It is the case of the /opt/pyrame/ports.txt file.

You can just add the number of your new test module in that file this way ::

  TEST_PORT=9212

By convention, we use the capitalized name of the module followed with _PORT as a name.
Verify that the port you use is free on your machine (that is, it does not collide with another Pyrame module nor with some other network service). 

In the description file, we have to had a line like:

.. code-block:: xml

  <port_base>/opt/pyrame/ports.txt</port_base>

Then we can use the name of the port instead of the number:

.. code-block:: xml

  <listen_port>TEST_PORT</listen_port>

Exporting functions
-------------------

To be useful, a Pyrame module should export some functions. These functions have to be declared in the description file as follows:

.. code-block:: xml

  <cmd name="helloworld_test" type="script">
    <function>helloworld_test</function>
  </cmd>

On the first line, the name corresponds to the command name in the Pyrame protocol. The type *script* is for local implementation (as opposed to *host* - see the next section).

On the second line, the function is the name of the python function that will be called by cmdmod. Usually both names are identical but for some reasons they can be different.

As a convention, we add an underscore and the name of the module after the name of the function. Here the function is helloworld but we call it helloworld_test to avoid name collision (as a namespace). 

Adding dependencies
-------------------

The module can use one or more underlying modules that provide communications or global services.

All these underlying modules provide an API (programming interface, specifically the names and parameters of the functions). These APIs are available in the folder /opt/pyrame in the \*.api files. The format is name_of_function : parameter_1, parameter_2... See :doc:`getapi` for more details.

All modules provide init_* and deinit_* functions to initialize and deinitialize a device managed by the module. The other functions are functional. Their first argument is always the *id* of the hardware which is returned by the init function.

In our example, let's add the serial module as a dependency. We don't need to get all the serial functions but just the ones we really use:

.. code-block:: xml

  <cmd name="init_serial" type="host">
    <host>localhost</host>
    <port>SERIAL_PORT</port>
  </cmd>
  <cmd name="deinit_serial" type="host">
    <host>localhost</host>
    <port>SERIAL_PORT</port>
  </cmd>
  <cmd name="write_serial" type="host">
    <host>localhost</host>
    <port>SERIAL_PORT</port>
  </cmd>
  <cmd name="read_serial" type="host">
    <host>localhost</host>
    <port>SERIAL_PORT</port>
  </cmd>

For these four functions, we get:
- the name of the function (suffixed with the name of the module - see here the interest of this namespace, it avoids that all the init function are called *init*.
- the type *host* that says it could be executed on another host (including localhost)
- the host: it is the ip address or network name of the machine the underlying module is running on.
- the port: again we can use a number or a name if the *port_base* directive has been used

Final file
----------

Here is the concatenation of all the parts:

.. code-block:: xml

  <config>
    <file>/opt/pyrame/cmd_test.py</file>
    <port_base>/opt/pyrame/ports.txt</port_base>
    <listen_port>TEST_PORT</listen_port>
    <cmd name="helloworld_test" type="script">
      <function>helloworld_test</function>
    </cmd>
    <cmd name="init_serial" type="host">
      <host>localhost</host>
      <port>SERIAL_PORT</port>
    </cmd>
    <cmd name="deinit_serial" type="host">
      <host>localhost</host>
      <port>SERIAL_PORT</port>
    </cmd>
    <cmd name="write_serial" type="host">
      <host>localhost</host>
      <port>SERIAL_PORT</port>
    </cmd>
    <cmd name="read_serial" type="host">
      <host>localhost</host>
      <port>SERIAL_PORT</port>
    </cmd>   
  </config>
 
Implementation of the Python module
===================================

Now that we have a description file, we have to implement the functions in a Python file.

The cmdmod extension
--------------------

As stated in the cmdmod documentation, cmdmod is basically a Python virtual machine with a TCP/XML/Pyrame protocol decoder. Thus, the core of a module is a set of Python functions that respond to requests.
cmdmod extends Python possibilities with two Pyrame primitives *setres* and *execmd*. They are groupped in the submod namespace.

*setres* allows the module to set the boolean return value and the string return message. Caution : it does not return immediately. You have to call return explicitely if it is not the end of the function.

*execmd* allows the module to call a function on an underlying module.

.. note::

  Pyrame protocol does not accept to name the arguments of functions, so optional arguments must always be at the end of the list.

Hello world
-----------

This very basic function just returns 1 as return value (which means success) and "Hello World" as return text::

  def helloworld_test(): 
    submod.setres(1,"Hello World")

A more complicated example
--------------------------

Here is a little bit more complicated example showing parameters manipulation and return after setres::

  def helloworld_test(name):
    if (name=="badname"):
      submod.setres(0,"Helloworld function does not like badname")
      return
    if (name==""):
      submod.setres(1,"Hello World")
      return
    else:
      submod.setres(1,"Hello %s"%(name))

When 0 is returned it means an error. The error message has to be explicit for easying the debugging. A ``return`` statement at the end is useless because we have already reached the end of the function.

Calling another module
----------------------

To construct complicated systems, the modules have to rely on others. This is why a module can call another one with the *execmd* primitive.

Here is an example of a serial helloworld. It just opens a serial communication with a device having imprint "abcd:efgh" and sends Hello World on this serial link::

  def serialhelloworld_test():
    val,res=submod.execmd("init_serial","abcd:efgh")
    if (val==0):
      submod.setres(0,"cant init serial : %s"%(res))
      return
    else:
      serial_id=res
      val,res=submod.execmd("write_serial",serial_id,"Hello World\n")
      if (val==0):
        submod.setres(0,"cant write to serial : %s"%(res))
        return
      else:
        val,res=submod.execmd("deinit_serial",serial_id)
    if (val==0):
          submod.setres(0,"cant deinit serial : %s"%(res))
          return
    else:
          submod.setres(1,"Hello World successfully sent on serial")

In case of success, the init_serial function returns an id in retcode that will be the reference for all following actions. It will have to be deinitialized at some point. 

You can see that in case of error, we pipeline the error reason to the next level ::
  
  submod.setres(0,"error in something : %s"%(res))

This way, at any level we get the deepest error messages, allowing to debug easilly.

Internal and External functions
-------------------------------

.. warning::

  A module should never call itself!

As the treatments are atomic (to avoid interblocking during hardware access), a module is able to handle its own call during its execution resulting in an interblocking situation. If the module has to call its own functions, you have to declare an internal function for internal use::

  def helloworld():
    return 1,"Hello World"

and an external function based on the internal version for external use::

  def helloworld_test():
    val,res=helloworld()
    submod.setres(val,res)

Note that, by convention, the external function has the name of the module as a suffix (for namespacing as explain previously) but the internal function has not.

Testing the module
==================

Now, our module is completed. We just have to install it and test it.

By convention, all the Pyrame modules are stored in the */opt/pyrame* folder but you can place it wherever you want.

Launching cmdmod
----------------

Launching cmdmod is very simple::

  cmdmod /opt/pyrame/cmd_test.xml

It takes as its only parameter the description file with its path. The output of the module is the standard output.

You should see an output like::

  cmdmod with 2 args
  opening port table file /opt/pyrame/ports.txt
  load configuration : 
  found file : /opt/pyrame/cmd_test.py
  found ports base : /opt/pyrame/ports.txt
  opening port table file /opt/pyrame/ports.txt
  launching the tcp listening socket on port 9212
  netserv active with delay 2000000
  1 clients
  initializing socket for client 0
  socket setup finished on fd 6 

If you get an "error in XML_Parse", check your file with an xml syntax checker like xmllint.

Sending commands with chkpyr
----------------------------

chkpyr2 is a tool that allows to send Pyrame commands through the command line.
Its syntax is ::

  chkpyr2.py host port function [parameters]

As we want to check our test module with the second version of the helloworld function, we should type ::

  chkpyr2.py localhost 9212 helloworld_test Fred

Fred is the value for the name parameter.
Dont forget to escape your double quote with antislash.
We get the result ::
  
  retcode=1   res=Hello Fred

If you don't want to use the numerical value of the port, you can add it in the /opt/pyrame/ports.sh file ::
  
  export TEST_PORT=9212

Then you just run this script and run chkpyr2 with name of the port instead of its value ::
  
  . /opt/pyrame/ports.sh
  chkpyr2.py localhost TEST_PORT helloworld_test Fred

You can pass a void argument ::

  chkpyr2.py localhost TEST_PORT helloworld_test ""

and then we have the "Hello World" result ::

  retcode=1   res=Hello World

Finally if we use the "badname" value ::

  chkpyr2.py localhost TEST_PORT helloworld_test badname

We get an error ::

  retcode=0   res=Helloworld function does not like badname

