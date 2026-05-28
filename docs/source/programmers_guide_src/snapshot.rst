Snapshots (SnapVX)
==================
This section demonstrates the ``conn.snapshot`` module which provides
dedicated SnapVX snapshot management functions.

.. note::
    These functions were previously available only via ``conn.replication``.
    The ``conn.replication`` path still works but emits a deprecation warning.
    New code should use ``conn.snapshot`` directly.

- `Snapshot Operations`_

Snapshot Operations
-------------------
This example covers the full snapshot lifecycle: checking SnapVX licensing,
creating snapshots (with and without TTL), listing and querying snap IDs,
linking/unlinking to target storage groups, renaming, finding expired
snapshots, and deleting.

.. literalinclude:: code/snapshot-operations.py
    :linenos:
    :language: python
    :lines: 15-92
