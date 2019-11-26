.. PyU4V documentation master file, created by
   sphinx-quickstart on Mon Jan 29 10:39:03 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PyU4V's documentation!
=================================

.. toctree::
   :maxdepth: 2
   :hidden:

   installation
   quick_start
   tools
   api

Overview
--------

PyU4V is a python module that simplifies integration with the Unisphere for VMAX RestAPI interface.

It wraps REST calls with simple APIs and abstracts the HTTP request and
response handling. For specifics on API arguments, consult the REST API
guide for the VMAX release currently running on the target array. To get this documentation,
navigate to https://{ip-address}:{port-number}/univmax/restapi/docs,
where {ip-address}: the ip of your Unisphere server and {port-number}: the corresponding
port to connect through, eg: https://10.0.0.1:8443/univmax/restapi/docs.

Getting Started
---------------

:doc:`installation`
  How to get the source code, and how to build or install the python package.

:doc:`quick_start`
  A quick start guide for PyU4V.

:doc:`tools`
  The tools guide for PyU4V

:doc:`api`
  A glossary of all available functions.

Supported Versions
------------------

PyU4V supports Unisphere for VMAX version 8.4 and higher. VMAX 3 and VMAX All Flash arrays are supported.
PyU4V officially supports Python 2.7 & 3.4-3.7 (but do remember that Python 2 will soon be `retired <https://pythonclock.org/>`_.)

Please note that PyU4V V3.0 is NOT BACKWARDS COMPATIBLE with existing scripts written for previous versions of PyU4V,
and does not support any Unisphere for VMAX version earlier that 8.4. PyU4V version 2.0.2.6 is still available on Pip,
and there is a 'stable/2.0' branch available on Github. Version 3 will be the version maintained going forward, and we
do suggest you move to this version when possible.


Feedback, Bug Reporting, Feature Requests
-----------------------------------------

We greatly value your feedback! Please file bugs and issues on the `Github issues page for this project <https://github.com/MichaelMcAleer/PyU4V/issues>`_.
This is to help keep track and document everything related to this repo. The code and documentation are released with no warranties or
SLAs and are intended to be supported through a community driven process.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


