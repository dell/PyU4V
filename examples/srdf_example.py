# Copyright (c) 2019 Dell Inc. or its subsidiaries.
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
