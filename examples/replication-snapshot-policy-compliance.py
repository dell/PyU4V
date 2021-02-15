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
"""docs/source/programmers_guide_src/code/
replication-snapshot-policy-compliance.py"""

import PyU4V

# Set up connection to Unisphere for PowerMax Server, details collected
# from configuration file in working directory where script is stored.
conn = PyU4V.U4VConn()

# Create a snapshot policy
snapshot_policy_name = 'PyU4V_Compliance_Policy'
conn.snapshot_policy.create_snapshot_policy(
    snapshot_policy_name=snapshot_policy_name, interval='1 Day',
    local_snapshot_policy_snapshot_count=5)

# Get the snapshot policy
snapshot_policy_details = (
    conn.snapshot_policy.get_snapshot_policy(snapshot_policy_name))

# Check that snapshot policy exists
assert snapshot_policy_details and snapshot_policy_details.get(
    'snapshot_policy_name')

# Create storage Group with one volume and associate with snapshot
# policy.
storage_group_name = 'PyU4V_compliance_SG'
storage_group = conn.provisioning.create_non_empty_storage_group(
    srp_id='SRP_1', storage_group_id=storage_group_name,
    service_level='Diamond', workload=None,
    num_vols=1, vol_size=1, cap_unit='GB',
    snapshot_policy_ids=[snapshot_policy_name])

# Get the storage group
storage_group_details = conn.provisioning.get_storage_group(
    storage_group_name)

# Check that storage group exists
assert storage_group_details and storage_group_details.get('storageGroupId')

# Get the compliance details
compliance_details = (
    conn.snapshot_policy.get_snapshot_policy_compliance_last_week(
        storage_group_name))

# Check details have been return
assert compliance_details

# Disassociate from snapshot policy
conn.snapshot_policy.modify_snapshot_policy(
    snapshot_policy_name, 'DisassociateFromStorageGroups',
    storage_group_names=[storage_group_name])

# Delete the snapshot policy
conn.snapshot_policy.delete_snapshot_policy(snapshot_policy_name)

# Get volumes from the storage group
volume_list = (conn.provisioning.get_volumes_from_storage_group(
    storage_group_name))

# Delete the storage group
conn.provisioning.delete_storage_group(storage_group_id=storage_group_name)

# Delete each volume from storage group
for volume in volume_list:
    conn.provisioning.delete_volume(volume)

# Close the session
conn.close_session()
