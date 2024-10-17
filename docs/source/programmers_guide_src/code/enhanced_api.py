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
"""docs/source/programmers_guide_src/code/basic-unisphere_connect.py."""

import PyU4V

# Initialise PyU4V connection to Unisphere
conn = PyU4V.U4VConn(
    server_ip='10.0.0.75', port=8443, verify='~/.PyU4V/Unisphere102.pem',
    username='pyu4v-user', password='secret-pass', array_id='0001967200123')

# Get Details on all storage groups for the specified Storage Array,
# selecting values that are needed for report.
print(conn.storage_groups.get_storage_groups_details())

# Get Details on what data you can gather about storage volumes.
print(conn.volumes.get_volumes_meta_data())
# Get a list of volumes with their storage group id,
print(conn.volumes.get_volumes_details(
    select=['id', 'effective_wwn', 'effective_wwn', 'storage_groups', 'cap_gb',
            ],
    filters=['identifier ilike findme']))

# get all diagnostic Key Performance indicator metrics for last 5 minute
# interval for the specified storage array

print(conn.performance_enhanced.get_all_performance_metrics_for_system())

# Close the session
conn.close_session()
