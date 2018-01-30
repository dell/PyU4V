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
   api

Overview
--------

PyU4V is a python module that simplifies integration with the Unisphere for VMAX REST interface.

It wraps REST calls with simple APIs and abstracts the HTTP request and
response handling. For specifics on API arguments, consult the REST API
guide for the VMAX release currently running on the target array. To get this documentation,
navigate to https://<ip-address>:<port-number>/univmax/restapi/docs,
where <ip-address> = the ip of your Unisphere server and <port-number> = the corresponding
port to connect through, eg: https://10.0.0.1:8443/univmax/restapi/docs.

:doc:`installation`
  How to get the source code, and how to build or install the python package.

:doc:`quick_start`
  A quick start guide for PyU4V.

:doc:`api`
  A glossary of all available functions.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
