System
======
This section gives examples of the following system functionality:

- `Health Checks`_
- `Audit Logs`_
- `Download & Upload Settings`_

Health Checks
-------------
This example of system calls demonstrates performing a system health check,
retrieving information from the last health check, querying for all installed
disk IDs in an array and outputting information about each.

.. literalinclude:: code/system-health_check.py
    :linenos:
    :language: python
    :lines: 14-35

Audit Logs
----------
The storage system audit records include all actions that are taken on that
storage system. The storage system audit records come from the SYMAPI database
and include all actions that are taken on that storage system. The audit log
resides on the storage system and currently has a maximum size of 40 MB. Once
the 40 MB limit is reached, the log begins to overwrite itself. Beginning in
Unisphere release 9.2, operations that are executed through Unisphere UI
have been added to the audit log.

.. warning::
    Audit logs can be very large. You are warned that the operation may take a
    long time if you attempt to retrieved audit log records for a time period
    of greater than 7 days.

In the example below a query is made to return audit logs for the last hour
which match a provided user name and client host name. A sample audit log
record is then queried to return more detailed information.

.. literalinclude:: code/system-audit_log_query.py
    :linenos:
    :language: python
    :lines: 14-44

In addition to querying audit logs via REST it is possible to download a PDF
audit log record for the previous week. The example below demonstrates this.

.. note::
    When providing a ``file_name`` there is no need to add the ``.pdf``
    extension, PyU4V will do this automatically.
.. note::
    When downloading an audit log record, it is possible to return the binary
    data instead of writing to pdf automatically, this allows you to handle
    the file writing process yourself. To do so just set
    ``return_binary=True``.  The data will be stored in the response dict
    under the key ``binary_data``.

.. literalinclude:: code/system-audit_log_download.py
    :linenos:
    :language: python
    :lines: 14-32

Download & Upload Settings
--------------------------
Unisphere allows an authorized user with appropriate access to manage system
settings. Settings can also be cloned, that is, settings can be copied from one
array and applied to one or more target arrays subject to compatibility checks.
In addition to cloning system settings from one array to another, it is also
possible to clone Unisphere settings from one instance to another.

The exported settings have a generic format and do not contain any specific
information regarding particular storage array or Unisphere instance, thus
making it applicable in any environment.

The intention is to help users to port the system wide settings to another
instance of Unisphere, and also to capture single array settings so that they
can be applied to another storage array within single instance or another
instance of Unisphere at any point of time.

The example below downloading system settings for the primary array and
applying those same settings to another array registered to the same instance
of Unisphere.

.. note::
    A file_password is required not to protect the file when it is downloaded
    to a local computer, it is to verify the settings when they are being
    applied to another system or instance of Unisphere. This prevents
    unauthorised settings changes by people who have access to the data file.

.. literalinclude:: code/system-settings_management.py
    :linenos:
    :language: python
    :lines: 14-39
