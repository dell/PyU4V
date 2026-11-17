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
"""docs/source/programmers_guide_src/code/settings-operations.py."""

import PyU4V

# Initialise PyU4V connection to Unisphere
conn = PyU4V.U4VConn()

# Get current performance registration settings
perf_settings = conn.settings.get_performance_registration_settings()
print('Performance registration settings: {s}'.format(s=perf_settings))

# Update performance registration settings - enable diagnostic and
# real-time data collection for an array
conn.settings.update_performance_registration_settings(
    array_id=conn.array_id, diagnostic=True, real_time=True)

# Get Secure Connect Gateway (SCG) configuration details
scg_config = conn.settings.get_scg_configuration_details()
print('SCG configuration: {c}'.format(c=scg_config))

# Get CloudIQ data collection configuration
cloudiq_config = conn.settings.get_cloudiq_data_collection_configuration()
print('CloudIQ config: {c}'.format(c=cloudiq_config))

# Close the session
conn.close_session()
