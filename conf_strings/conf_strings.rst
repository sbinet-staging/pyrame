=========================
The configuration strings
=========================

Many Pyrame module use a configuration string called conf_string. It allows to pass initialization parameters for a module in a single string with optional and named parameters. The format is:

    module_name(parameter_list)

    *parameter_list* is of the form param1=value1,param2=value2,param3=value3,etc.

There is no notion of order for the parameters, which are always named, and any of them can be optional, as enforced by the receiving module.

Values cannot contain commas nor equal signs. The only exception is when a value is also a conf_string. For example:

    gpib(dst_addr=3,bus=tcp(host=10.220.0.3,port=2300),adapter_addr=5)

This conf_string is destined to the GPIB module. It specifies a destination address (3), the underlying bus (TCP) and an adapter address (5). The latter is an optional parameter that otherwise defaults to value 0. The `bus` parameter is itself also a conf_string for the TCP module, containing the parameters `host` and `port`.

Pyrame provides a Python module (conf_strings) to parse and stringify conf_strings. See API below.

conf_strings API
================

.. automodule:: conf_strings
    :members:
    :member-order: bysource
