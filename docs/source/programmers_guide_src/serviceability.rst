Serviceability
==============
This section gives examples of serviceability functionality for managing
PowerMax system diagnostics and configuration.

- `Serviceability Operations`_

Serviceability Operations
-------------------------
This example demonstrates retrieving local system information, querying NTP
server configuration, and downloading serviceability GRAB log files for
diagnostics.

.. warning::
    The ``download_grab_files`` operation can take a significant amount of time
    depending on the size of the logs. Set an appropriate timeout value.

.. literalinclude:: code/serviceability-operations.py
    :linenos:
    :language: python
    :lines: 15-37
