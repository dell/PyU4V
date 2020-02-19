
Tools Guide
===========

First, make sure that PyU4V is installed_. Then visit the quick_start_
section to make sure you have secure connectivity to your array.

OpenStack
---------

**Description**

This script facilitates the seamless(live) migration of volumes from the SMIS
masking view structure to the REST masking view structure introduced in Pike.
This is only applicable if you have existing volumes created in Ocata or an
earlier release.

.. important::
   Running this script is not necessary unless you intend 'Live Migrating'
   from one compute node to another.

**Pre-requisites**

1. The OpenStack system must first be successfully upgraded to Pike or a post
   Pike release.
2. All your existing compute nodes must be online.
3. Avoid executing any cinder operations when running migrate.py python script.
4. Avoid Unisphere for PowerMax upgrades or VMAX / PowerMAX OS upgrades when
   running migrate.py python script.

**Recommendations**

1. It is recommended to create a test instance in OpenStack to force a
   creation of a masking view on the array. When you run the script it
   should move the volumes to the child storage group associated with that
   volume type. If it does not and it creates a masking view or storage
   group with a slightly different name then please file a bug on the GitHub
   issues page for this project.
2. It is also recommended to move one volume first and verify it has been
   moved to the correct storage group within the correct masking view.
3. If in any doubt, please file an issue on the GitHub issues page for this
   project issues_.

The script can be run using python 2.7, python3.6 and python 3.7. It is
recommended you run from the PyU4V base directory, however you can run from
the 'openstack' directory so long as you copy/create PyU4V.conf in that
directory.

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
   - If you find any issues, please open them on the GitHub issues page for
     this project issues_.

.. URL LINKS

.. _issues: https://github.com/MichaelMcAleer/PyU4V/issues
.. _installed: http://pyu4v.readthedocs.io/en/latest/installation.html
.. _quick_start: http://pyu4v.readthedocs.io/en/latest/quick_start.html
