Bulking Information Requests using Enhanced API calls
=====================================================

Enhanced API Modules
--------------------

Unisphere for PowerMax 10.x and higher provided new functionality to make it
easier for developers to get large quantities of data quickly.  The example
below shows how to use the new enhanced API calls.

.. literalinclude:: code/enhanced_api.py
    :linenos:
    :language: python
    :lines: 14-34

Force-refreshing storage details
--------------------------------

``get_storage_object_details()`` normally omits the ``force_refresh`` query
parameter, preserving the standard Unisphere response behavior. Set
``force_refresh=True`` when the returned attributes must reflect the most
up-to-date information available:

.. literalinclude:: code/enhanced_api.py
    :language: python
    :lines: 36-39

The option works with the existing ``array_id``, ``filters``, ``select``, and
``exclude`` arguments. Keep it disabled unless a fresh server-side collection
is required.

Rate limiting
-------------

.. note::

   Unisphere permits only one ``force_refresh=true`` request per second. If
   requests are sent too frequently, the API returns HTTP 429 with a response
   such as ``{"retry_after_ms": 328}``. PyU4V propagates this through
   ``VolumeBackendAPIException`` and does not automatically sleep or retry.

Applications issuing repeated forced refreshes should catch the existing
exception, record its retry details, and wait before retrying:

.. code-block:: python

    from PyU4V.utils import exception

    try:
        fresh_volumes = conn.enhanced_api.get_storage_object_details(
            storage_object='volumes',
            select=['id', 'identifier', 'cap_gb'],
            force_refresh=True)
    except exception.VolumeBackendAPIException as error:
        # The error text retains the server's retry_after_ms response.
        print(error)
