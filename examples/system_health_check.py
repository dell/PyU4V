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
"""system_health_check.py."""

import PyU4V

# Initialise PyU4V connection to Unisphere
conn = PyU4V.U4VConn(
    u4v_version='90', server_ip='10.0.0.75', port=8443,
    verify='~/.PyU4V/Unisphere91.pem', username='pyu4v-user',
    password='secret-pass')

# Perform a system health check, this call can take 15-20 minutes to
# complete in Unisphere due to the nature of the checks performed
conn.system.perform_health_check(description='test-hc-dec19')

# Get details of the last system health check
health_check = conn.system.get_system_health()

# Get a list of physical disks installed in the array
disk_list = conn.system.get_disk_id_list()
# Get disk information for each disk installed
for disk in disk_list.get('disk_ids'):
    disk_info = conn.system.get_disk_details(disk_id=disk)
