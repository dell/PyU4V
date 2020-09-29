# Copyright (c) 2020 Dell Inc. or its subsidiaries.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""docs/source/programmers_guide_src/code/provision-async_create_storage.py"""

import PyU4V

# Initialise PyU4V connection to Unisphere
conn = PyU4V.U4VConn()

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
    initiator_list = ['iqn:2020-test1', 'iqn:2020-test1']
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
