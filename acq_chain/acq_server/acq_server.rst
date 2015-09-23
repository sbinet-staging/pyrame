=====================
The acquisition chain
=====================

This module is dedicated to data acquisition, uncap and dispatch.

Key concepts of design
======================

The acquisition chain is a software hub collecting data from acquisition unit. It has multiple mission : 

- acquiring data from media (Ethernet, TCP, UDP, USB...) through dedicated acquisition plugins.
- uncapping data : removing headers and trailers, converting between data formats, verifying data integrity (CRC for example), checking receive order (with sequence numbers) and reordering if necessary, splitting between data and control packets, injecting a reference clock in the data. All these tasks are done through dedicated uncap plugins.
- splitting data into separate streams.
- storing data to files (one file per stream plus a trash). It has also the possibility to store the raw data to replay it later for debugging purpose.
- dispatching data through tcp sockets. Any program which connects to the adequate tcp port will get all the data from the corresponding stream (one tcp port per stream).
- dispatching data through shared memories (one shared space per stream).

In order to handle different data from different media at the same time, the acquistion chain use a plugin system. At the same time, multiple plugins can acquire data from different media. This data are dispatched in the different streams and can be synchronized through a reference clock system.

.. figure:: acq_server.doc.png
    :align: center

    Figure 1: Architecture of the acquisition chain.

API
===

The acquisition chain is a Pyrame module. Thus, it respond to several Pyrame commands. 

.. function:: init_acq(datadir)

Initialize the acquisition chain. Note that at init, this chain has no acquisition unit and thus cannot take any data (see newunit_acq for details).

- The datadir parameters is a folder where the data files will be stored.

It is necessary to call this function before any other else.

.. function:: deinit_acq()

De-initialize the acquisition chain. In particular, it removes all existing acquisition and uncap plugins. After the call, the chain is ready to be initialized again.

It takes no parameter.

.. function:: newunit_acq(nb_streams, acq_plugin, uncap_plugin, stream_suffix, acq_plugin_param_1,  acq_plugin_param_2,  acq_plugin_param_3)

Add a new acquisition unit to the acquisition chain. An acquisition unit is characterized by its acquisition plugin (i.e. the hardware media it reads) and its uncap plugin (i.e. the way it will decode the data). 

It is able to manage an arbitrary number of streams (this means that a single acquisition unit can handle multiple hardware of the same flavor).

Parameters : 

- nb_streams : the number of streams handled by this new acquistion unit
- acq_plugin : the name (with path) of the acquisition plugin library
- uncap_plugin : the name (with path) of the uncap plugin library
- stream_suffix : this is a suffix that is added in the name of the files.  The name will have the form takename_suffix_streamnumber.raw. Takename is the name if the data take (see flush_files for more details).
- acq_plugin_param_(1,2,3) : these params are specific param of the acquisition chain plugin. Please see specific documentation of every plugin for more details.

Note that the only way to remove an acquisition unit is to de-initialize the acquisition chain (with the deinit_acq function).

In case of success, it returns the identifier of the new acquisition unit.

.. function:: startacq()

Start the acquisition. Until this function is called, the acquisition unit are loaded but does not acquire anything.

It takes no parameter.

.. function:: stopacq()

Stop the acquisition. After this function is called the acquisition plugins will not acquire any data but some untreated data can remains some time in the treatment chain.

It takes no parameter.

.. function:: flush_files_acq(takename)

While acquiring, all the data are stored in files called running_suffix_streamnumber.raw. By calling this function, all the files are renamed takename_suffix_streamnumber.raw. The running files are re-opened immediately.

Parameters : 

- takename : this is the prefix of the saved files.

.. function:: get_stats_acq()

This functions returns the acquisition statistics with this form::

  nb_busy_bufs=0 nb_data_pkts=16 nb_lost_pkts=0 nb_ctrl_pkts=0 bytes_on_disk=22 bytes_on_socket=0 bytes_on_shmem=0

The values are in order : 
- number of busy buffers (i.e. the number of data acquired but not treated)
- number of received data packets
- number if lost packets (lost in the acquisition chain for congestion reason)
- number of received control packets
- number of bytes stored on disk (until the previous flush_files_acq)
- number of bytes sent on data sockets
- number of bytes sent on shared memories

It takes no parameter.

.. function:: start_shmem_acq()

Start the export of data through shared memories. Take care that Shared memories are blocking if not read. Thus the reading program must be launched prior to call this function.

It takes no parameter.

.. function:: stop_shmem_acq()

Stop the export of data through shared memories.

It takes no parameter.

.. function:: start_bsched_acq()

Start the burst scheduler. This is a mechanism for blocking the treatment chain while acquiring a burst of data. This can be useful when using unsafe media where data can vanish (Raw ethernet for example). 

Take care not to use this scheduler if your data stream is continuous.

It takes no parameter.

.. function:: stop_bsched_acq()

Stop the burst scheduler.

It takes no parameter.

.. function:: allow_autoflush_acq(limit)

This is a mechanism to avoid filling the whole disk with data and running out of space. If this function is called with a limit in Mo. If the cumulated size of the files reach this limit then the system automatically flush the data files with the prefix auto_flush.

The autoflush is disallowed by default.

Parameters : 

- limit : limit in Mo of the total size of the data files. 

.. function:: dis_autoflush_acq()

Disallow the autoflush mechanism.

It takes no parameter.

.. function:: allow_rawoutp_acq()

Allow the raw output. If allowed, all the raw data (as received by the uncap plugin) is stored in a special size in order to relay it later for debugging purpose. 

This behavior is disallowed by default.

It takes no parameter.

Take care, this file is not taken in account by the autoflush mechanism.

.. function:: dis_rawoutp_acq()

Disallow the raw output.

It takes no parameter.

.. function:: inject_data_acq(stream_id,data)

This command allow to inject arbitrary data in any stream.

Paramters : 

- stream_id : the identifier of the stream where the data has to be injected.
- data : the data to inject encoded in ascii hexadecimal numbers, separated with comma.

.. function:: set_refclock_acq(refclock)

The reference clock is a mechanism allowing to synchronize data between them. This clock is just a string made available to every plugins. They can update it from their data stream or just use it to tag their data. 

This command allow the user to set himself the reference clock. This can be useful in case of scripts generating data and whishing to tag the data with this clock.

Parameters : 

- refclock : the string value of the clock

.. function:: get_cpkt_byid_acq(au_id,id1,id2,id3,id4)

Crawl the control packets pool, searching a particular packet. The control packets received by the uncap plugins are stored in a circular pool.

Parameters : 

- au_id : this is the identifier of the acquisition unit where the control packet has been received.
- id(1,2,3,4) : these ids are intended to help uncap plugin to find the needed packet. The values are not constrained by the acquisition chain and can be used freely in the plugins.

It case of success, it returns the packet encoded in ascii hexadecimal representation.  

The acquisition plugin
======================

Every acquisition plugin has in charge to connect to their media and acquiring blocks of data when requested. 

These plugins are bunch of C functions with fixed prototypes. They have to be compiled as a dynmic library (.so). They are loaded dynamically by the acquisition unit.

Here you will find all the details of their prototypes : 

.. function:: init_acq(param_1,param_2,param_3)

This function will initialize the plugin. 

It takes three string parameters coming from acq_plugin_param_1,  acq_plugin_param_2 and  acq_plugin_param_3 from the new_acqunit_acq command. 

It returns a pointer (void*) to its own workspace. This workspace is a bunch of memory where the plugin can store all its parameters. Its is mandatory to store this workspace and use it at every call of the plugin functions.

.. function:: deinit_acq(ws)

This function de-initialize the plugin. It close all the necessary connections and destroy its own workspace. After the return of this function, all the function pointers can be destroyed, thus no data should remain.

.. function:: start_acq(workspace)

Start the acquisition.

.. function:: stop_acq(workspace)

Stop the acquisition.

.. function:: acquire_one_block(workspace,buffer,maxsize)

Acquire data from hardware into buffer up to maxsize bytes.

Real plugins
------------

For real examples, see the following documentations : 

.. toctree::
    :titlesonly:

    tcps_acq
    tcpc_acq
    udp_acq
    eth_acq
    noacq_acq

The uncap plugin
================

.. function:: init(nb_streams,fid,plugin_name)

Initialize the plugin.

Parameters : 

- nb_streams : number of streams handled by this plugin
- fid : first stream id available. All the streams will be between fid and fid+nb_streams
- plugin_name : just a string to name the plugin

In case of success, this function returns a pointer (void*) to its own workspace. This workspace is a bunch of memory where the plugin can store all its parameters. Its is mandatory to store this workspace and use it at every call of the plugin functions.

.. function:: deinit(workspace)

Deinitialize the plugin

.. function:: prefilter(workspace,packet,size)

This is a first analyse of a received packet to know which type of packet it is. The function returns an encoded value. It can be : 

- PREF_DATA : the packet is data
- PREF_CTRL : the packet is control
- PREF_JUNK : the packet can be thrown, it is not for this plugin

This function has to be very light because it is called very often during acquisition itself. 

.. function:: uncap(workspace,packet,packet_size,result,result_size,loss,data,corrupted,stream,refclock)

This function uncap the packet and fill the other parameters wich are pointer.

Parameters : 

- workspace : memory of the plugin
- packet : contain the raw packet as received by the acquisition plugin
- packet_size : the size in bytes of the packet
- result : pointer to the result packet
- result_size : pointer to the result packet size
- loss : pointer to a boolean indicating if there had been a loss of packet before the current one.
- data : pointer to a boolean indicating if the packet is data or not.
- corrupted : pointer to a boolean indicating if the packet is corrupted or not.
- stream : pointer to a integer that should contain the stream id the packet blongs to. Remember that the streams that belong to the plugin are between the fid and fid+nb_streams parameters given at init.
- refclock : pointer to the reference clock. Can be used or updated by the plugin.

The function returns 1 for success and 0 for failure. All the result pointer are supposed to be filled.

This function call can be postponed by the burst scheduler. 

.. function:: int select_packet(workspace,packet,id1,id2,id3,id4)

This function decides if a control packet correspond to a multiple id description.

When a module ask for a particular control packet, it will execute a get_cpkt_byid_acq command. The ids are sent as is to the plugin.

Parameters : 

- workspace : memory of the plugin
- packet : control packet to check
- id(1,2,3,4) : these ids can be used freely by the plugin to select the good packet.

In case of success, the function returns 1, 0 otherwise.

Real plugins
------------

For real examples, see the following documentations : 

.. toctree::
    :titlesonly:

    uncap_dummy
    uncap_addclock
    uncap_extclock

