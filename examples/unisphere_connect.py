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
"""unisphere_connect.py."""

import PyU4V

# Initialise PyU4V connection to Unisphere
conn = PyU4V.U4VConn(
    u4v_version='90', server_ip='10.0.0.75', port=8443,
    verify='~/.PyU4V/Unisphere91.pem', username='pyu4v-user',
    password='secret-pass')

# Get the Unisphere version
version = conn.common.get_uni_version()

# Retrieve a list of arrays managed by your instance of Unisphere
array_list = conn.common.get_array_list()

# Output results to screen
print('Congratulations on your first connection to Unisphere, your '
      'version is: {ver}'.format(ver=version[0]))
print('This instance of Unisphere instance manages the following arrays: '
      '{arr_list}'.format(arr_list=array_list))

# GET those arrays which are local to this instance of Unisphere
local_array_list = list()
for array_id in array_list:
    array_details = conn.common.get_array(array_id)
    if array_details['local']:
        local_array_list.append(array_id)

# Output results to screen
print('The following arrays are local to this Unisphere instance: '
      '{arr_list}'.format(arr_list=local_array_list))

# Close the session
conn.close_session()
