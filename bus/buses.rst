===============
Buses
===============

.. toctree::
    :titlesonly:

    cmd_gpib
    cmd_tcp
    cmd_serial
    cmd_raweth

From the four bus modules that Pyrame includes, three of them provide bidirectional communication capabilities (:doc:`serial <cmd_serial>`, :doc:`tcp <cmd_tcp>` and :doc:`gpib <cmd_gpib>`) while the fourth one (:doc:`raw ethernet <cmd_raweth>`) only provides the possibility of sending packets, specifically reserving the collection of responses/data to the :doc:`acquisition chain <acq_server>`.

On the following, the bidirectional buses will be described. Pyrame includes two low-level bus modules: :doc:`serial <cmd_serial>` and :doc:`tcp <cmd_tcp>`. The former provides access to USB devices while the latter is an interface for communication via TCP sockets. In addition, a mid-level module: :doc:`gpib <cmd_gpib>` (cmd_gpib), provides an interface to PROLOGIX GPIB adapters. Both the USB and Ethernet models are supported via serial (cmd_serial) and tcp (cmd_tcp).

This document describes the common API provided by cmd_serial, cmd_tcp and cmd_gpib, as well as the differences between them. The three modules keep a pool of connections.

.. figure:: buses.doc.png
    :align: center
    :scale: 50%

    Figure 1: Example of interaction between Pyrame bus modules (gpib, serial, tcp) and others.

Pool and identification
=======================

Every link or connection in the pool gets assigned an identification token (id >= 0) which identifies it uniquely during the execution of Pyrame. The id is attributed by the function init_BUS (where BUS is serial, tcp of gpib). All functions of gpib, serial and tcp, except init_BUS, require this id token as the first argument.

Initialization
==============

The init_BUS functions take a :doc:`conf_strings <conf_strings>` as sole parameter to initialize and configure the link. See the documentation of each module for the required and optional parameters of the conf_string.

The init_BUS functions must register in memory the parameters provided by the conf_string and attribute an id. According to the basic :doc:`phases of Pyrame <phases>`, no communication with the hardware should happen during the initialization phase.

Configuration
=============

The config_BUS functions must initiate communication with the hardware and prepare the link for immediate operation.

Low-level functions
===================

The low-level bus modules (so far tcp and serial) must include, at least, an implementation of the following functions:

    init_BUS (*conf_string*)

    deinit_BUS (*link_id*)

    write_BUS (*link_id*, *data*)

    read_BUS (*link_id*, *bytes_to_read* [, *timeout*])

    read_bin_BUS (*link_id*, *bytes_to_read* [, *timeout*])

    read_until_BUS (*link_id*, *eot* [, *timeout*])

    read_bin_until_BUS (*link_id*, *eot* [, *timeout*])

    wrnrd_BUS (*link_id*, *data*, *bytes_to_read* [, *timeout*])

    wrnrd_bin_BUS (*link_id*, *data*, *bytes_to_read* [, *timeout*])

    wrnrd_until_BUS (*link_id*, *data*, *eot* [, *timeout*])

    wrnrd_bin_until_BUS (*link_id*, *data*, *eot* [, *timeout*])

    expect_BUS (*link_id*, *pattern* [, *timeout*])

General considerations:

    - Non binary reading functions will ignore characters 10, 13 and 0 (nul-byte).
    - Writing functions can receive non printable characters by escaping them like \e, \t, \n or \r for bytes 27, 9, 10 and 13 respectively. Any escaping sequence accepted by Python's str.decode function can be used.
    - Timeout is 60 s by default when the optional parameter is not usedi

Expected behavior of the functions in addition to the general considerations:

    - write_*_BUS must send data through the link described by link_id.
    - read_BUS must receive bytes_to_read bytes from the link described by link_id in single operation (not byte-per-byte). This read operation must time out according to the optional parameter or the default timeout value.
    - "until" functions have an *eot* parameter. This is a comma-separated list of patterns. The reading operation will terminate upon receival of any of those patterns. A pattern is one or more characters that can be escape sequences.
    - expect_BUS must read byte-per-byte from the link until the pattern is found or time out. Before comparison, pattern is unescaped as on writing functions, resulting in a string of pattern_length bytes. The pattern is found when the last pattern_length bytes received from the link, ignoring nul-bytes, coincides with the unescaped pattern.
