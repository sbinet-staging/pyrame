===================
The Pyrame protocol
===================

This document describes the protocol used by Pyrame modules to communicate.

The Pyrame module concept
=========================

In Pyrame, a module is a piece of software that handles a type of hardware device. Generally, it can handle multiple devices of the same flavour. This module will be able to treat requests if they are expressed in the Pyrame protocol. It will handle the access to its hardware, performing the conversion of data format between the hardware and Pyrame.

The protocol
============

A Pyrame command is expressed in XML language and sent through a TCP socket with the following form :

.. code-block:: xml

    <cmd name="name_of_command"><param></param></cmd>

where *name_of_command* is the name of the Pyrame command. A linefeed character (ascii 10) must terminate every command. Arguments can be passed to the command by using the ``<param></param>`` tags inside the ``<cmd></cmd>`` block. For example:

.. code-block:: xml

    <cmd name="print_once"><param>hello world</param></cmd>
    <cmd name="print_ntimes"><param>hello world</param><param>2</param></cmd>

Responses from a Pyrame module are also in XML language and expressed in the form:

.. code-block:: xml

    <res retcode="X"></res>

*X* must be an integer and indicates the result of the command. Zero is failure. A linefeed character (ascii 10) must terminate every response. Additional information can be returned by including it inside the ``<res></res>`` block. For example:

.. code-block:: xml

    <res retcode="1">hello to you, too</res>

.. warning::

    Since both commands and responses are ended with a linefeed character, these characters must be escaped as \\n or \\r respectively in order to be transferred to and from Pyrame modules.

.. note::

    If the characters ``<`` or ``>`` need to be included in either commands or responses, the ``<![CDATA[ ]]>`` block must be used to prevent the XML parser from parsing those values. For example:
    
    .. code-block:: xml

        <res retcode="1"><![CDATA[True statement: 100>10]]></res>
        <res retcode="1"><![CDATA[HTML documents start with <html>]]></res>

    **This is systematically done by cmdmod on all responses.**
