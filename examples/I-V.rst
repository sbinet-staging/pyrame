Example: I(V) curve
===================

A common measure in a laboratory is the mesurement of the current vs voltage response of a sample. This examples shows an example of code written in Python which takes an I(V) curve using Pyrame modules. Configuration strings for the :doc:`Agilent 34401A <cmd_ag_34401a>` and :doc:`Keithley 6487 <cmd_mm_ki_6487>` multimeters and for the power supply within the :doc:`Keithley 6487 <cmd_ki_6487>`, are given. Obviously, only two of the three should be used for an I(V) curve (one for power supply and one for multimeter).

The use of a helper function like `sendcmd` allows to reduce the amount of boilerplate code.

.. literalinclude:: ../../../examples/I-V.py
    :linenos:
    :language: python
