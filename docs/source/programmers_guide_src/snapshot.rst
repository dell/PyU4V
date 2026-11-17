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

Finding expired snapshots
-------------------------
Expired-snapshot discovery lists replication storage groups without the
``hasSnapshots`` server filter, which some arrays reject with HTTP 500.
It then reads each group's replication details and skips groups without
snapshots. This may require more requests on arrays with many replication
groups. The legacy ``conn.replication`` methods use the same discovery path.

With an existing connection, this read-only call reports expired linked
snapshots without deleting them::

    expired = conn.snapshot.find_expired_snapvx_snapshots_by_snap_ids()
    for snapshot in expired:
        print(snapshot['storagegroup_name'], snapshot['snapshot_name'],
              snapshot['snap_id'], snapshot['linked_sg_name'])
