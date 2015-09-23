======
Phases
======

Many Pyrame modules present four phases: initialization, configuration, invalidation and deinitialization.  which allow them to interact with the abstraction layers. Although not mandatory in general, modules interacting with abstracting layers (e.g. :doc:`ps <cmd_ps>` or :doc:`motion <cmd_motion>`) must follow this model.

Initialization must be implemented by an init_MODULE function. It prepares the module to perform its tasks although but never communicates with hardware. It can communicate, however, with other modules. Usually, it creates a new object in a pool and initializes variables or properties to the adequate values.

Configuration must be implemented by a config_MODULE function. It finishes the preparation of the module and performs any necessary communication with the hardware.

Invalidation must be implemented by a inval_MODULE function. It prepares the module to be configured once again. Can communicate with hardware.

Deinitialization must be implemented by a deinit_MODULE function. It removes all memory structures that were allocated during initialization. Cannot communicate with hardware.
