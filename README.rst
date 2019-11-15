================
Welcome to PyU4V
================

NOTE

A library showing some of the functionality possible using the RestAPI of Dell EMC's Unisphere for VMAX.
See the documentation here: http://pyu4v.readthedocs.io/.
Get the Unisphere for VMAX Rest documentation by navigating to https://<ip-address>:<port-number>/univmax/restapi/docs,
where <ip-address> = the ip of your Unisphere server and <port-number> = the corresponding port to connect through,
eg: https://10.0.0.1:8443/univmax/restapi/docs.

VERSION 3

Please note that version '3.1.4' of the library is NOT BACKWARDS
COMPATIBLE with scripts written with version 2.x of PyU4V, and does not
support any Unisphere for VMAX version earlier than 8.4 - PyU4V version 2.0.2.6 is
still available on Pip, and there is a 'stable/2.0' branch available on Github.
Version 3.1.1 is now limited to security and bug fixes only. Features and
enhancements from the community will be accepted after the next major PyU4V
release.

WHAT'S SUPPORTED

This package supports Unisphere version 8.4 onwards. We support VMAX3 and
VMAX All-Flash and PowerMAX.

INSTALLATION

To give the master branch a try, clone the package using git (see the link above), and install the package using pip
(switch to the newly cloned PyU4V directory and run 'pip install .'). Copy the sample PyU4V.conf into your working
directory, and add your server and array details to the top of the PyU4V.conf configuration file, under the [setup]
heading. Alternatively, you can pass some or all of these details on initialisation.
Password, username, server_ip, port, and array MUST be set (either in the config file or on initialisation).
Verify can be left as is, or you can enable SSL verification by following the directions below
(see SSL CONFIGURATION).

SSL CONFIGURATION

1. Get the CA certificate of the Unisphere server.

    # openssl s_client -showcerts -connect {server_hostname}:8443 </dev/null 2>/dev/null|openssl x509 -outform PEM > {server_hostname}.pem

    (This pulls the CA cert file and saves it as server_hostname.pem e.g. esxi01vm01.pem)
2.	Either (a) add the certificate to a ca-certificates bundle, OR (b) add the path to the conf file:
    a. - Copy the pem file to the system certificate directory:
          .. code-block:: bash

             # cp {server_hostname}.pem /usr/share/ca-certificates/{server_hostname}.crt

       - Update CA certificate database with the following commands (Ensure the new cert file is highlighted)
          .. code-block:: bash

             # dpkg-reconfigure ca-certificates
             # update-ca-certificates

       - In the conf file ensure "verify=True" OR pass the value in on initialization

    b. In the conf file insert the following:
       verify=/{path-to-file}/{server_hostname}.pem OR pass the value in on initialization.

USAGE

PyU4V could also be used as the backend for a script, or a menu etc.
Just import the PyU4V package, create the connection to the server by instantiating an instance of U4VConn, and you're
good to go. The functions are divided up into categories - common, provisioning, replication and performance.

.. code-block:: python

    import PyU4V

    conn = PyU4V.U4VConn()
    conn.provisioning.get_host_list()
    conn.replication.find_expired_snapvx_snapshots()

If you wish to query another array without changing the configuration file, call the 'set_array_id(new_array_id)'
function, e.g.

.. code-block:: python

    conn.set_array_id('000197123456')


EXAMPLES

There are a number of examples which can be run with minimal set-up. For details on how to run these,
and other very useful information, please see Paul Martin's blog https://community.emc.com/people/PaulCork/blog

FUTURE

This is still a work in progress. To be expected in the future:
 - Expansion of the RestFunctions library
 - Improved exception handling and logging
 - Unittests
 - Tutorials

CONTRIBUTION

Please do! Create a fork of the project into your own repository. Make all your necessary changes and create a pull
request with a description on what was added or removed and details explaining the changes in lines of code.
Please run the following:

.. code-block:: bash

   # tox -e py27
   # tox -e py36
   # tox -e py37
   # tox -e pep8
   # tox -e pylint

.. note::
   If you do not have all the versions of python installed, just run tox on
   the versions you have. pep8 and pylint must run clean also.

If it all looks good, I'll merge it.  Please refer to CONVENTIONS section for more details

CONVENTIONS

For neatness and readability we will enforce the following conventions going forward.

1. Single quotes ' unless double quotes " necessary.

2. use .format() when manipulating strings

.. code-block::

   my_string= '/{variable1}, thanks for contributing to {variable2}'.format(
       variable1=’Hello’, variable2=’PyU4V’)

3. We cannot use .format() in logging due to pylint error (W1202) so we follow the following format:

.. code-block::

   my_message = 'Hello, this is my log message.'
   logger.debug('message: %(my_message)s', {my_message: my_message})

4. Use :returns: in docstring.  Pep8 will guide you with all the other docstring conventions

.. code-block::

   """The is my summary of the method with full stop.

   This is a brief description of what the method does.  Keep
   it as simple as possible.

   :param parameter1: brief description of parameter 1
   :param parameter2: brief description of parameter 2
   :returns: what gets returned from method, omit if none
   :raises: Exceptions raised, omit if none
    """

5. Class name is mixed case with no underscores _

.. code-block::

   class ClassFunctions(object):
       """Collection of functions ClassFunctions."""

6. Public Methods are separated by underscores _.  Make the name as meaningful as possible

.. code-block::

    def public_function_does_exactly_what_it_says_it_does(self):
        """Function does exactly what it says on the tin."""

7. Private Methods are prefixed and separated by underscores _.  Make the name as meaningful as possible

.. code-block::

    def _private_function_does_exactly_what_it_says_it_does(self):
        """Function does exactly what it says on the tin."""

8. If functions seems to big or too complicated then consider breaking them into smaller functions.

9. Each new function must be unit tested.

10. Each bug fix must be unit tested.

11. Unix and OS X format only.  If in doubt run

.. code-block::

   dos2unix myfile.txt

or in PyCharm:

   File -> Line Separators -> LF- Unix and OS X (\n)


SUPPORT

Please file bugs and issues on the Github issues page for this project. This is to help keep track and document
everything related to this repo. The code and documentation are released with no warranties or SLAs and are intended
to be supported through a community driven process.

OPENSTACK

Description

This script facilitates the seamless(live) migration of volumes from the SMIS
masking view structure to the REST masking view structure introduced in Pike.
This is only applicable if you have existing volumes created in Ocata or an earlier
release.

.. important::
   - Running this script is not necessary unless you intend 'Live Migrating' from one compute node to another.

Pre-requisites

1. The OpenStack system must first be successfully upgraded to Pike or a post Pike release.
2. All your existing compute nodes must be online.
3. Avoid executing any cinder operations when running migrate.py python script.
4. Avoid Unisphere for PowerMax upgrades or VMAX / PowerMAX OS upgrades when running migrate.py python script.

Recommendations

1. It is recommended to create a test instance in OpenStack to force a creation of a masking view
   on the array. When you run the script it should move the volumes to the child storage group
   associated with that volume type.  If it does not and it creates a masking view or storage
   group with a slightly different name then please file a bug on the Github issues page for this
   project.
2. It is also recommended to move one volume first and verify it has been moved to the correct
   storage group within the correct masking view.
3. If in any doubt, please file an issue on the Github issues page for this project.

The script can be run using python 2.7, python3.6 and python 3.7. It is recommended you run from
the PyU4V base directory, however you can run from the 'openstack' directory so long as you
copy/create PyU4V.conf in that directory.

.. code-block:: bash

   $ alias python3='/usr/bin/python3.7'
   $ cd $PYU4V_WORKING_DIR
   $ python3 PyU4V/tools/openstack/migrate.py

.. code-block:: bash

   $ alias python3='/usr/bin/python3.7'
   $ cp ./PyU4V.conf $PYU4V_WORKING_DIR/PyU4V/tools/openstack/.
   $ cd $PYU4V_WORKING_DIR/PyU4V/tools/openstack
   $ python3 migrate.py

.. warning::
   Python 2.7 is nearing EOL and will not be maintained past 2020

.. note::
   - Only masking views that are eligible for migrating will be presented.
   - You have the option to migrate all volume's or a subset of volumes,
     in a storage group.
   - The old masking view and storage group will remain even if all volumes
     have been migrated, so you can always move them back if in any doubt.
   - The new masking view will contain the same port group and initiator
     group as the original.
   - If you find any issues, please open them on the Github issues page for
     this project.
