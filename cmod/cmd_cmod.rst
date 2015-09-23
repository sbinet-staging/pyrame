========================
The configuration module
========================

This configuration module (called cmod) is dedicated to configuration storage and export.

Every Pyrame module can register in the cmod and store its configuration parameters.
The modules are stored in a tree representing the arborescence of the system.

The cmod contains at any time a copy of the configuration of all the modules and it can generate xml files containing all that parameters for using with :doc:`calxml <calxml>`.

 
API
===

.. automodule:: cmd_cmod
    :members: 
    :member-order: bysource
