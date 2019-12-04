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
"""snapshot_create.py"""

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
