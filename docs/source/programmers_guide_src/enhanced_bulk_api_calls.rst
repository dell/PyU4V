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

Performance membership filters
------------------------------

The diagnostic performance examples in this SDK use ``in`` and ``notin``
with semicolon-separated IDs inside parentheses. Pass the whole expression
as a quoted string inside the ``filters`` list:

.. code-block:: python

    # Include these storage groups and request all metrics for the last hour.
    included = conn.performance_enhanced.get_category_metrics(
        category='StorageGroup',
        filters=['id in (SG1;SG2)', 'time_range eq 1'],
        all_metrics=True)

    # Exclude these storage groups.
    excluded = conn.performance_enhanced.get_category_metrics(
        category='StorageGroup',
        filters=['id notin (SG1;SG2)', 'time_range eq 1'])

The first call sends
``?filter=id in (SG1;SG2),time_range eq 1&metric_type=All``. Commas separate
filter clauses; semicolons separate membership values. ``metric_type`` is
a separate query parameter. Do not write ``filters=id in 'SG1;SG2'``:
Python evaluates that expression before PyU4V receives it.

``get_all_performance_metrics_for_system()`` forwards the same filters to
every discovered category, so choose IDs appropriate to the categories being
queried. Use ``get_category_metrics()`` when targeting one category.

PyU4V preserves filter expressions and does not validate operators or expand
device ranges. The supplied ``14406-10.5.0.json`` OpenAPI export defines the
diagnostic ``filter`` query parameter only as a string ("the Defined Filter
Attributes"). It does not specify membership operators, separators, or range
syntax, and it does not include the real-time endpoints. These examples
reflect the SDK's existing diagnostic documentation; the export alone cannot
confirm server acceptance. Check the documentation for the installed
Unisphere endpoint or validate with a read-only request. In particular,
real-time filter passthrough does not establish server support for ``in``
or ``notin``.

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
