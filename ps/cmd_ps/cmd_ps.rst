=========================
The power supplies module
=========================

Abstraction module for power supplies (PS). The ps module (cmd_ps) allows the transparent use of a pool of an undefined number of PS regardless of maker, model or host-device link technology. Its function is to redirect the requests and orders made to it, to a module that knows how to interface with that particular PS. That module can in turn use one of the available lower-level interfacing modules (:doc:`GPIB <cmd_gpib>`, :doc:`TCP <cmd_tcp>`, :doc:`serial <cmd_serial>`).

As of this writing, modules for the following PS are implemented:

.. toctree::
    :titlesonly:

    Agilent E3631A <cmd_ag_e3631a>
    Agilent N6700B <cmd_ag_n6700b>
    CAEN SY527 <cmd_ca_sy527>
    Hameg HMP4030 <cmd_ha_hmp4030>
    Keithley 6487 <cmd_ki_6487>
    TDK-Lambda Genesys GEN8-90 <cmd_la_gen8_90>

On the following, the ps module and the way to implement new PS modules is described. For information on how to interface with the bus modules, refer to :doc:`their documentation <buses>`.

.. figure:: cmd_ps.doc.png
    :align: center
    :scale: 50%

    Figure 1: Example of interaction between cmd_ps, PS modules and pyrame bus modules (gpib, serial, tcp). 

Pool and identification
=======================

Every PS in the pool gets assigned an identification token (*id* >= 0) which identifies it uniquely during the execution of Pyrame. All functions of cmd_ps, except :py:func:`init_ps <cmd_ps.init_ps>`, require this *id* token as the first argument. The assignment of *id* is done by init_ps and constitutes its return value. Along with the *id* (integer), cmd_ps also stores the *model* (string) and *model_id* (string) parameters; *model* being the PS module to which address requests and orders, and *model_id* the identification token from the model pool.

During init_ps, the initialization function for the particular model is called. Its name must be *init_MODEL* (e.g.: :py:func:`init_ag_e3631a <cmd_ag_e3631a.init_ag_e3631a>`). The conventionstyle for MODEL is a two-letter maker symbol plus the model, separated by an underscore (_). The init_MODEL function returns *model_id* which must unambiguously identify the PS among others of the same model. Any other function from the PS module must be able to determine how to address the required PS only based on its *model_id*.

Initialization
==============

As pointed out previously, cmd_ps provides a function init_ps and requires functions init_MODEL from the modules with which it interfaces. The init_ps declaration is:

.. py:function:: init_ps (conf_string)

    Registers in the pool and initializes a new PS. *conf_string* is the configuration string for the module to be initialized.

    Returns its *ps_id*. 

Functions
=========

A series of functions in cmd_ps interface the corresponding functions on the PS modules. In most cases, a call to the function of the same name is performed (replacing _ps by _MODEL). All PS models must include, at least, an implementation of the following functions:

- getapi_MODEL ()
- init_MODEL (*conf_string*)
- deinit_MODEL (*model_id*)
- config_MODEL (*model_id*)
- inval_MODEL (*model_id*)

Optionally, these functions can also be implemented:

- set_voltage_MODEL (*model_id*, *voltage* [, *channel*[, *slew_rate*]])
- set_current_MODEL (*model_id*, *current* [, *channel*])
- power_on_MODEL (*model_id* [, *channel*])
- power_off_MODEL (*model_id* [, *channel*])
- get_voltage_MODEL (*model_id* [, *channel*])
- get_current_MODEL (*model_id* [, *channel*])
- set_voltage_limit_MODEL (*model_id*, *voltage_limit* [, *channel*])
- set_current_limit_MODEL (*model_id*, *current_limit* [, *channel*])
- set_rise_delay_MODEL (*model_id*, *rise_delay*, *channel*)
- get_error_queue_MODEL (*model_id*)

In all cases:

- Magnitudes (i.e.: voltage, current, slew_rate, etc.), either sent or returned, must be expressed in base units of the International System of Units (V, A, V/s, etc.).

It is advisable that functions check and flush the error queue of the device after every command, on devices that provide this functionality. In case of error, return the queue elements separated by semicolons (;).

The functionality provided by each of the functions is primarily the following:

    set_voltage_MODEL (*model_id*, *voltage* [, *channel*[, *slew_rate*]])

        Set voltage on channel or PS at the specified slew rate. A previous call to set_current_limit is necessary.

    set_current_MODEL (*model_id*, *current* [, *channel*])

        Set current on channel or PS. A previous call to set_voltage_limit is necessary.

    power_on_MODEL (*model_id* [, *channel*])

        Power on channel or PS.

    power_off_MODEL (*model_id* [, *channel*])

        Power off channel or PS.

    get_voltage_MODEL (*model_id* [, *channel*])

        Get voltage from channel or PS. Preferentially measured, not setpoint reading.

    get_current_MODEL (*model_id* [, *channel*])

        Get current from channel or PS. Preferentially measured, not setpoint reading.

    set_voltage_limit_MODEL (*model_id*, *voltage_limit* [, *channel*])

        Set voltage limit on channel. When available, use a Over Voltage Protection setting.

    set_current_limit_MODEL (*model_id*, *current_limit* [, *channel*])

        Set current limit on channel. When available, use a Over Current Protection setting.

    set_rise_delay_MODEL (*model_id*, *rise_delay*, *channel*)

        Set delay between receiving power-on command and actually engaging on channel.

    get_error_queue_MODEL (*model_id*)

        Get queue of errors.

.. note::

    As hinted out by the optional arguments on the list of functions, the arguments passed through to the model function will depend on the capabilities of that particular PS model. cmd_ps uses the :doc:`API exchange mechanism <getapi>` to determine them.

API
===

.. automodule:: cmd_ps
   :members:
   :member-order: bysource

