=============================
The variables module (varmod)
=============================

The varmod is a centralized service that allow all the modules to share variables for collecting statistics or sharing global informations.

It allows to store a value associated with a name (a variable), to get it back. It also allows to make some basic operations on the variables : 

- intopvar provides any integer operations on variables. The operator can be + - x or / providing the corresponding arithmetic operation.
- stropvar provides string operations. The operator can be only 'c' at that time corresponding to the concatenation operation.


API
===

.. automodule:: cmd_varmod
    :members: 
    :member-order: bysource



