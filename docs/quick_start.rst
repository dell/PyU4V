
Quick Start Guide
=================

First, make sure that PyU4V is `installed <http://pyu4v.readthedocs.io/en/latest/installation.html>`_.

Let's get started with some simple examples.

Begin by importing the PyU4V package, and creating a connection to the Unisphere server by instantiating an instance of
U4VConn. For now, we will pass in our login credentials on instantiation, but you can also create a configuration file
(see `The Configuration File - PyU4V.conf`_, below. Also see  `Configuring SSL`_ below to get more information on the
'verify' parameter)


.. code-block:: python

    >>> import PyU4V

    >>> conn = PyU4V.U4VConn(username='my_name', password='password', server_ip='10.0.0.1', port='8443', verify=True)

Now we have a connection to the Unisphere server. Next, we must select an array for our queries.
First, let's see what arrays we have in our environment:

.. code-block:: python

    >>> conn.common.get_array_list()
    ["000194900123", "000195900123", "000196900123", "000197900123", "000197900123"]

Let's pick one of these and set it as our array of choice:

.. code-block:: python

    >>> conn.set_array_id('000194900123')

If you wish to query another array without creating a new connection, this function can be called whenever required.
The array_id can also be set on initialisation (PyU4V.U4VConn(array_id='000197123456')), or by putting it in the conf
file.

Now we are ready to start making some calls!
The functions are divided up into categories - common, provisioning, replication, and performance.

- Common covers a few utils and also covers system calls
- Provisioning covers all things provisioning and masking related, and corresponds with the 'sloprovisioning' endpoints
- Replication covers local and remote replication
- Performance covers all the performance related calls.

.. code-block:: python

    >>> conn.provisioning.get_host_list()
    ['host1', 'host2', 'host3']
    >>> conn.replication.find_expired_snapvx_snapshots()
    [{'storagegroup_name': 'my-storagegroup1', 'snapshot_name': 'my-temporary-snap', 'generation_number': '0',
      'expiration_time': '14:46:24 Wed, 24 Jan 2018', 'linked_sg_name': 'my-linked-sg',
      'snap_creation_time': '14:46:24 Wed, 23 Jan 2018'}]


The Configuration File - PyU4V.conf
-----------------------------------

Instead of passing the Unisphere server details in on initialisation, there is also the option to put them in a
configuration file, 'PyU4V.conf'. This file also provides the option to setup logging in whatever way suits your
project (please see `here for further information on logging configuration <https://docs.python.org/2/library/logging.config.html#logging-config-fileformat>`_).
The configuration file should be placed in your working directory, or it can be placed in '~/.PyU4V/'.
A local PyU4V file (i.e. in the current working directory) will override a conf file in '~/.PyU4V/'. Please see
`PyU4V.conf.example <https://github.com/ciarams87/PyU4V/blob/master/PyU4V.conf.example>`_ for an example conf file.

Please note that parameters passed in on initialisation will override
those set in any configuration file, i.e. the priority goes

- First, parameters set on initialisation are selected,
- If any of these are unset, next any parameters set in a PyU4V.conf will be used,
- The local PyU4V.conf will be selected first, and if that cannot be found, a global file will be selected

Configuring SSL
---------------

We STRONGLY recommend that you configure the library to verify SSL. If not, you leave yourself open to MITM attacks
and other potential security issues. However, you can disable SSL verification by setting 'verify=False' on
initialisation, or in the configuration file.

To set:

1. Get the CA certificate of the Unisphere server.

   .. code-block:: bash

        # openssl s_client -showcerts -connect {server_hostname}:8443 </dev/null 2>/dev/null|openssl x509 -outform PEM > {server_hostname}.pem

(This pulls the CA cert file and saves it as server_hostname.pem e.g. esxi01vm01.pem)

2.	Either add the certificate to a ca-certificates bundle, OR add the path to the conf file/ pass it in as a parameter
on initialisation:

    * - Copy the pem file to the system certificate directory:
          .. code-block:: bash

             # cp {server_hostname}.pem /usr/share/ca-certificates/{server_hostname}.crt

       - Update CA certificate database with the following commands (Ensure the new cert file is highlighted)
          .. code-block:: bash

             # dpkg-reconfigure ca-certificates
             # update-ca-certificates

       - If the conf file is being used, ensure that if the 'verify' tag is present, that it is set to True
         ("verify=True") (If it is not set anywhere, 'verify' defaults to True)

OR

    * In the conf file insert the following:
       verify=/{path-to-file}/{server_hostname}.pem OR pass the value in on initialization.

Recommendations
---------------

It is strongly recommended that you create a volume with a unique volume_name or volume_identifier.
When you search for a volume device_id based on it's volume_name, it is preferable to receive a single
device id rather than a list of device ids, of which any could be the device that you just created.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
