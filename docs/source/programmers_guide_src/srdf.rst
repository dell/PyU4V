SRDF
====
This section demonstrates the ``conn.srdf`` module which provides dedicated
SRDF (Symmetrix Remote Data Facility) management functions.

.. note::
    These functions were previously available only via ``conn.replication``.
    The ``conn.replication`` path still works but emits a deprecation warning.
    New code should use ``conn.srdf`` directly.

- `RDF Director & Port Discovery`_
- `RDF Group Management`_
- `Storage Group SRDF Protection`_
- `SRDF State Management`_

RDF Director & Port Discovery
-----------------------------
Discover RDF directors, their ports, and scan for remote connections.
This is typically the first step when setting up a new SRDF configuration.

.. literalinclude:: code/srdf-operations.py
    :linenos:
    :language: python
    :lines: 15-49

RDF Group Management
--------------------
List, inspect, and look up RDF groups.  Query volumes within an RDF group
and filter groups by remote array, mode, or type.

.. literalinclude:: code/srdf-operations.py
    :linenos:
    :language: python
    :lines: 51-74

Storage Group SRDF Protection
-----------------------------
Create a storage group, protect it with SRDF replication to a remote array,
and query the resulting SRDF pairings.

.. literalinclude:: code/srdf-operations.py
    :linenos:
    :language: python
    :lines: 76-99

SRDF State Management
---------------------
Manage the SRDF replication state: suspend, establish, failover, failback,
change mode, and delete pairings.

.. literalinclude:: code/srdf-operations.py
    :linenos:
    :language: python
    :lines: 101-137
