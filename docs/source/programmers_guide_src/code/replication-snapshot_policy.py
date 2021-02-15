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
"""docs/source/programmers_guide_src/code/replication-snapshot_policy.py"""

import PyU4V

# Set up connection to Unisphere for PowerMax Server, details collected
# from configuration file in working directory where script is stored.
conn = PyU4V.U4VConn()

# Create storage Group with one volume
storage_group = conn.provisioning.create_non_empty_storage_group(
    srp_id='SRP_1', storage_group_id='PyU4V_SG', service_level='Diamond',
    workload=None, num_vols=1, vol_size=1, cap_unit='GB')

# Create a snapshot policy for the new storage group
policy_name = 'PyU4V-Test_Policy'
snap_policy = conn.snapshot_policy.create_snapshot_policy(
    snapshot_policy_name=policy_name, interval='1 Day',
    cloud_retention_days=7, cloud_provider_name='Generic_Provider',
    local_snapshot_policy_snapshot_count=5)

# Confirm the snapshot policy was created successfully
assert policy_name in conn.snapshot_policy.get_snapshot_policy_list()

# Get snapshot policy detailed info
snap_policy_details = conn.snapshot_policy.get_snapshot_policy(
    snapshot_policy_name=policy_name)

# Modify the snapshot policy
new_policy_name = 'PyU4V-Test_Policy-5mins'
new_snap_policy = conn.snapshot_policy.modify_snapshot_policy(
    snapshot_policy_name=policy_name, action='Modify',
    new_snapshot_policy_name=new_policy_name, interval_mins=5)

# Confirm the snapshot policy was renamed successfully
assert new_policy_name in conn.snapshot_policy.get_snapshot_policy_list()
assert policy_name not in conn.snapshot_policy.get_snapshot_policy_list()

# Delete the snapshot policy
conn.snapshot_policy.delete_snapshot_policy(
    snapshot_policy_name=new_policy_name)

# Close the session
conn.close_session()
