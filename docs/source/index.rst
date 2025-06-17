..  toctree::
    :maxdepth: 2
    :hidden:

    installation
    configuration
    quick_start
    recommendations
    contribute
    support
    programmers_guide
    tools
    api
    genindex

Welcome to PyU4V's documentation!
=================================

Overview
--------

PyU4V is a Python module that simplifies interaction with the Unisphere for
PowerMax REST API.  It wraps REST calls with simple APIs that abstract the HTTP
request and response handling.

.. note::
   All official documentation for Unipshere for PowerMax API
   is available at https://developer.dell.com/apis/4458. An OpenApi.json file
   can be download from this site for use with tools like PostMan or for
   interfacing with PyU4V custom API call mechanism.  Please refer to this
   documentation when looking for information about query path parameters
   for functions that accept them.

Supported PyU4V Versions
------------------------

+-------------------------------+----------------------------------------+
| **PyU4V Version**             | 10.2.0.3                               |
+-------------------------------+----------------------------------------+
| **Minimum Unisphere Version*  | 10.2.0                                 |
+-------------------------------+----------------------------------------+
| **Array Model**               | VMAX-3, VMAX AFA, PowerMax             |
+-------------------------------+----------------------------------------+
| **Array uCode**               | HyperMax OS, PowerMax OS               |
+-------------------------------+----------------------------------------+
| **Platforms**                 | Linux, Windows                         |
+-------------------------------+----------------------------------------+
| **Python**                    | 3.6, 3.7, 3.8, 3.9, 3.10               |
+-------------------------------+----------------------------------------+
| **Requirements**              | Requests_, Six_, urllib3_,             |
|                               | prettytable_                           |
+-------------------------------+----------------------------------------+
| **Test Requirements**         | TestTools_, Tox_                       |
+-------------------------------+----------------------------------------+


.. note::
    PyU4V officially supports Python 3.6, 3.7, 3.8, 3.9 & 3.10 Python 2.x support
    has been dropped since January 1st 2020.

.. note::
    PyU4V version 10.2.0.3 is compatible with scripts written for PyU4V versions
    >= 9.2. Please ensure to check change log to ensure that you are not
    using functions that have been marked as depreciated.

Getting Started
---------------

:doc:`installation`
    How to get the source code, and how to build or install the python package.

:doc:`configuration`
    Configuring PyU4V for your environment.

:doc:`quick_start`
    Making your first calls with PyU4V.

:doc:`contribute`
    Contribute to the PyU4V project.

:doc:`support`
    How to get support with or open issues for PyU4V.

:doc:`programmers_guide`
    A range of examples demonstrating various PyU4V module usage.

:doc:`tools`
  The tools guide for PyU4V

:doc:`api`
    A glossary of all available functions.

Build your own PyU4V Docs
-------------------------

PyU4V docs have been built using Sphinx and included with the source PyU4V
package, however if you would like to build the docs from scratch use the
following commands::

   $ pip install sphinx
   $ pip install sphinx-rtd-theme
   $ cd PyU4V/docs
   $ make clean && make html

All of the necessary make files and sphinx configuration files are included
with PyU4V so you can build the docs after the required dependencies have been
installed.

Once the above commands have been run you will find newly generated html files
within the ``/PyU4V/docs/build`` folder. Open ``index.html`` within a
browser of your choosing to view the docs offline. Generating the docs is not
required, we have bundled the most up-to-date docs with PyU4V so you can still
navigate to ``/PyU4V/docs/build/index.html`` within your browser to view
PyU4V docs offline.

Disclaimer
----------

PyU4V 10.2 is distributed under the Apache 2.0 License. Unless required by
applicable law or agreed to in writing, software distributed under the Apache
2.0 License is distributed on an **"as is" basis, without warranties or**
**conditions of any kind**, either express or implied. See the License for the
specific language governing permissions and limitations under the License.

.. URL LINKS

.. _Requests: https://realpython.com/python-requests/
.. _Six: https://six.readthedocs.io/
.. _urllib3: https://urllib3.readthedocs.io/en/latest/
.. _retired: https://pythonclock.org/
.. _TestTools: https://pypi.org/project/testtools/
.. _Tox: https://pypi.org/project/tox/
.. _prettytable: https://pypi.org/project/PrettyTable/
