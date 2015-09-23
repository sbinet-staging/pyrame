======================
API exchange mechanism
======================

Pyrame provides an API exchange mechanism between modules in order to determine the existence of functions and list of their parameters on any module. The `module_makefile` Makefile provided on the root of Pyrame sources generates, at installation time a `.api` file for each Python module through the script `gen_api.py`. This file contains a list of the public functions of the module (as declared on the XML file), and their respective parameters.

Two Python modules are provided:

1. getapi eases the implementation of the standard `getapi_MODULE()`. This is a function that sends a serialized API back as return value. It can be implemented, like::

    import getapi
    # Put serialized API in memory if not called via import
    if __name__ == '__main__':
        global api; api = getapi.load_api(__file__)

        def getapi_th_apt():
            submod.setres(1,api)


  The ``if __name__ == '__main__'`` condition, prevents from trying to read the .api file while generating it with gen_api.py, which needs to import the module. 

  The serialized API is a semicolon-separated string with the prototypes of the public functions in the module. Each function must be composed of its name, a colon and list comma-separated arguments. For example ::

    getapi_ag_e3631a:;init_ag_e3631a:conf_string;deinit_ag_e3631a:ag_e3631a_id;power_on_ag_e3631a:ag_e3631a_id;power_off_ag_e3631a:ag_e3631a_id;set_voltage_ag_e3631a:ag_e3631a_id,voltage,channel;set_current_ag_e3631a:ag_e3631a_id,current,channel;get_voltage_ag_e3631a:ag_e3631a_id,channel;get_current_ag_e3631a:ag_e3631a_id,channel;

2. The apipools module allows to keep a pool of APIs in memory and to parse the serialized API. The pool provides functions like: get_api (from the pool) and is_present (in the pool). See the its API below. A JavaScript implementation of apipools also exists.

apipools API
============

.. automodule:: apipools
    :members:
    :member-order: bysource
