=================
Modules
=================

.. toctree::
    :titlesonly:

    howto_new_modules
    cmdmod

Modules are the bulding blocks of Pyrame. The stock distribution comes with a number of modules that act as drivers for input/output buses and external devices but also others such as the :doc:`acquisition chain <acq_server>`, :doc:`cmod <cmd_cmod>`, :doc:`cmd_varmod <cmd_varmod>` and others.

Pyrame modules can be written in any language as long as they conform to the :doc:`Pyrame protocol <protocol>`. Particularly, for modules written in Python, Pyrame provides :doc:`cmdmod <cmdmod>`, a wrapper that simplifies their development by mutualizing the network server and client, the XML and Pyrame protocol parsing and the control of public/private functions among others.

See the document :doc:`howto_new_modules` if you are interested in a practical approach to writing Pyrame modules.

For a reference description of cmdmod see :doc:`cmdmod <cmdmod>`.
