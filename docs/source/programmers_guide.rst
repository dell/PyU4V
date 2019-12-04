Programmers Guide
=================

In this section a number of examples demonstrating various PyU4V functionality
are provided. If you have an example which you believe would make a good
addition here let us know be opening a support issue and we will review it for
addition!

Although the scope of these programmers examples is limited, it is worth
pointing out that if you want to see a working example of any function
you can do so by looking at that function's associated continuous integration
test.

.. note::
    In the first two examples print statements will be included to show how
    responses from REST requests for newly created assets can be used for
    further operations, in all later examples print statements will not be
    included for succinctness.

First connection to PyU4V
-------------------------

In this basic example we initialise a connection with Unisphere, retrieving
version and array information, and finishing by closing the REST session.

.. code-block:: Python

    """examples/unisphere_connect.py."""

    import PyU4V

    # Initialise PyU4V connection to Unisphere
    conn = PyU4V.U4VConn(
        u4v_version='90', server_ip='10.0.0.75', port=8443,
        verify='~/.PyU4V/Unisphere91.pem', username='pyu4v-user',
        password='secret-pass')

    # Get the Unisphere version
    version = conn.common.get_uni_version()

    # Retrieve a list of arrays managed by your instance of Unisphere
    array_list = conn.common.get_array_list()

    # Output results to screen
    print('Congratulations on your first connection to Unisphere, your '
          'version is: {ver}'.format(ver=version[0]))
    print('This instance of Unisphere instance manages the following arrays: '
          '{arr_list}'.format(arr_list=array_list))

    # GET those arrays which are local to this instance of Unisphere
    local_array_list = list()
    for array_id in array_list:
        array_details = conn.common.get_array(array_id)
        if array_details['local']:
            local_array_list.append(array_id)

    # Output results to screen
    print('The following arrays are local to this Unisphere instance: '
          '{arr_list}'.format(arr_list=local_array_list))

    # Close the session
    conn.close_session()


A-Synchronous Provisioning & Creating Storage for a Host
--------------------------------------------------------

This example demonstrates checking an array SRP and service level to determine
if there is enough headroom to provision storage of a set size, if so, proceed
to creating a storage group with volume. Create a host, port group, and masking
view to tie all the elements together, close the session when done.

.. code-block:: Python

    """examples/async_provision.py"""

    import PyU4V

    # Initialise PyU4V connection to Unisphere
    conn = PyU4V.U4VConn(
        u4v_version='90', server_ip='10.0.0.75', port=8443,
        verify='~/.PyU4V/Unisphere91.pem', username='pyu4v-user',
        password='secret-pass')

    # Before provisioning storage we are going to check that there is enough
    # headroom left on the array for our provisioning operations
    REQUESTED_CAPACITY = 10

    # Get the available headroom for the SRP and service level required
    headroom_info = conn.wlp.get_headroom(array_id=conn.array_id,
                                          srp='SRP_1', slo='Diamond')

    # Extract the capacity value from the headroom_info REST response
    headroom_capacity = headroom_info[
        'OLTP'][0]['headroom'][0]['headroomCapacity']

    # If the requested capacity of 10GB is less than or equal to the available
    # capacity proceed with the provisioning operations
    if REQUESTED_CAPACITY <= int(headroom_capacity):
        # Create a non-empty storage group using asynchronous request - we can
        # wait until the job completes or proceed with operations and check
        # back at a later time
        storage_group_async_job = (
            conn.provisioning.create_non_empty_storage_group(
                srp_id='SRP_1', storage_group_id='example-sg',
                service_level='Diamond', num_vols=1,
                vol_size=REQUESTED_CAPACITY, cap_unit='GB', _async=True))

        # We will wait this time on the results of the storage group create
        # request
        conn.common.wait_for_job(operation='Create SG with volume',
                                 job=storage_group_async_job)
        print('Storage Group created successfully...')

        # Get information on our new storage group
        storage_group_info = conn.provisioning.get_storage_group(
            storage_group_name='Example-SG')
        print('Storage Group details: {details}'.format(
                details=storage_group_info))

        # Create a Host using supplied initiator IDs, these can be also be
        # retrieved via the call conn.provisioning.get_available_initiator()
        initiator_list = ['iqn:2019-test1', 'iqn:2019-test1']
        host_info = conn.provisioning.create_host(
            host_name='Example-Host', initiator_list=initiator_list)
        print('Host created successfully...')
        print('New Host details: {details}'.format(details=host_info))

        # Create a Port Group using supplied ports, these could be also be
        # retrieved via the call conn.provisioning.get_port_list()
        port_group_info = conn.provisioning.create_port_group(
            port_group_id='Example-PG', director_id='SE-01', port_id='1')
        print('Port Group created successfully...')
        print('Port Group details: {details}'.format(details=port_group_info))

        # Create a Masking View and tie all the elements we have created
        # together
        masking_view_info = (
            conn.provisioning.create_masking_view_existing_components(
                port_group_name='Example-PG', masking_view_name='Example-MV',
                storage_group_name='Example-SG', host_name='Example-Host'))
        print('Masking View created...')
        print('Masking View details: {details}'.format(
            details=masking_view_info))

    # Close the session
    conn.close_session()



Local Replication with SnapVX
-----------------------------

In this example a new storage group is created with a single 1GB volume. A
snapshot name is generated using the current time so it can be easily
identified, and the storage group snapshot is created. The operation is
verified by querying for a list of snapshots for a given storage group and
confirming the snapshot we created is present in that list.

.. code-block:: Python

    """examples/create_snapshot.py"""

    import PyU4V
    import time

    # Initialise PyU4V connection to Unisphere
    conn = PyU4V.U4VConn()

    # Create storage Group with one volume using settings specified for
    # service level and capacity
    storage_group = conn.provisioning.create_non_empty_storage_group(
        srp_id='SRP_1', storage_group_id='PyU4V_SG', service_level='Diamond',
        workload=None, num_vols=1, vol_size=1, cap_unit='GB')

    # Define a Name for the Snapshot, in this case the name auto appends
    # the host
    # time for when it was taken for ease of identification
    snap_name = 'PyU4V_Snap_' + time.strftime('%d%m%Y%H%M%S')

    # Create the snapshot of the storage group containing the volume and
    # storage group created in the previous step
    snapshot = conn.replication.create_storage_group_snapshot(
        storage_group_id=storage_group['storageGroupId'], snap_name=snap_name)

    # Confirm the snapshot was created successfully, get a list of storage
    # group snapshots
    snap_list = conn.replication.get_storage_group_snapshot_list(
        storage_group_id=storage_group['storageGroupId'])

    # Assert the snapshot name is in the list of storage group snapshots
    assert snapshot['name'] in snap_list

    # Close the session
    conn.close_session()


This example will create a storage group with a volume, create a snapshot
of that storage group and link the snapshot to a new storage group. This is a
typical workflow for provisioning a dev environment and making a copy
available.

.. code-block:: Python

    """examples/link_snapshot.py"""

    import PyU4V
    from time import strftime

    # Set up connection to Unisphere for PowerMax Server, details collected
    # from configuration file in working directory where script is stored.
    conn = PyU4V.U4VConn()

    # Create storage Group with one volume
    storage_group = conn.provisioning.create_non_empty_storage_group(
        srp_id='SRP_1', storage_group_id='PyU4V_SG', service_level='Diamond',
        workload=None, num_vols=1, vol_size=1, cap_unit='GB')

    # Define a Name for the Snapshot, in this case the name auto appends the
    # host time for when it was taken for ease of identification
    snap_name = 'PyU4V_Snap_' + time.strftime('%d%m%Y%H%M%S')

    # Create the snapshot of the storage group containing the volume and
    # storage group created in the previous step
    snapshot = conn.replication.create_storage_group_snapshot(
        storage_group_id=storage_group['storageGroupId'], snap_name=snap_name)

    # Link The Snapshot to a new storage group, the API will automatically
    # create the link storage group with the right number of volumes if one
    # with that name doesn't already exist
    conn.replication.modify_storage_group_snapshot(
        src_storage_grp_id=storage_group['storageGroupId'],
        tgt_storage_grp_id='PyU4V_LNK_SG', link=True,
        snap_name=snap_name, gen_num=0)

    # Close the session
    conn.close_session()

Remote Replication with SRDF
----------------------------

This example will create a storage group on the PowerMax array with some
volumes.  Once the storage group has been created it will protect the volumes
in the storage group to a remote array using SRDF/Metro, providing
Active/Active business continuity via Symmetrix Remote Data Facility (SRDF).

.. code-block:: Python

    """srdf_example.py"""

    import PyU4V

    # Initialise PyU4V connection to Unisphere
    conn = PyU4V.U4VConn()

    # Create storage Group with one volume using settings specified for
    # service level and capacity
    storage_group = conn.provisioning.create_non_empty_storage_group(
        srp_id='SRP_1', storage_group_id='PyU4V_SG', service_level='Diamond',
        workload=None, num_vols=1, vol_size=1, cap_unit='GB')

    # Make a call to setup the remote replication, this will automatically
    # create a storage group with the same name on the remote array with the
    # correct volume count and size, the example here is executed
    # asynchronously and a wait is added to poll the async job id until
    # complete
    srdf_job_id = conn.replication.create_storage_group_srdf_pairings(
        storage_group_id=storage_group['storageGroupId'],
        remote_sid=conn.remote_array, srdf_mode="Active", _async=True)

    # Wait until the previous create SRDF pairing job has completed before
    # proceeding
    conn.common.wait_for_job_complete(job=srdf_job_id)

    # The now protected storage group will have an RDFG associated with it,
    # using the function conn.replication.get_storage_group_rdfg() function we
    # can retrieve a list of RDFGs associated with the storage group, in this
    # case there will only be one
    rdfg_list = conn.replication.get_storage_group_srdf_group_list(
        storage_group_id=storage_group['storageGroupId'])

    # Extract the (only) RDFG number from the retrieved list
    rdfg_number = rdfg_list[0]

    # Finally the details of the protected storage group can be output to the
    # user.
    storage_group_srdf_info = conn.replication.get_storage_group_srdf_details(
        storage_group_id=storage_group['storageGroupId'],
        rdfg_num=rdfg_number)

    # Close the session
    conn.close_session()


Performance Metrics Gathering
-----------------------------

This example demonstrates a range of performance functionality such as getting
performance categories and metrics, timestamps from Unisphere for an array,
get recent only performance information, and getting ResponseTime for all
SRPs in an array.

.. code-block:: Python

    """examples/performance_data_retrieval.py"""

    from PyU4V import U4VConn

    # Initialise PyU4V Unisphere connection
    conn = PyU4V.U4VConn(
        u4v_version='90', server_ip='10.0.0.75', port=8443,
        verify='~/.PyU4V/Unisphere91.pem', username='pyu4v-user',
        password='secret-pass')

    # Get a list of performance categories
    category_list = conn.performance.get_performance_categories_list()

    # Get a list of supported metrics for the category 'FEDirector'
    fe_dir_metrics = conn.performance.get_performance_metrics_list(
        category='FEDirector')

    # Get a list of KPI only metrics for the category 'StorageGroup'
    storage_group_metrics = conn.performance.get_performance_metrics_list(
        category='StorageGroup', kpi_only=True)

    # Get array KPI performance metrics for the most recent timestamp only,
    # set recency so timestamp has to be less than 5 minutes old
    array_performance_data = conn.performance.get_array_stats(metrics='KPI',
                                                              recency=5)

    # Get ResponseTime for each SRP for the last 4 hours
    # Firstly get the most recent performance timestamp for your array
    recent_timestamp = conn.performance.get_last_available_timestamp()
    # Set the performance recency value to 10 minutes and check if the most
    # recent timestamp meets that recency value
    conn.performance.recency = 10
    is_recent_ten = conn.performance.is_timestamp_current(recent_timestamp)
    # Recency can also be passed to is_timestamp_current
    is_recent_five = conn.performance.is_timestamp_current(recent_timestamp,
                                                           minutes=5)

    # Get the start and end times by providing the most recent timestamp and
    # specifying a 4 hour difference
    start_time, end_time = conn.performance.get_timestamp_by_hour(
        end_time=recent_timestamp, hours_difference=4)
    # Get the list of SRPs
    srp_keys = conn.performance.get_storage_resource_pool_keys()
    srp_list = list()
    for key in srp_keys:
        srp_list.append(key.get('srpId'))
    # Get the performance data for each of the SRPs in the list
    for srp in srp_list:
        srp_data = conn.performance.get_storage_resource_pool_stats(
            srp_id=srp, metrics='ResponseTime', start_time=start_time,
            end_time=end_time)

    # Close the session
    conn.close_session()

System
------

This example of system calls demonstrates performing a system health check,
retrieving information from the last health check, querying for all installed
disk IDs in an array and outputting information about each.

.. code-block:: Python

    """examples/system_health_check.py."""

    import PyU4V

    # Initialise PyU4V connection to Unisphere
    conn = PyU4V.U4VConn(
            u4v_version='90', server_ip='10.0.0.75', port=8443,
            verify='~/.PyU4V/Unisphere91.pem', username='pyu4v-user',
            password='secret-pass')

    # Perform a system health check, this call can take 15-20 minutes to
    # complete in Unisphere due to the nature of the checks performed
    conn.system.perform_health_check(description='test-hc-dec19')

    # Get details of the last system health check
    health_check = conn.system.get_system_health()

    # Get a list of physical disks installed in the array
    disk_list = conn.system.get_disk_id_list()

    # Get disk information for each disk installed
    for disk in disk_list.get('disk_ids'):
        disk_info = conn.system.get_disk_details(disk_id=disk)

    # Close the session
    conn.close_session()


File Handling & Thresholds
--------------------------

In this example both performance threshold calls and CSV file handling with
PyU4V are demonstrated.  A call is made to retrieve a full list of performance
threshold settings and output the results to a CSV file at a path specified
by the user. That CSV file is read into a Python dictionary and the respective
values within are updated. Once complete the updated threshold settings are
uploaded to Unisphere to take immediate effect.

.. code-block:: Python

    """examples/thresholds.py."""

    import os
    import PyU4V

    # Initialise PyU4V connection to Unisphere
    conn = PyU4V.U4VConn()

    # Set the CSV file name and path
    current_directory = os.getcwd()
    output_csv_name = 'thresholds-test.csv'
    output_csv_path = os.path.join(current_directory, output_csv_name)

    # Generate a CSV file with all of the thresholds and corresponding values
    conn.performance.generate_threshold_settings_csv(
        output_csv_path=output_csv_path)

    # Read the CSV values into a dictionary, cast all string booleans and
    # numbers to their proper types
    threshold_dict = PyU4V.utils.file_handler.read_csv_values(output_csv_path,
                                                              convert=True)

    # Increase all of the first threshold values by 5 and second threshold
    # values by 10, alert only on the KPIs
    for i in range(0, len(threshold_dict.get('metric'))):
        threshold_dict['firstThreshold'][i] += 5
        threshold_dict['secondThreshold'][i] += 5
        if threshold_dict['kpi'][i] is True:
            threshold_dict['alertError'][i] = True

    # Process the CSV file and update the thresholds with their corresponding
    # values, we are only going to set the threshold value if it is a KPI
    conn.performance.set_thresholds_from_csv(csv_file_path=output_csv_path,
                                             kpi_only=True)

    # It is also possible to set a threshold value without editing the values
    # in a CSV, the threshold metric and be edited directly
    threshold_settings = conn.performance.update_threshold_settings(
        category='Array', metric='PercentCacheWP', alert=True,
        first_threshold=60, first_threshold_occurrences=2,
        first_threshold_samples=6, first_threshold_severity='INFORMATION',
        second_threshold=90, second_threshold_occurrences=1,
        second_threshold_samples=3, second_threshold_severity='CRITICAL')

    # Close the session
    conn.close_session()
