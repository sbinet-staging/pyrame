=====================
How to install Pyrame
=====================

.. note:: Pyrame needs root priviledges to be installed and, depending on the modules used, also to be executed. Install it and use it as root, or otherwise use sudo as needed.

Dependencies on Scientific Linux 6.6
====================================

Install the dependencies:

.. code:: bash

    yum -y install epel-release
    yum -y install gcc gcc-c++ python python-devel python-pip expat-devel lua-devel python-pip

If you want to generate the documentation, install also:

.. code:: bash

    pip install --upgrade docutils Pygments sphinx pyserial notify2 argparse

If you want to use the websocket to pyrame binding, install also:

.. code:: bash

    yum -y install httpd mod_python

Dependencies on Debian-based distribution
=========================================

Install the dependencies:

.. code:: bash

    apt-get -y install gcc g++ python python-dev python-pip libexpat1-dev liblua5.1-dev python-pip

If you want to generate the documentation, install also:

.. code:: bash

    pip install --upgrade docutils Pygments sphinx pyserial notify2 argparse

If you want to use the websocket to pyrame binding, install also:

.. code:: bash

    apt-get -y install apache2 libapache2-mod-python


Installation
============

.. warning:: If you have a previous version of Pyrame it is important to go to the sources of that version, and `make uninstall`. This will avoid conflicts with the new version. If you want to clean even more, remove /opt/pyrame

Get the source code from our `website <http://llr.in2p3.fr/sites/pyrame>`_

.. note::
    In Debian systems you might need to create links for lua.h and liblua.so::

        updatedb
        ln -s `locate -b "\liblua5.1.so"` /usr/lib/liblua.so
        ln -s /usr/include/lua5.1/lua.h /usr/include/lua.h

Get into it, compile and install. The installation path is /opt/pyrame/ :

.. code:: bash
    
    tar -xf pyrame_latest.tgz
    cd pyrame
    make install

To compile the documentation, go into docs and make:

.. code:: bash

    cd docs
    make install

The documentation will be accessible at /opt/pyrame/doc/index.html

In order to use the websocket to pyrame binding, do:

Install pywebsocket:

.. code:: bash

    cd /tmp
    svn checkout http://pywebsocket.googlecode.com/svn/trunk/ pywebsocket-read-only
    cd pywebsocket-read-only/src/
    python setup.py build
    sudo python setup.py install

then, if using Scientific-Linux 6.6:

.. code:: bash

    echo "PythonOption mod_pywebsocket.handler_root /opt/pyrame/" > /etc/httpd/conf.d/mod_pywebsocket.conf
    echo "PythonHeaderParserHandler mod_pywebsocket.headerparserhandler" >> /etc/httpd/conf.d/mod_pywebsocket.conf

if using a Debian-based distribution:

.. code:: bash

    echo "PythonOption mod_pywebsocket.handler_root /opt/pyrame/" > /etc/apache2/conf-available/mod_pywebsocket.conf
    echo "PythonHeaderParserHandler mod_pywebsocket.headerparserhandler" >> /etc/apache2/conf-available/mod_pywebsocket.conf
    ln -s /etc/apache2/conf-available/mod_pywebsocket.conf /etc/apache2/conf-enabled/mod_pywebsocket.conf

If you are using SELINUX, disable it. For Scientific-Linux 6.6 set SELINUX=permissive or SELINUX=disabled in /etc/selinux/config. Then reboot or do:

.. code:: bash

    echo 0 > /selinux/enforce
