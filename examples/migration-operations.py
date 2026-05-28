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
"""docs/source/programmers_guide_src/code/migration-operations.py."""

import PyU4V

# Initialise PyU4V connection to Unisphere
conn = PyU4V.U4VConn()

# Get migration information for the primary array
migration_info = conn.migration.get_migration_info()
print('Migration info: {info}'.format(info=migration_info))

# Check migration capabilities for the array
capabilities = conn.migration.get_array_migration_capabilities()
print('Migration capabilities: {cap}'.format(cap=capabilities))

# List existing migration environments
environments = conn.migration.get_environment_list()
print('Migration environments: {env}'.format(env=environments))

# Create a migration environment to a target array
target_array = '000297900124'
new_env = conn.migration.create_migration_environment(
    target_array_id=target_array)
print('Created migration environment: {env}'.format(env=new_env))

# Get details of the migration environment
env_details = conn.migration.get_environment(
    target_array_id=target_array)
print('Environment details: {det}'.format(det=env_details))

# Create a storage group migration session
sg_migration = conn.migration.create_storage_group_migration(
    storage_group_name='my_sg', target_array_id=target_array,
    srp_id='SRP_1')
print('SG migration session: {sg}'.format(sg=sg_migration))

# Get storage group migration details
sg_details = conn.migration.get_storage_group(
    storage_group_name='my_sg')
print('SG migration details: {det}'.format(det=sg_details))

# Cutover the migration
conn.migration.modify_storage_group_migration(
    storage_group_name='my_sg', action='Cutover')

# Commit the migration
conn.migration.modify_storage_group_migration(
    storage_group_name='my_sg', action='Commit')

# Delete migration session and environment when complete
conn.migration.delete_storage_group_migration(
    storage_group_name='my_sg')
conn.migration.delete_migration_environment(
    target_array_id=target_array)

# Close the session
conn.close_session()
