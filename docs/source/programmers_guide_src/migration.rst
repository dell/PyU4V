Migration
=========
This section gives examples of migration functionality for non-disruptive
data migration between PowerMax arrays.

- `Migration Operations`_

Migration Operations
--------------------
This example demonstrates checking migration capabilities, creating a migration
environment between two arrays, initiating a storage group migration session,
performing cutover and commit operations, and cleaning up the migration
environment when complete.

.. literalinclude:: code/migration-operations.py
    :linenos:
    :language: python
    :lines: 15-70
