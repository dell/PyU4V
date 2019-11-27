======================
Welcome to PyU4V 3.1.7
======================

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

PyU4V Version 3.1.7
-------------------

+-----------------------+----------------------------+
| **Author**            | Dell EMC                   |
+-----------------------+----------------------------+
| **PyU4V Version**     | 3.1.7                      |
+-----------------------+----------------------------+
| **Unisphere Version** | 8.4 and 9.0 series         |
+-----------------------+----------------------------+
| **Array Model**       | VMAX-3, VMAX AFA, PowerMax |
+-----------------------+----------------------------+
| **Array uCode**       | HyperMax OS, PowerMax OS   |
+-----------------------+----------------------------+
| **Platforms**         | Linux, Windows             |
+-----------------------+----------------------------+
| **Python**            | 2.7, 3.6, 3.7              |
+-----------------------+----------------------------+
| **Requires**          | Requests_, Six_, urllib3_  |
+-----------------------+----------------------------+


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
    $ pip install PyU4V==3.1.7

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


SSL Configuration
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


Initialise PyU4V Connection
---------------------------

Initialising PyU4V in your Python scripts is as simple as importing the library
and initialising the connection (assuming you have ``PyU4V.conf`` configured as
outlined in the previous section).

.. code-block:: python

    import PyU4V

    conn = PyU4V.U4VConn()
    conn.common.get_unisphere_version()
    >> {'version': 'V9.0.2'}

If you wish to query another array without changing the configuration file,
call the connection ``set_array_id()`` function:

.. code-block:: python

    conn.set_array_id('000197123456')

The various types of functionality provided by PyU4V is separated into logical
sections such as ``replication``, ``provisioning``, and ``performance``. For a
full API breakdown by section and some usage example please refer to the
PyU4V ReadTheDocs_.


Examples
--------

There are a number of examples which can be run with minimal set-up. For details on how to run these,
and other very useful information, please see Paul Martin's blog https://community.emc.com/people/PaulCork/blog


Coding conventions
------------------

For neatness and readability we will enforce the following conventions going forward.

1. Single quotes ' unless double quotes " necessary.

2. use ``.format()`` when manipulating strings

.. code-block::

   my_string= '/{variable1}, thanks for contributing to {variable2}'.format(
       variable1=’Hello’, variable2=’PyU4V’)

3. We cannot use ``.format()`` in logging due to pylint error (W1202) so we follow the following format:

.. code-block::

   my_message = 'Hello, this is my log message.'
   logger.debug('message: %(my_message)s', {my_message: my_message})

4. Use ``:returns:`` in docstring.  Pep8 will guide you with all the other docstring conventions

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

.. code-block:: bash

   # dos2unix myfile.txt

or in PyCharm:

.. code-block:: bash

   `File` -> `Line Separators` -> `LF- Unix and OS X (\n)`


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

Tools
-----

Please refer to the Tools section of ReadTheDocs_ for OpenStack functionality
to migrate volumes to the new REST masking view structure.

Disclaimer
----------

Unless required by applicable law or agreed to in writing, software distributed
under the MIT License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations under
the License.

.. BadgeLinks

.. |Maintenance| image:: https://img.shields.io/badge/Maintained-Bug_fixes_only-blue
   :target: https://github.com/MichaelMcAleer/PyU4V/commits/master
.. |OpenSource| image:: https://img.shields.io/badge/Open%20Source-Yes-blue
   :target: https://github.com/MichaelMcAleer/PyU4V
.. |AskUs| image:: https://img.shields.io/badge/Ask%20Us...-Anything-blue
   :target: https://github.com/MichaelMcAleer/PyU4V/issues
.. |License| image:: https://img.shields.io/badge/License-MIT-blue
   :target: https://github.com/MichaelMcAleer/PyU4V/blob/master/LICENSE
.. |Test| image:: https://img.shields.io/badge/Tests-Passing-blue
.. |Build| image:: https://img.shields.io/badge/Build-Passing-blue
.. |Docs| image:: https://img.shields.io/badge/Docs-Passing-blue
.. |Language| image:: https://img.shields.io/badge/Language-Python%20-blue
   :target: https://www.python.org/
.. |PyVersions| image:: https://img.shields.io/badge/Python-2.7%20%7C%203.6%20%7C%203.7-blue
   :target: https://github.com/MichaelMcAleer/PyU4V/blob/master/README.rst
.. |Platform| image:: https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-blue
   :target: https://github.com/MichaelMcAleer/PyU4V/blob/master/README.rst
.. |Unisphere| image:: https://img.shields.io/badge/Unisphere-8.4.x%20%7C%209.0.x-blue
   :target: https://www.dell.com/support/home/us/en/19/product-support/product/u
.. |DTotal| image:: https://pepy.tech/badge/pyu4v
   :target: https://pepy.tech/project/pyu4v
.. |DMonth| image:: https://pepy.tech/badge/pyu4v/month
   :target: https://pepy.tech/project/pyu4v/month
.. |DWeek| image:: https://pepy.tech/badge/pyu4v/week
   :target: https://pepy.tech/project/pyu4v/week

.. README URL Links

.. _Requests: https://realpython.com/python-requests/
.. _Six: https://six.readthedocs.io/
.. _urllib3: https://urllib3.readthedocs.io/en/latest/
.. _ReadTheDocs: https://pyu4v.readthedocs.io/en/latest/
.. _GitHub-Issues: https://github.com/MichaelMcAleer/PyU4V/issues
.. _StackOverFlow: https://stackoverflow.com/search?q=PyU4V
