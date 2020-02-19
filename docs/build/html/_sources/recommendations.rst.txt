PyU4V Usage Recommendations
===========================

In this section we aim to highlight various topics that we hope will improve
your overall experience when using PyU4V.  If you have any recommendations
that you would like to make please let us know by opening an issue_ and we will
review it for addition here.

Volume Naming Conventions
-------------------------

It is strongly recommended that you create a volume with a unique volume_name
or volume_identifier. When you search for a volume device_id based on its
volume_name, it is preferable to receive a single device id rather than a list
of device ids, of which any could be the device that you just created.

Performance Monitoring
----------------------

When using PyU4V for performance metrics collection there are a number of best
practices that you should follow:

- After enabling Unisphere for performance metrics collection allow Unisphere
  30 minutes to gather enough data before making any calls.
- The most granular time available with PyU4V performance metrics collection
  is 5 minutes, so querying for data more frequently than 5 minutes is
  a wasteful use of resources.
- If you want to ensure that your performance metric collection is querying
  the most recent performance data available set a recency window value on your
  calls.
- If the performance timestamp is not recent as of 5-10 minutes ago there is a
  strong likelihood that your instance of Unisphere has gone into catchup mode
  and is processing a backlog of performance data. It will resume normal
  operations once this backlog processing is complete and be indicated by
  performance timestamps with a window of 5-10 minutes from the current time.
- When querying a single instance of Unisphere for performance metrics across
  a number of arrays be careful on the load placed on Unisphere and try to
  determine if it is possible to query that amount of data in the given
  time frame you have set.
- If querying for data at regular intervals, examine your calls to see if you
  can create the interval time. If information is not likely to change over
  the course of 24 hours then querying once a day would be sufficient.

Lastly, and most importantly, with great power comes great responsibility,
PyU4V provides you with the ability to query every performance metric for every
performance category. Instead of gathering everything possible, be resourceful
with your calls and only query what is needed. This will provide improvements
in PyU4V performance, network load, and Unisphere REST performance. If you are
only interested in querying for KPIs, you can specify that only KPI metrics are
returned, but better still only query for a subset of metrics that you are
interested in.

.. URL LINKS

.. _issue: https://github.com/MichaelMcAleer/PyU4V/issues
