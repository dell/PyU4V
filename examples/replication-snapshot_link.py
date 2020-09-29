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
"""docs/source/programmers_guide_src/code/replication-snapshot_link.py"""

import PyU4V
import time

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
snapshot_details = conn.replication.get_storage_group_snapshot_snap_id_list(
    storage_group['storageGroupId'], snap_name)
snap_id = snapshot_details[0]

# Link The Snapshot to a new storage group, the API will automatically
# create the link storage group with the right number of volumes if one
# with that name doesn't already exist
conn.replication.modify_storage_group_snapshot_by_snap_id(
    src_storage_grp_id=storage_group['storageGroupId'],
    tgt_storage_grp_id='PyU4V_LNK_SG',
    snap_name=snap_name, snap_id=snap_id, link=True,)

# Close the session
conn.close_session()
