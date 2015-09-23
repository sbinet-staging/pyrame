=================
The motion module
=================

:doc:`motion <cmd_motion>` interfaces with the modules actually controlling the hardware and provides a unified API. The compatible modules presently implemented are:

.. toctree::
    :titlesonly:

    Thorlabs APT <cmd_th_apt>
    Newport ESP301 <cmd_nw_esp301>

Three axis must be defined to work with :doc:`motion <cmd_motion>`. This constitutes the motion system. Multiple motion systems can be defined.

Pool and identification
=======================

As usual in Pyrame, every motion system in the pool gets assigned an identification token (*id* >= 0) which identifies it uniquely during the execution of Pyrame. All functions of cmd_motion, except :py:func:`init_motion <cmd_motion.init_motion>`, require this *id* token as the first argument. The assignment of *id* is done by init_motion and constitutes its return value.

During init_motion, the initialization functions for the particular models is called. Their names must be *init_MODEL* (e.g.: :py:func:`init_th_apt <cmd_th_apt.init_th_apt>`). The conventionstyle for MODEL is a two-letter maker symbol plus the model, separated by an underscore (_). The init_MODEL function returns *model_id* which must unambiguously identify the motion controller among others of the same model. Any other function from the motion controller module must be able to determine how to address the hardware only based on its *model_id*.

Initialization
==============

As pointed out previously, cmd_motion provides a function init_motion and requires functions init_MODEL from the modules with which it interfaces. The init_motion declaration is:

.. py:function:: init_motion (conf_string1,conf_string2,conf_string3)

    Initialize motion system. Provide the :doc:`conf_strings <conf_strings>` for its three axis *csn* (for axis number n: 1,2,3)

    Returns its *motion_id*. 

Functions
=========

A series of functions in cmd_motion interface the corresponding functions on the motion controller modules. In most cases, a call to the function of the same name is performed (replacing _motion by _MODEL). All motion controller modules must include, at least, an implementation of the following functions:

- getapi_MODEL ()
- init_MODEL (*conf_string*)
- deinit_MODEL (*model_id*)
- config_MODEL (*model_id*, *max*, *min*)
- inval_MODEL (*model_id*)
- reset_MODEL (*model_id*, *direction*, *speed*)
- is_reset_MODEL (*model_id*)
- move (*model_id*, *displacement*, *speed*, *acceleration*)
- get_pos (*model_id*)


The functionality provided by each of the functions is primarily the following:

    reset_MODEL (*model_id*, *direction*, *speed*)

        Reset the axis so that the measured position is correct. Usually involves a homing procedure.

    is_reset_MODEL (*model_id*)

        Determine if the axis is reset (i.e. provides correct measured positions).

    move (*model_id*, *displacement*, *speed*, *acceleration*)
    
        Perform a relative *displacement* of the axis at *speed* with *acceleration*.

    get_pos (*model_id*)

        Get the present position of the axis.

API
===

.. automodule:: cmd_motion
    :members:
    :member-order: bysource
