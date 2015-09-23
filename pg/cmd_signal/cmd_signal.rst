==================
Pattern generation
==================

Abstraction module for signals. The signal module allows the creation of signals entities, characterized by a series of parameters and linked to a particular pattern generator (PG). The signal module is agnostic about the PG. Communicates to the device via a secondary module from which it requires a specific API. It is up to that module to send the appropriate commands to the PG. The module can use (or not) one of the available lower-level interfacing modules (:doc:`GPIB <cmd_gpib>`, :doc:`TCP <cmd_tcp>`, :doc:`serial <cmd_serial>`).

As of this writing, modules for the following PG are implemented:

.. toctree::
    :titlesonly:

    Agilent 33200 series <cmd_ag_33200>
    Agilent 33500 series <cmd_ag_33500>
    Agilent 81160 <cmd_ag_81160>

On the following, the signal module and the way to implement new PG modules compatible with it is described. For information on how to interface with the bus modules, refer to :doc:`their documentation <buses>`.

.. figure:: cmd_signal.doc.png
    :align: center
    :scale: 50%

    Figure 1: Example of interaction between cmd_signal, PG modules and pyrame bus modules (gpib, serial, tcp). 

Pool and identification
=======================

Every signal in the pool gets assigned an identification token (*id* >= 0) which identifies it uniquely during the execution of Pyrame. All functions of cmd_signal, except :py:func:`init_signal <cmd_signal.init_signal>` and :py:func:`init_signal.init_pg_signal>`, require this *id* token as the first argument. The assignment of *id* is done by init_signal and constitutes its return value. cmd_signal stores the *id* (integer) and other parameters characterizing the signal on an object of in a pool:

During init_pg_signal, the initialization function for the particular model is called. Its name must be *init_MODEL* (e.g.: :py:func:`init_ag_33200 <cmd_ag_33200.init_ag_33200>`). The convention style for MODEL is a two-letter maker symbol plus the model, separated by an underscore (_). The init_MODEL function returns *MODEL_id* which must unambiguously identify the PG among others of the same model. Any other function from the PG module must be able to determine how to address the required PG only based on its *MODEL_id*.

Initialization
==============

There is a minumum of two mandatory init steps to be carried out: :py:func:`init_signal <cmd_signal.init_signal>` and :py:func:`init_pg_signal <cmd_signal.init_pg_signal>`. The former creates the object where the characteristics of the signal will be stored and adds the object to the signal pool. The latter initializes a PG using the module specified through the *conf_string* parameter and adds the PG to the PG pool:

.. py:function:: init_pg_signal (conf_string)

    Initialize pattern generator where *conf_string* is the conf_string of the pattern generator to be initialized.

    Returns id of the pattern generator *pg_id*

After initialization, the function :py:func:`set_pg_signal <cmd_signal.set_pg_signal>` can be used to associate a PG to a signal, and :py:func:`conf_pg_signal <cmd_signal.conf_pg_signal>` to configure the pg.

The only functions of cmd_signal that interact with the PG module are :py:func:`init_pg_signal <cmd_signal.init_pg_signal>`, :py:func:`deinit_pg_signal <cmd_signal.deinit_pg_signal>`, :py:func:`conf_pg_signal <cmd_signal.conf_pg_signal>`, :py:func:`inval_pg_signal <cmd_signal.inval_pg_signal>`, :py:func:`power_on_signal <cmd_signal.power_on_signal>` and :py:func:`power_off_signal <cmd_signal.power_off_signal>`. All other functions only change the signal object in memory and only while the *power* flag of the signal is off (0). A signal can be powered on with :py:func:`power_on_signal <cmd_signal.power_on_signal>` and off with :py:func:`power_off_signal <cmd_signal.power_off_signal>`.

The init_MODEL functions of pattern generators must accept a conf_string and initialize all necessary memory structures. Communication with the hardware is performed with the config_MODEL function.

Functions
=========

cmd_signal requires a set of functions on the API of the PG module in order to be compatible with it:

- getapi_MODEL ()
- init_MODEL (*conf_string*)
- deinit_MODEL (*MODEL_id*)
- config_MODEL (*MODEL_id*)
- inval_MODEL (*MODEL_id*)
- power_on_MODEL (*MODEL_id* [, *channel*])
- power_off_MODEL (*MODEL_id* [, *channel*])

In order to provide support for the phase and sync output settings, the following functions can be implemented:

- set_phase_MODEL (*MODEL_id*, *phase* [, *channel*])
- set_sync_MODEL (*MODEL_id*, *sync* [, *channel*])

In addition, at least one configure\_FUNCTION function must be implemented. Each one will provide support for the FUNCTION (e.g.: sine) function, as configured with :py:func:`set_function_signal <cmd_signal.set_function_signal>`. The :py:func:`power_on_signal <cmd_signal.power_on_signal>` function of cmd_signal will look for a matching configure\_FUNCTION function in the module. configure\_FUNCTION functions must have a first mandatory *MODEL_id* parameter and then a list of parameters from the following list and respecting the same order:

- frequency
- high_level
- low_level
- duty_cycle
- symmetry
- pulse_width
- rising_edge
- falling_edge
- channel

For example, a dead-simple pattern generator not capable of any configuration could well be driven by a module only providing `configure_sine(*MODEL_id*)`, in case the output function would be a sine wave without configurable parameters. More complex pattern generators can, on the other hand, provide functions such as:

- configure_wave_MODEL (*MODEL_id*, *high_level*, *low_level*)
- configure_sine_MODEL (*MODEL_id*, *frequency*, *high_level*, *low_level*)
- configure_square_MODEL (*MODEL_id*, *frequency*, *duty_cycle*, *channel*)
- configure_ramp_MODEL (*MODEL_id*, *high_level*, *low_level*, *symmetry*)
- configure_pulse_MODEL (*MODEL_id*, *frequency*, *high_level*, *low_level*, *pulse_width*, *rising_edge*, *falling_edge*, *channel*)

.. note::

    As hinted out by the optional arguments on the list of functions, the arguments passed through to the model function will depend on the capabilities of that particular PG model. cmd_signal uses the :doc:`API exchange mechanism <getapi>` to determine them.

In all cases:

- Magnitudes (i.e.: voltage, current, slew_rate, etc.), either sent or returned, must be expressed in base units of the International System of Units (V, A, V/s, etc.).

It is advisable that functions check and flush the error queue of the device after every command, on devices that provide this functionality. In case of error, return the queue elements separated by semicolons (;).

API
===

.. automodule:: cmd_signal
   :members:
   :member-order: bysource

