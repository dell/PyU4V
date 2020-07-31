Configuration
=============

Once PyU4V is installed the next step is to configure it through
``PyU4V.conf.`` There is a sample version of ``PyU4V.conf`` provided in PyU4V
which has default configuration options for logging but will require
environment configuration setting changes for PyU4V to work.

Copy the sample ``PyU4V.conf`` provided with PyU4V to either your working
directory or within a directory named ``.PyU4V`` in your current users home
directory. The ``.sample`` suffix has to be removed for the configuration file
to become valid for loading by PyU4V:

.. code-block:: bash

    $ mkdir ~/.PyU4V
    $ cp PyU4V/PyU4V.conf.sample ~/.PyU4V/PyU4V.conf

.. note::
    The ``\~`` symbol is used here to represent the users home directory
    regardless of operating system, however, ``\~`` is not a valid shortcut in
    Windows command prompt so direct path to users home directory should be
    used instead ``C:\> mkdir C:\Users\{user}\.PyU4V`` where ``{user}`` is the
    current user.

.. note::
    If ``PyU4V.conf`` is present in both the current working directory and the
    current user's home directory, the version of ``PyU4V.conf`` in the current
    working directory will take precedence. See the section below on PyU4V
    settings precedence.

Edit PyU4V configuration settings in ``PyU4V.conf`` under the ``[setup]``
heading, these setting will need to reflect your environment configuration:

.. code-block:: bash

    [setup]
    username=pyu4v-user
    password=secret-pass
    server_ip=10.0.0.75
    port=8443
    array=00012345678
    verify=/path-to-file/server_hostname.pem

Where...

+---------------+-------------------------------------------------------------+
| **Key**       | **Description**                                             |
+---------------+-------------------------------------------------------------+
| ``username``  | Unisphere REST login username                               |
+---------------+-------------------------------------------------------------+
| ``password``  | Unisphere REST login password                               |
+---------------+-------------------------------------------------------------+
| ``server_ip`` | Unisphere server IP address                                 |
+---------------+-------------------------------------------------------------+
| ``port``      | Unisphere server port number                                |
+---------------+-------------------------------------------------------------+
| ``array``     | 12 digit array serial number                                |
+---------------+-------------------------------------------------------------+
| ``verify``    || ``True`` - Load SSL cert from CA certificate bundle        |
|               || ``/path/to/file`` - Load SSL cert from file location       |
|               || ``False`` - Disable SSL verification                       |
+---------------+-------------------------------------------------------------+

Alternative PyU4V.conf Load Using U4VConn().file_path
-----------------------------------------------------

It is also possible to override ``PyU4V.conf`` in both the working directory
and home directory by specifying
``univmax_conn.file_path='/path/to/PyU4V.conf'`` before initialising PyU4V.

.. code-block:: Python

    import PyU4V

    PyU4V.univmax_conn.file_path = '~/path/to/PyU4V.conf'
    # Instantiate U4VConn() using the PyU4V config file specified in file_path
    conn = U4VConn()

If you specify a ``file_path`` whilst having a copy of ``PyU4V.conf`` in both
your working directory and home directory in ``~/.PyU4V``, the instance of
``PyU4V.conf`` as specified in ``file_path`` will take precedence. See the
section below on PyU4V settings precedence.

Passing Environment Configuration to U4VConn() on Initialisation
----------------------------------------------------------------

Instead of specifying PyU4V configuration options within ``PyU4V.conf`` it is
possible to pass these values directly to ``U4VConn()`` on initialisation. The
key/values expected are the same as those specified in ``PyU4V.conf``.

.. code-block:: Python

    >>> import PyU4V
    >>> conn = U4VConn(
            username='pyu4v-user', password='secret-pass',
            server_ip='10.0.0.75', port='8443', verify=True,
            array_id='00012345678')
    >>> conn.common.get_unisphere_version()
    {'version': 'V9.1.0.5'}

If you pass configuration into ``U4VConn()`` directly in the code, these
settings will override any that are defined in ``PyU4V.conf`` at any location.

PyU4V Configuration Loading Precedence
--------------------------------------

There are a number of ways to initialise PyU4V with your environment settings
through ``PyU4V.conf`` or passing the values directly. These various methods of
setting PyU4V environment configuration have a load precedence, these are
listed in order with number 1 being the first load precedent:

1. Configuration key/values passed directly to ``U4VConn()``
2. ``PyU4V.conf`` as specified in ``univmax_conn.file_path``
3. ``PyU4V.conf`` in current working directory
4. ``PyU4V.conf`` in current users home directory
5. If none of the above or missing mandatory options raise
   ``MissingConfigurationException``

PyU4V Logger Configuration
--------------------------

Logger options in PyU4V have been streamlined since the previous 3.1.x version,
all options are now consolidated to save on duplicate options being presented.
All logger configuration options in PyU4V.conf can be found under the comment
``; log configuration`` in the sections ``[loggers*]``, ``[handlers*]``, and
``[formatters*]``. There are a number of configuration options which you can
change to suit your needs, the most relevant of those for the installation
and configuration process are outlined in the table below.

+--------------------------------+------------------------------------+----------------------------------+
| **Section**                    | **Config Option**                  | **Description**                  |
+--------------------------------+------------------------------------+----------------------------------+
| ``[logger_PyU4V]``             | ``level=INFO``                     | | Sets the PyU4V log level, this |
|                                |                                    | | defaults to INFO but can be    |
|                                |                                    | | changed to any logger LOG level|
+--------------------------------+------------------------------------+----------------------------------+
| ``[handler_consoleHandler]``   | ``args=(sys.stdout,)``             | | Control how log messages are   |
|                                |                                    | | output to console              |
+--------------------------------+------------------------------------+----------------------------------+
| ``[handler_fileHandler]``      | | ``args=('PyU4V.log', 'a',``      | | Control how log messages are   |
|                                | | ``10485760, 10)``                | | written to log files and where |
|                                |                                    | | the log file is located        |
+--------------------------------+------------------------------------+----------------------------------+
| ``[formatter_simpleFormatter]``| | ``format=%(asctime)s - %(name)s``| | Set the format for the log     |
|                                | | ``- %(levelname)s - %(message)s``| | prefix output in PyU4V.log     |
+--------------------------------+------------------------------------+----------------------------------+

.. note::
    PyU4V log functionality is run on top of Python's great inbuilt logger. If
    you require in depth descriptions of the PyU4V logger configuration
    options, the logger sections, or input arguments for the handlers, please
    see the official Python Logger documentation here_.

.. URL LINKS

.. _here: https://docs.python.org/3.7/howto/logging.html