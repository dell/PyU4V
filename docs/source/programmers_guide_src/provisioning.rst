Provisioning
============

A-Synchronous Provisioning & Creating Storage for a Host
--------------------------------------------------------

This example demonstrates checking an array SRP and service level to determine
if there is enough headroom to provision storage of a set size, if so, proceed
to creating a storage group with volume. Create a host, port group, and masking
view to tie all the elements together, close the session when done.

.. literalinclude:: code/provision-async_create_storage.py
    :linenos:
    :language: python
    :lines: 14-83
