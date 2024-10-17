Quick Start Guide
=================

Initialise PyU4V
----------------

First, make sure that PyU4V is installed as directed in the
:doc:`installation`:

.. code-block:: bash

    $ pip show PyU4V

To initialise the connection with Unisphere use ``U4VConn``, it will load the
configuration provided in ``PyU4V.conf`` configured during installation:

.. code-block:: python

    import PyU4V
    conn = PyU4V.U4VConn()

With a connection to the Unisphere server you can start to run some test
queries to validate the successful connection.

.. code-block:: python

    conn.common.get_unisphere_version()
    ('V10.2.0.0', '101')
    conn.common.get_array_list()
    ["000197900123", "000197900124", "000197900125", "000197900126"]

If you want to query another array, you can set the ``array_id`` to a value of
your choice which overrides what is set in ``PyU4V.conf``. Alternatively you
can initialise a new PyU4V connection and pass in the ``array_id`` but load
all other configuration settings from ``PyU4V.conf``.

.. code-block:: python
    
    # Option 1 - Set new array ID in current PyU4V connection
    conn.set_array_id('000197900126')
    # Option 2 - Create new PyU4V connection using PyU4V.conf settings
    new_conn = PyU4V.U4VConn(array_id='000197900126')


PyU4V Unisphere REST Coverage
-----------------------------

The functions in PyU4V have been divided into logical categories which reflect
the various categories provided by the Unisphere REST API:

- Common - REST methods and assistive utilities
- Migration - all migration related calls
- Performance - all performance and threshold calls
- Real Time - all performance real-time calls
- Provisioning - all provisioning and masking related calls
- Replication - all local and remote replication calls
- Clone - Create and manage clone replicas of storage groups.
- Metro DR - all Metro DR calls
- Snapshot Policy - all Snapshot Policy calls
- System - all system level calls
- Workload Planner - all workload planner calls
- Utils - assistive functions to aid with PyU4V usage
- Enhanced API - Array & Performance, Bulk API calls to simplify and reduce the number of API calls needed to get information for Data Mining.

There are plans to further increase the coverage of Unisphere REST calls in
future releases. All changes are reflected in the PyU4V change log (link_).

Perform a Custom REST Call in PyU4V
-----------------------------------

At its core PyU4V is your typical REST client. It creates a request
header, defines any request parameters in JSON, sends the request with
an associated method which dictates the action being performed (``GET``,
``POST``, etc.), and expects a response payload in most instances (``DELETE``
calls tend to return a status instead of a response payload).

There are functions created in ``PyU4V.common`` which provide the ability to
perform ``GET``, ``POST`` and other request calls directly with the Unisphere
REST API to any supported endpoint.

- ``PyU4V.common.get_resource()`` - ``GET``
- ``PyU4V.common.create_resource()`` - ``POST``
- ``PyU4V.common.modify_resource()`` - ``PUT``
- ``PyU4V.common.delete_resource()`` - ``DELETE``

If there is any functionality that is provided by the Unisphere REST API that
is not yet implemented in PyU4V, it is possible to create a custom function
which use the above functions to make use of that functionality. For
information on the Unisphere REST API please consult its related documentation.

The Unisphere for PowerMax REST documentation is accessible directly from the
help menu in Unipshere or you can Navigate to
``https://developer.dell.com/apis/4458/versions/10.2/``

.. literalinclude:: programmers_guide_src/code/custom_call.py
    :linenos:
    :language: python
    :lines: 14-65

To find out more information on the any PyU4V calls refer to the supporting
function documentation in the :doc:`api` , there are also programmers
guide examples provided with this documentation which demonstrate a range of
functions using PyU4V.


.. Links

.. _link: https://github.com/dell/PyU4V/blob/master/ChangeLog
