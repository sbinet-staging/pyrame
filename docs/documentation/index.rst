
==================================
Welcome to Pyrame's documentation!
==================================

Pyrame is a fast prototyping framework for online systems. It provides basic blocks (called :doc:`modules <modules>`) of control-command or data acquisition. These blocks can be assembled together to quickly obtain complete systems for testbenches. The framework is very flexible and provides lots of options, allowing the system to evolve as fast as the testbench.

.. figure:: index1.doc.png
    :align: center
    :scale: 50%

    Figure 1: Pyrame architecture

Modules are connected together through a software bus and a specific :doc:`protocol <protocol>`. In order to ease the development of extensions, Pyrame uses open standards: TCP and XML. They are implemented on most platforms and in most languages. The use of TCP/IP eases the distribution of code on multi-computer setups, but also the use of embbeded platforms.

The global architecture of the system is based on a high level of modularity. Every module manages a very specific hardware and uses other modules to manage the lower level aspects.

The framework contains many modules to manage commonly used hardware: High and low voltage :doc:`power supplies <cmd_ps>` (Agilent, CAEN, Hameg, Keithley...), :doc:`Pattern generators <cmd_signal>` (Agilent), :doc:`digital oscilloscopes <dso>` (LeCroy), :doc:`motion controllers <motion>` (Newport, Thorlabs, Signatone), :doc:`gaussmeters <cmd_ls_421>` (LakeShore) and :doc:`bus <buses>` adapters (IEEE 488 / GPIB, USB, RS-232, Ethernet, UDP, TCP, ...)

Generic modules are also provided. They unify access to machines from different generations, providing native or emulated functions depending on the possibilities of the machines.

Pyrame provides a lot of service modules, easing the development of complex systems:

- A multi-media and high performance :doc:`acquisition chain <acq_server>`. With a plugin system, the chain can be adapted to any media and data format. The modules provided include raw Ethernet, UDP, TCP client or server side and Pyrame protocol. The chain allows to acquire data from different sources at the same time (multi-media) and also to synchronize data between them.
- The :doc:`variable module <cmd_varmod>` can be used to share string or numeric values between different modules of the system (statistics, state machine values, synchronisation informations, ...). The module allows to make simple operations on the values (concatenation, arithmetic operations, ...)
- The :doc:`configuration module <config>` provides for the rest of the modules a way of storing and sharing their configuration parameters in real-time. This provides a way to save the global configuration of the system in a XML file and to reload it at any time (with a symmetrical module).

The core of Pyrame is a generic :doc:`command module <cmdmod>` that allows to very easily implement the control of your hardware in Python. The command module handles all the Pyrame protocol part. Therefore, the online programmer can concentrate on the hardware specific part and :doc:`develop <howto_new_modules>` his/her module very quickly.

The protocol of Pyrame is open and very easy to implement. Pyrame provides a choice of :doc:`bindings <bindings>`: C, C++ and Python for generalist languages, but also R, LabView and Javascript. The coding of a new binding in another language is an easy and quick work.

On most of our test benchs, the PC can be replaced by a lighter platform. Pyrame can run on a Raspberry Pi and thus be an inexpensive control system.

The flexibility of a test bench allows the experimentalist to find quick solutions to his/her problems through embedded plateforms. That is why we provide a binding for the Arduino, effectively allowing it to act as a Pyrame module.

The performances of Pyrame are compatible with a real use. Data rates of up to 1.7 Gb/s on the acquisition chain and 1.6 ms per Pyrame command operation (without any chaining) can be obtained.

.. figure:: index2.doc.png
    :align: center
    :scale: 50%

    Figure 2: Example of architecture for an electromagnetic calorimeter experiment


Table of contents
================================

.. toctree::
    :maxdepth: 4
    :titlesonly:

    howto_install
    examples
    protocol
    modules
    bindings
    acq_server
    The configuration module <config>
    The configuration strings <conf_strings>
    The variables module <cmd_varmod>
    phases
    getapi
    Read Out Chips <roc>
    buses
    Power supplies <cmd_ps>
    Multimeters <cmd_multimeter>
    Pattern generation <cmd_signal>
    Motion <motion>
    Oscilloscopes <dso>
    Gaussmeters <cmd_ls_421>
