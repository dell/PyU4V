Replication
===========
This section gives examples of the following replication functionality:

- `Local Replication with SnapVX`_
- `Snapshot Policies`_
- `Remote Replication with SRDF`_
- `Remote Replication with SRDF Metro Smart DR`_

Local Replication with SnapVX
-----------------------------

In this example a new storage group is created with a single 1GB volume. A
snapshot name is generated using the current time so it can be easily
identified, and the storage group snapshot is created. The operation is
verified by querying for a list of snapshots for a given storage group and
confirming the snapshot we created is present in that list.

.. literalinclude:: code/replication-snapshot_create.py
    :linenos:
    :language: python
    :lines: 14-47

This example will create a storage group with a volume, create a snapshot
of that storage group and link the snapshot to a new storage group. This is a
typical workflow for provisioning a dev environment and making a copy
available.

.. literalinclude:: code/replication-snapshot_link.py
    :linenos:
    :language: python
    :lines: 14-46


Snapshot Policies
-----------------
The Snapshot policy feature provides snapshot orchestration at scale (1,024
snaps per storage group). The feature simplifies snapshot management for
standard and cloud snapshots.

Snapshots can to be used to recover from data corruption, accidental deletion
or other damage, offering continuous data protection. A large number of
snapshots can be difficult to manage. The Snapshot policy feature provides an
end to end solution to create, schedule and manage standard (local) and cloud
snapshots.

For full detailed information on snapshot policies in Unisphere for PowerMax
please consult the official Unisphere for PowerMax online help guide.

In the example below a new snapshot policy is created, modified, then deleted.

.. literalinclude:: code/replication-snapshot_policy.py
    :linenos:
    :language: python
    :lines: 14-56

Snapshot Policy Compliance
--------------------------
This allows the user to query snapshot policy compliance over a period of time.
Last week, last four weeks, epoch to/from, human readable to/from are
supported.

For full detailed information on snapshot policies in Unisphere for PowerMax
please consult the official Unisphere for PowerMax online help guide.

In the example below a new snapshot policy is created, modified, then deleted.

.. literalinclude:: code/replication-snapshot-policy-compliance.py
    :linenos:
    :language: python
    :lines: 14-81



Remote Replication with SRDF
----------------------------

This example will create a storage group on the PowerMax array with some
volumes.  Once the storage group has been created it will protect the volumes
in the storage group to a remote array using SRDF/Metro, providing
Active/Active business continuity via Symmetrix Remote Data Facility (SRDF).

.. literalinclude:: code/replication-srdf_protection.py
    :linenos:
    :language: python
    :lines: 14-57

Remote Replication with SRDF Metro Smart DR
--------------------------------------------

SRDF/Metro Smart DR is a two region High-Availability (HA) Disaster Recovery
(DR) solution. It integrates SRDF/Metro and SRDF/A, enabling HA DR for an
SRDF/Metro session. By closely coupling the SRDF/A sessions on both sides of
an SRDF/Metro pair, SRDF/Metro Smart DR can replicate to a single DR device.

SRDF/Metro Smart DR environments are identified by a unique name and contain
three arrays (MetroR1, MetroR2, and DR). For SRDF/Metro Smart DR, arrays
must be running PowerMaxOS 5978.669.669 or higher.

This example will create a storage group on the PowerMax array with some
volumes.  Once the storage group has been created it will protect the volumes
in the storage group to a remote array using SRDF/Metro DR.

Note once Metro DR is setup, the environment is controlled exclusively by
the environment name.  SRDF Metro and SRDF/A replication can not be
controlled by standard Replication Calls without first deleting the Metro DR
environment.

For more information on SRDF/Metro Smart DR, please refer to Dell EMC
Solutions Enabler SRDF Family CLI user guide available
on https://support.dell.com

.. literalinclude:: code/replication-metro_dr.py
    :linenos:
    :language: python
    :lines: 14-55