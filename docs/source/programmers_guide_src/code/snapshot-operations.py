# Copyright (c) 2026 Dell Inc. or its subsidiaries.
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
"""docs/source/programmers_guide_src/code/snapshot-operations.py"""

import PyU4V
import time

# Initialise PyU4V connection to Unisphere
conn = PyU4V.U4VConn()

# Check if SnapVX is licensed on the array
is_licensed = conn.snapshot.is_snapvx_licensed()
print(f'SnapVX licensed: {is_licensed}')

# Create a storage group with one 1GB volume
storage_group = conn.provisioning.create_non_empty_storage_group(
    srp_id='SRP_1', storage_group_id='PyU4V_Snap_SG',
    service_level='Diamond', workload=None, num_vols=1,
    vol_size=1, cap_unit='GB')
sg_id = storage_group['storageGroupId']

# Create a snapshot with an auto-generated name
snap_name = 'PyU4V_Snap_' + time.strftime('%d%m%Y%H%M%S')
snapshot = conn.snapshot.create_storage_group_snapshot(
    storage_group_id=sg_id, snap_name=snap_name)
print(f'Created snapshot: {snapshot["name"]}')

# Create a snapshot with a TTL of 1 day
snap_ttl = conn.snapshot.create_storage_group_snapshot(
    storage_group_id=sg_id, snap_name='PyU4V_TTL_Snap', ttl='1')
print(f'Created TTL snapshot: {snap_ttl["name"]}')

# List all snapshots for the storage group
snap_list = conn.snapshot.get_storage_group_snapshot_list(sg_id)
print(f'Snapshots: {snap_list}')

# Get snap IDs for a named snapshot
snap_ids = conn.snapshot.get_storage_group_snapshot_snap_id_list(
    sg_id, snap_name)
print(f'Snap IDs for {snap_name}: {snap_ids}')

# Get details for a specific snap ID
if snap_ids:
    details = conn.snapshot.get_snapshot_snap_id_details(
        sg_id, snap_name, snap_ids[0])
    print(f'Snap details: state={details.get("state")}')

# Link the snapshot to a new target storage group
if snap_ids:
    conn.snapshot.link_snapshot_by_snap_id(
        sg_id=sg_id, link_sg_name='PyU4V_Snap_TGT',
        snap_name=snap_name, snap_id=snap_ids[0])
    print('Snapshot linked to PyU4V_Snap_TGT')

# Unlink the snapshot from the target storage group
if snap_ids:
    conn.snapshot.unlink_snapshot_by_snap_id(
        sg_id=sg_id, unlink_sg_name='PyU4V_Snap_TGT',
        snap_name=snap_name, snap_id=snap_ids[0])
    print('Snapshot unlinked from PyU4V_Snap_TGT')

# Rename a snapshot
if snap_ids:
    conn.snapshot.rename_snapshot_by_snap_id(
        sg_id=sg_id, snap_name=snap_name,
        new_name='PyU4V_Snap_Renamed', snap_id=snap_ids[0])
    print('Snapshot renamed')

# Find any expired snapshots on the array
expired = conn.snapshot.find_expired_snapvx_snapshots_by_snap_ids()
print(f'Expired snapshots: {len(expired)}')

# Delete a snapshot by snap ID
if snap_ids:
    conn.snapshot.delete_storage_group_snapshot_by_snap_id(
        storage_group_id=sg_id, snap_name='PyU4V_Snap_Renamed',
        snap_id=snap_ids[0])
    print('Snapshot deleted')

# Close the session
conn.close_session()
