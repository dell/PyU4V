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

Please note that version '3.1.2' of the library is NOT BACKWARDS
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
everything related to this repo. For general discussions and further support you can join the {code} Community
slack channel. Lastly, for questions asked on Stackoverflow.com, please tag them with Dell or Dell EMC. The code and
documentation are released with no warranties or SLAs and are intended to be supported through a community driven
process.
