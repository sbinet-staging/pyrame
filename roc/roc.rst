==============
Read Out Chips
==============

Pyrame has a number of modules able to generate and manipulate the bitstreams for several read out chips (ROCs).

.. toctree::
    :titlesonly:

    Omega SKIROC2 <cmd_skiroc>
    Omega SPIROC2 <cmd_spiroc>
    Omega EASIROC <cmd_easiroc>
    Omega MAROC3 <cmd_maroc3>

Common functions
================

All modules for ROCs have at least 5 functions:

- init_MODULE
- deinit_MODULE
- config_MODULE
- set_missing_MODULE
- dump_sc_MODULE

The first three act according to :doc:`Pyrame's phases <phases>`. set_missing tags a chip as not present in a card although being initialized. dump_sc returns the bitstream of that chip.
