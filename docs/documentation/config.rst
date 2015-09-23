============================
The configuration management
============================


If Pyrame is used in a complex setup, it can be boring to set all the parameters by hand. In the same way, we would like to get a way to save the complete configuration of the system. 
Pyrame provides two mechanisms with a common format to achive this goal : 

- The :doc:`configuration module <cmd_cmod>` (named cmod) is a storage module dedicated to hardware description and configuration parameters.
- The :doc:`calxml <calxml>` module allows to dispatch a set of parameters across a whole setup.
- Both modules use the same :doc:`format <calxml_format>` based on xml to describe the system and the parameters.

See the complete documentation of these modules on the following pages : 

.. toctree::
    :maxdepth: 4
    :titlesonly:

    cmd_cmod
    calxml
    calxml_format
