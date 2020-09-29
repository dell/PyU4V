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
"""docs/source/programmers_guide_src/code/replication-metro_dr.py"""

import PyU4V

# Initialise PyU4V connection to Unisphere
conn = PyU4V.U4VConn()

metro_r1_array_id = '000297600111'
metro_r2_array_id = '000297600112'
dr_array_id = '000297600113'

sg_name = 'PyU4V_Test_MetroDR'
environment_name = 'PyU4VMetro'

# Create a storage Group with some volumes
sg_details = conn.provisioning.create_non_empty_storage_group(
    storage_group_id=sg_name, service_level='Diamond',
    num_vols=5, vol_size=6, cap_unit='GB', srp_id='SRP_1',
    workload=None)

"""
The next call section creates the metro dr environment, this includes all
Necessary SRDF setup creating the SRDF metro pairings and remote devices
and storage group at the Metro R2 array.

The API also creates all the necessary SRDF groups between R11, R21 and R2
for the DR leg, this includes a recovery SRDF group.  The example is
using async execution of the REST calls,  this task can take many
minutes to complete and depending on the number of devices.
"""
job = conn.metro_dr.create_metrodr_environment(
    storage_group_name=sg_name, environment_name=environment_name,
    metro_r1_array_id=metro_r1_array_id, metro_r2_array_id=metro_r2_array_id,
    dr_array_id=dr_array_id, dr_replication_mode='adaptivecopydisk')

conn.common.wait_for_job_complete(job=job)

metro_dr_env_details = conn.metro_dr.get_metrodr_environment_details(
    environment_name, array_id=metro_r1_array_id)

# Close the session
conn.close_session()
