Performance
===========
This section gives examples of the following performance functionality:

- `Registering an Array For Performance Data Collection`_
- `Diagnostic Metrics Gathering`_
- `Real-Time Metrics Gathering`_
- `Backup Performance Database`_
- `Thresholds`_

Registering an Array For Performance Data Collection
----------------------------------------------------

Arrays can be enabled for both diagnostic and real-time performance data
collection using PyU4V. The example below demonstrates enabling both varieties
and confirming the registration has been successful.

.. literalinclude:: code/performance-registration.py
    :linenos:
    :language: python
    :lines: 14-38


Diagnostic Metrics Gathering
----------------------------

This example demonstrates a range of diagnostics (5 minute interval)
performance functionality such as getting performance categories and metrics,
timestamps from Unisphere for an array, get recent only performance
information, and getting ResponseTime for all SRPs in an array.

.. literalinclude:: code/performance-diagnostic_calls.py
    :linenos:
    :language: python
    :lines: 14-64


Real-Time Metrics Gathering
---------------------------

With the PyU4V 9.2 release it is possible to retrieve real-time performance
data from Unisphere for arrays which have been registered for real-time data.
This example demonstrates getting supported real-time peformance metrics for
a given category, getting the keys for that category (the assets which we
can obtain real-time data for), and retrieving real-time data for the last
hour.

.. note::
    The maximum amount of real-time data that can be retrieved from Unisphere
    via PyU4V in one call is one hour. If more than one hour of data is
    required then more calls can be run, however if you find yourself doing
    this often it is a good idea to save data locally for easy retrieval and
    reduce the amount of REST calls required.

.. note::
    Storage Groups are supported for real-time metrics but these **must** be
    enabled in Unisphere via ``Settings > Performance > System Registrations``.
    Under the table heading ``Storage Group Real Time`` and for the array you
    want to enable real-time for, select the option
    ``Real Time Storage Groups`` and add up to 100 Storage Groups for real-time
    data collection.

.. literalinclude:: code/performance-real_time_calls.py
    :linenos:
    :language: python
    :lines: 14-55


Backup Performance Database
---------------------------

Backup of a performance database is a recommended practice. The backup
performance database option is available for one or more storage systems,
regardless of their registration status.

By default, only Trending & Planning (Historical) data is backed up. The
performance databases backups should be stored in a safe location. Performance
database backups can be restored. For more information on restoring backups
please see Unisphere for PowerMax official documentation, for now only
performing backups is supported via REST.

To create a backup of a performance data simply call
``performance.backup_performance_database()``, both the ``array_id`` and
``filename`` are optional values, if no ``filename`` is provided then the
client hostname will be used.

.. note::
    Underscores will be stripped from any filename provided, this is due to
    Unisphere restricting the length of the filename string when underscores
    are provided. The backup filename format will be as follows when viewed in
    Unisphere: ``{array_id}_{date}{time}_{TZ}_{filename}_SPABackup.dat``

.. literalinclude:: code/performance-db_backup.py
    :linenos:
    :language: python
    :lines: 14-26

To view this performance database backup in Unisphere navigate to
``Settings > Unisphere Databases > Performance Databases``. Use the performance
databases list view to view and manage databases.


Thresholds
----------

In this example both performance threshold calls and CSV file handling with
PyU4V are demonstrated.  A call is made to retrieve a full list of performance
threshold settings and output the results to a CSV file at a path specified
by the user. That CSV file is read into a Python dictionary and the respective
values within are updated. Once complete the updated threshold settings are
uploaded to Unisphere to take immediate effect.

.. literalinclude:: code/performance-thresholds.py
    :linenos:
    :language: python
    :lines: 14-59
