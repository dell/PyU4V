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
"""docs/source/programmers_guide_src/code/volumes-storage_groups.py."""

import PyU4V

# Initialise PyU4V connection to Unisphere
conn = PyU4V.U4VConn()

# --- Volumes ---

# Get available metadata attributes for volumes
volume_metadata = conn.volumes.get_volumes_meta_data()
print('Volume metadata attributes: {m}'.format(m=volume_metadata))

# Get all volumes with default attributes
all_volumes = conn.volumes.get_volumes_details()
print('All volumes: {v}'.format(v=all_volumes))

# Get volumes with specific attributes selected
filtered_volumes = conn.volumes.get_volumes_details(
    select=['id', 'effective_wwn', 'cap_gb', 'storage_groups'],
    filters=['identifier ilike myhost'])
print('Filtered volumes: {v}'.format(v=filtered_volumes))

# --- Storage Groups ---

# Get available metadata attributes for storage groups
sg_metadata = conn.storage_groups.get_storage_groups_meta_data()
print('Storage group metadata attributes: {m}'.format(m=sg_metadata))

# Get all storage groups with default attributes
all_sgs = conn.storage_groups.get_storage_groups_details()
print('All storage groups: {sg}'.format(sg=all_sgs))

# Get storage groups filtered by name pattern and volume count
filtered_sgs = conn.storage_groups.get_storage_groups_details(
    select=['id', 'num_of_volumes', 'cap_gb', 'type'],
    filters=['id ilike prod', 'num_of_volumes gt 0'])
print('Filtered storage groups: {sg}'.format(sg=filtered_sgs))

# Close the session
conn.close_session()
