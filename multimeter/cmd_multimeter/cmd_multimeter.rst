The multimeter module
=====================

Abstraction module for multimeters. The cmd_multimeter module allows the transparent use of a pool of an undefined number of multimeters regardless of maker, model or host-device link technology. Its function is to redirect the requests and orders made to it, to a module that knows how to interface with that particular device.

Presently, the following compatible modules are shipped with Pyrame:

.. toctree::
    :titlesonly:

    Agilent 34401A multimeter <cmd_ag_34401a>
    Keithley 6487 picoammeter <cmd_mm_ki_6487>

This module is the analog of :doc:`cmd_ps <cmd_ps>` for multimeters. See its documentation for general considerations.

Functions
=========

On top of the mandatory functions listed in :doc:`cmd_ps <cmd_ps>`, the following can be implemented and accessed through cmd_multimeter:

- get_dc_voltage_MODEL(*model_id* [, *range* [, *resolution* [, *channel* ]]])
- get_ac_voltage_MODEL(*model_id* [, *range* [, *resolution* [, *channel* ]]])
- get_dc_current_MODEL(*model_id* [, *range* [, *resolution* [, *channel* ]]])
- get_ac_current_MODEL(*model_id* [, *range* [, *resolution* [, *channel* ]]])
- get_2w_resistance_MODEL(*model_id* [, *range* [, *resolution* [, *channel* ]]])
- get_4w_resistance_MODEL(*model_id* [, *range* [, *resolution* [, *channel* ]]])
- get_frequency_MODEL(*model_id* [, *range* [, *resolution* [, *channel* ]]])
- get_period_MODEL(*model_id* [, *range* [, *resolution* [, *channel* ]]])
- get_error_queue_MODEL (*model_id* )

In all cases:
- Magnitudes (i.e.: voltage, current, frequency, etc.), either sent or returned, must be expressed in base units of the International System of Units (V, A, Hertz, etc.).

The functionality provided by each of the functions is primarily the following:

- get_dc_voltage_MODEL(*model_id* [, *range* [, *resolution* [, *channel* ]]])

  Measure DC voltage.

- get_ac_voltage_MODEL(*model_id* [, *range* [, *resolution* [, *channel* ]]])

  Measure AC voltage.

- get_dc_current_MODEL(*model_id* [, *range* [, *resolution* [, *channel* ]]])

  Measure DC current.

- get_ac_current_MODEL(*model_id* [, *range* [, *resolution* [, *channel* ]]])

  Measure AC current.

- get_2w_resistance_MODEL(*model_id* [, *range* [, *resolution* [, *channel* ]]])

  Measure 2-wire resistance 

- get_4w_resistance_MODEL(*model_id* [, *range* [, *resolution* [, *channel* ]]])

  Measure 4-wire resistance

- get_frequency_MODEL(*model_id* [, *range* [, *resolution* [, *channel* ]]])

  Measure frequency

- get_period_MODEL(*model_id* [, *range* [, *resolution* [, *channel* ]]])

  Measure period

- get_error_queue_MODEL (*model_id* )

  Get queue of errors.

.. note:: As hinted out by the optional arguments on the list of functions, the arguments passed through to the model function will depend on the capabilities of that particular PS model. cmd_ps uses the API exchange mechanism to determine them. 

API
===

.. automodule:: cmd_multimeter
   :members:
   :member-order: bysource

