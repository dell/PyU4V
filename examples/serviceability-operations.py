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
"""docs/source/programmers_guide_src/code/serviceability-operations.py."""

import PyU4V

# Initialise PyU4V connection to Unisphere
conn = PyU4V.U4VConn()

# Get local system information (embedded environments only)
local_system = conn.serviceability.get_local_system()
print('Local system: {sys}'.format(sys=local_system))

# Get current NTP server configuration
ntp_settings = conn.serviceability.get_ntp_settings()
print('NTP settings: {ntp}'.format(ntp=ntp_settings))

# Download serviceability grab files (GRAB logs) for diagnostics.
# Note: This can take some time, set an appropriate timeout.
grab_result = conn.serviceability.download_grab_files(
    node_name='Semgmt0', dir_path='.', file_name='grab_logs',
    timeout=600)
print('Grab file download result: {res}'.format(res=grab_result))

# Close the session
conn.close_session()
