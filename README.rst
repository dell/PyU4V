Welcome to PyU4V 10.5
=====================

| |Maintenance| |OpenSource| |AskUs| |License| |Test| |Build| |Docs|
| |Language| |PyVersions| |Unisphere| |Platform| |DTotal| |DMonth| |DWeek|

Overview
--------

PyU4V is a Python module that simplifies interaction with the Unisphere for
PowerMax REST API.  It wraps REST calls with simple APIs that abstract the HTTP
request and response handling.

Full documentation and user guides can be found in PyU4V's ReadTheDocs_.

Note
   You can get the Unisphere for PowerMax REST documentation by
   navigating to a URL in your local instance of Unisphere for PowerMax.
   Navigate to ``https://{ip-address}:{port}/univmax/restapi/docs``
   where ``{ip-address}`` is the IP address of your Unisphere server and
   ``{port}`` is the port it is listening on.

PyU4V Version 10.5
------------------

+-------------------------------+----------------------------+
| **Author**                    | Dell EMC                   |
+-------------------------------+----------------------------+
| **PyU4V Version**             | 10.5.0.1                   |
+-------------------------------+----------------------------+
| **Minimum Unisphere Version** | 10.5.0                     |
+-------------------------------+----------------------------+
| **Array Model**               | VMAX-3, VMAX AFA, PowerMax |
+-------------------------------+----------------------------+
| **Array uCode**               | HyperMax OS, PowerMax OS   |
+-------------------------------+----------------------------+
| **Platforms**                 | Linux, Windows             |
+-------------------------------+----------------------------+
| **Python**                    | 3.9 - 3.13                 |
+-------------------------------+----------------------------+
| **Requires**                  | Requests_, urllib3_       |
+-------------------------------+----------------------------+

Note
    If you want to continue to use Unisphere 8.4.x or 9.0.x with PyU4V you will
    need to remain on PyU4V 3.1.x. There is no support for PyU4V 9.x with any
    version of Unisphere older than 9.1.x

Note
    PyU4V version 10.5 is compatible with scripts written for PyU4V versions
    >= 9.2. Please ensure to check change log to ensure that you are not
    using functions that have been marked as depreciated.

Installation
------------

Note
    A full installation guide can be found in PyU4V's ReadTheDocs_ which
    includes additional configuration options around PyU4V logging.

PyU4V can be installed from source, via ``pip``, or run directly from the
source directory. To clone PyU4V from source use ``git``::

    $ git clone https://github.com/dell/PyU4V

To install from source navigate into the new ``PyU4V`` directory and use
``pip``::

    $ cd PyU4V/
    $ pip install .

Installing via ``pip`` without cloning from source can be achieved by
specifying ``PyU4V`` as the install package for ``pip``::

    $ pip install PyU4V
    # Install a specific version
    $ pip install PyU4V==10.4

Copy the sample ``PyU4V.conf`` provided with PyU4V to either your working
directory or within a directory named ``.PyU4V`` in your current users home
directory. The ``.sample`` suffix has to be removed for the configuration file
to become valid for loading by PyU4V::

    $ mkdir ~/.PyU4V
    $ cp PyU4V/PyU4V.conf.sample ~/.PyU4V/PyU4V.conf

Note
    If ``PyU4V.conf`` is present in both the current working directory and the
    current user's home directory, the version of ``PyU4V.conf`` in the current
    working directory will take precedence.

Edit PyU4V configuration settings in ``PyU4V.conf`` under the ``[setup]``
heading, these setting will need to reflect your environment configuration::

    [setup]
    username=pyu4v-user
    password=secret-pass
    server_ip=10.0.0.75
    port=8443
    array=00012345678
    verify=/path-to-file/server_hostname.pem

Alternatively, you can pass some or all of these details on initialisation.
Environment configuration values ``password``, ``username``, ``server_ip``,
``port``, and ``array`` **must** be set either in the config file or on
initialisation. SSL verification as indicated by the ``verify`` key in
``PyU4V.conf`` is discussed in the next section.

SSL CONFIGURATION
-----------------

In order to enable SSL enabled communication between your host and the
Unisphere server there are some additional steps required. First you must
extract the CA certificate from Unisphere then either add it to the system
certificate bundle or specify the path to the cert in ``PyU4V.conf``. We will
demonstrate both approaches here.

Get the CA certificate of the Unisphere server::

    $ openssl s_client -showcerts -connect {server_hostname}:8443 \
    </dev/null 2>/dev/null|openssl x509 -outform PEM > {cert_name}.pem

    # Example
    $ openssl s_client -showcerts -connect 10.0.0.75:8443 \
    </dev/null 2>/dev/null|openssl x509 -outform PEM > unisphere91.pem

Where ``{server_host_ip}`` is the hostname or IP address of your Unisphere
server and ``{cert_name}`` is the name for your CA cert. This pulls the CA cert
file from the instance of Unisphere at ``10.0.0.75:8443`` and saves it as a
``.pem`` file.

To add the cert to a CA certificate bundle, copy the ``.pem`` file to the
system certificate directory and update the CA certificate database::

    # cp {cert_name}.pem /usr/share/ca-certificates/{cert_name}.crt
    # dpkg-reconfigure ca-certificates
    # update-ca-certificates

Once the above steps are complete you will need to specify ``verify=True`` in
``PyU4V.conf`` for PyU4V to load the required Unisphere CA cert from the system
certificate bundle::

    [setup]
    verify=True

Alternatively you can skip adding the certificate to a certificate bundle and
pass it directly on PyU4V initialisation or specify the path to the certificate
directly in ``PyU4V.conf``::

    [setup]
    verify=/path/to/file/{cert_name}.pem

API Version Configuration
-------------------------

PyU4V uses the latest Unisphere API version by default for the current release.
If you need to connect to an older Unisphere server that does not support the
latest API version, you can specify a custom API version using the ``u4v_version``
parameter.

This is useful for backward compatibility when using PyU4V with older Unisphere
versions. The specified version will be validated against the server's supported
API versions on connection.

Configure in ``PyU4V.conf``:

.. code-block:: ini

    [setup]
    u4v_version=100

Or pass it on initialisation:

.. code-block:: python

    import PyU4V

    # Connect using API version 100 (Unisphere 10.0)
    conn = PyU4V.U4VConn(u4v_version='100')

    # Or dynamically update the version
    conn.set_u4v_version('101')

Note
    The ``u4v_version`` parameter accepts string values like ``'100'``, ``'101'``,
    ``'104'``, etc. These correspond to the Unisphere API version numbers. If the
    specified version is not supported by the server, PyU4V will exit with an error
    listing the supported versions.

Skipping the Version Check
--------------------------

If you need maximum flexibility - for example to talk to a Unisphere server
whose version is below the SDK minimum, or to force a specific ``u4v_version``
that the server does not advertise as supported - set ``skip_version_check``.
When enabled, PyU4V logs a warning instead of exiting, and API calls use the
supplied ``u4v_version`` if set, otherwise the packaged default for the
release. Requests that are unsupported at the resolved version simply return
the server's error (for example a 404), which your code can handle.

Configure in ``PyU4V.conf``:

.. code-block:: ini

    [setup]
    skip_version_check=True

Or pass it on initialisation:

.. code-block:: python

    import PyU4V

    # Force API version 92 without failing the version check
    conn = PyU4V.U4VConn(u4v_version='92', skip_version_check=True)

Note
    ``skip_version_check`` defaults to ``False``, preserving the existing
    strict validation behaviour. Enable it only if you are prepared to handle
    unsupported-endpoint errors in your own code.

Note
    As of 10.5 the active API version is held in a single place (the shared REST
    client) and exposed live via ``conn.common.UNI_VERSION``. Calling
    ``conn.set_u4v_version('101')`` updates every feature module
    (``conn.snapshot``, ``conn.srdf``, ``conn.provisioning``, etc.) at once — no
    per-module update is required. ``conn.common.UNI_VERSION`` remains both
    readable and writable, but a write now applies globally to the connection.

OpenTelemetry Metrics Export
----------------------------

PyU4V 10.5 can manage the Unisphere OpenTelemetry collector endpoint through
``conn.system``. The public API includes endpoint registration, inspection,
update, and deletion, together with per-array metrics-export registration::

    conn.system.register_otel_endpoint(
        address='otel-collector.example.com', port=4317,
        protocol='gRPC', enable_compression=True)
    conn.system.update_otel_registration(registration_details=[
        {'system_id': conn.array_id, 'export_metrics': True}
    ])

Use ``get_otel_endpoint_settings()`` and ``get_otel_registration()`` to inspect
the current configuration. See the System section of the programmers guide for
the complete update and cleanup workflow.

Initialise PyU4V Connection
---------------------------

Initialising PyU4V in your Python scripts is as simple as importing the library
and initialising the connection (assuming you have ``PyU4V.conf`` configured as
outlined in the previous section).

.. code-block:: python

    import PyU4V

    conn = PyU4V.U4VConn()
    conn.common.get_unisphere_version()
    >> {'version': '10.4.0.0'}

If you wish to query another array without changing the configuration file,
call the connection ``set_array_id()`` function:

.. code-block:: python

    conn.set_array_id('000197123456')

The various types of functionality provided by PyU4V is separated into logical
sections such as ``replication``, ``provisioning``, and ``performance``. For a
full API breakdown by section and some usage example please refer to the
PyU4V ReadTheDocs_.

Version 10.5 Changes Summary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Enhanced API force refresh**: ``get_storage_object_details()`` accepts a new
  ``force_refresh`` keyword argument (default ``False``). When ``True``, Unisphere
  refreshes the requested information before returning it. The API permits one
  force-refresh request per second; HTTP 429 responses include ``retry_after_ms``
  and propagate through the existing backend exception without automatic retry.
- **``get_category_metrics`` enhanced**: new ``all_metrics`` keyword argument (default
  ``False``). When ``True``, appends the ``metric_type=All`` query parameter so all
  available metrics are returned instead of KPI metrics only. Fully backward-compatible
  — existing call-sites require no changes.
- **Expired SnapVX discovery**: Scans replication storage groups without the
  ``hasSnapshots`` filter to support arrays that reject that filter with HTTP
  500. Groups without snapshots are skipped; discovery can make more requests.
- **New modules**: ``PyU4V.snapshot`` (``SnapshotFunctions``) and ``PyU4V.srdf``
  (``SRDFFunctions``) split from ``replication.py``. Access via ``conn.snapshot``
  and ``conn.srdf`` respectively.
- **Backward compatibility**: All existing ``conn.replication.*`` calls continue to work
  via thin delegation wrappers decorated with ``@refactoring_notice``.
- **New CI test files**: ``test_pyu4v_ci_snapshot.py`` (``CITestSnapshot``) and
  ``test_pyu4v_ci_srdf.py`` (``CITestSRDF``) added to ``PyU4V/tests/ci_tests/``.
  These test ``conn.snapshot`` and ``conn.srdf`` directly.
- **Legacy CI tests**: ``CITestReplication`` in ``test_pyu4v_ci_replication.py`` is
  retained for regression; snapshot/SRDF methods marked deprecated pointing to new files.
- **Post-split fixes**: ``set_array_id()`` now reaches the snapshot/SRDF instances used by
  the deprecated ``conn.replication.*`` calls (shared single instances); deprecation
  decorators preserve docstrings/signatures via ``functools.wraps``; and
  ``ReplicationFunctions.version`` now reflects the live ``common.UNI_VERSION``.

Support, Bugs, Issues
---------------------

Please file support requests, bugs, and issues on the PyU4V GitHub-Issues_
page for this project. For further information on opening an issue and
recommended issue templates please see the PyU4V ReadTheDocs_.

For questions asked on StackOverFlow_, please tag them with ``Dell``,
``Dell EMC``, ``PowerMax``, and ``PyU4V`` to maximise the chances of the
correct community members assisting.

Contributing
------------

PyU4V is built to be used openly by everyone, and in doing so we encourage
everyone to submit anything they may deem to be an improvement, addition, bug
fix, or other change which may benefit other users of PyU4V.

There are some requirements when submitting for PyU4V, such as coding
standards, building unit tests and continuous integration tests, and going
through a formal code review process, however anyone familiar with open source
development will be familiar with this process.  There are a number of core
PyU4V reviewers and once a submission has approvals from two or more core
reviewers and all tests are running cleanly then the request will be merged
with the upstream PyU4V repo.

For a full breakdown of contribution requirements, coding standards, submitting
and everything else in between please refer to PyU4V ReadTheDocs_.

Disclaimer
----------

Unless required by applicable law or agreed to in writing, software distributed
under the Apache 2.0 License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations under
the License.

.. BadgeLinks

.. |Maintenance| image:: https://img.shields.io/badge/Maintained-Yes-blue
   :target: https://github.com/dell/PyU4V/commits/master
.. |OpenSource| image:: https://img.shields.io/badge/Open%20Source-Yes-blue
   :target: https://github.com/dell/PyU4V
.. |AskUs| image:: https://img.shields.io/badge/Ask%20Us...-Anything-blue
   :target: https://github.com/dell/PyU4V/issues
.. |License| image:: https://img.shields.io/badge/License-Apache%202.0-blue
   :target: https://github.com/dell/PyU4V/blob/master/LICENSE
.. |Test| image:: https://img.shields.io/badge/Tests-Passing-blue
.. |Build| image:: https://img.shields.io/badge/Build-Passing-blue
.. |Docs| image:: https://img.shields.io/badge/Docs-Passing-blue
.. |Language| image:: https://img.shields.io/badge/Language-Python%20-blue
   :target: https://www.python.org/
.. |PyVersions| image:: https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue
   :target: https://github.com/dell/PyU4V/blob/master/README.rst
.. |Platform| image:: https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-blue
   :target: https://github.com/dell/PyU4V/blob/master/README.rst
.. |Unisphere| image:: https://img.shields.io/badge/Unisphere-10.0-blue
   :target: https://www.dell.com/support/home/us/en/19/product-support/product/unisphere-powermax/overview
.. |DTotal| image:: https://pepy.tech/badge/pyu4v
   :target: https://pepy.tech/project/pyu4v
.. |DMonth| image:: https://pepy.tech/badge/pyu4v/month
   :target: https://pepy.tech/project/pyu4v/month
.. |DWeek| image:: https://pepy.tech/badge/pyu4v/week
   :target: https://pepy.tech/project/pyu4v/week

.. README URL Links

.. _Requests: https://realpython.com/python-requests/
.. _urllib3: https://urllib3.readthedocs.io/en/latest/
.. _ReadTheDocs: https://pyu4v.readthedocs.io/en/latest/
.. _GitHub-Issues: https://github.com/dell/PyU4V/issues
.. _StackOverFlow: https://stackoverflow.com/search?q=PyU4V
