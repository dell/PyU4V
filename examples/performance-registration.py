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
"""docs/source/programmers_guide_src/code/performance-registration.py"""

import PyU4V

# Initialise PyU4V Unisphere connection
conn = PyU4V.U4VConn()

# Check if the primary array is registered for diagnostic performance data
# collection
if not conn.performance.is_array_diagnostic_performance_registered():
    # If not, enable diagnostic data collection
    conn.performance.enable_diagnostic_data_collection()
    # Confirm the enable operation was successful
    assert conn.performance.is_array_diagnostic_performance_registered()

# Check if the primary array is registered for real-time performance data
# collection
if not conn.performance.is_array_real_time_performance_registered():
    # If not, enable real-time data collection
    conn.performance.enable_real_time_data_collection()
    # Confirm the enable operation was successful
    assert conn.performance.is_array_real_time_performance_registered()

# Close the session
conn.close_session()
