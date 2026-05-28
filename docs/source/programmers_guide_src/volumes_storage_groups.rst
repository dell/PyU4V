Volumes & Storage Groups
========================
This section gives examples of the enhanced v1 API functionality for
querying volume and storage group details in bulk.

These modules use the enhanced REST API endpoints which provide filtering
and attribute selection to efficiently retrieve large datasets.

- `Volumes & Storage Groups Queries`_

Volumes & Storage Groups Queries
--------------------------------
This example demonstrates querying volume and storage group metadata,
retrieving details with attribute selection, and applying filters to
narrow results.

.. literalinclude:: code/volumes-storage_groups.py
    :linenos:
    :language: python
    :lines: 15-54
