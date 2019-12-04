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
"""performance_calls.py"""

import PyU4V

# Initialise PyU4V Unisphere connection
conn = PyU4V.U4VConn(
    u4v_version='90', server_ip='10.0.0.75', port=8443,
    verify='~/.PyU4V/Unisphere91.pem', username='pyu4v-user',
    password='secret-pass')

# Get a list of performance categories
category_list = conn.performance.get_performance_categories_list()

# Get a list of supported metrics for the category 'FEDirector'
fe_dir_metrics = conn.performance.get_performance_metrics_list(
    category='FEDirector')

# Get a list of KPI only metrics for the category 'StorageGroup'
storage_group_metrics = conn.performance.get_performance_metrics_list(
    category='StorageGroup', kpi_only=True)

# Get array KPI performance metrics for the most recent timestamp only, set
# recency so timestamp has to be less than 5 minutes old
array_performance_data = conn.performance.get_array_stats(metrics='KPI',
                                                          recency=5)

# Get ResponseTime for each SRP for the last 4 hours
# Firstly get the most recent performance timestamp for your array
recent_timestamp = conn.performance.get_last_available_timestamp()
# Set the performance recency value to 10 minutes and check if the most
# recent timestamp meets that recency value
conn.performance.recency = 10
is_recent_ten = conn.performance.is_timestamp_current(recent_timestamp)
# Recency can also be passed to is_timestamp_current
is_recent_five = conn.performance.is_timestamp_current(recent_timestamp,
                                                       minutes=5)

# Get the start and end times by providing the most recent timestamp and
# specifying a 4 hour difference
start_time, end_time = conn.performance.get_timestamp_by_hour(
    end_time=recent_timestamp, hours_difference=4)
# Get the list of SRPs
srp_keys = conn.performance.get_storage_resource_pool_keys()
srp_list = list()
for key in srp_keys:
    srp_list.append(key.get('srpId'))
# Get the performance data for each of the SRPs in the list
for srp in srp_list:
    srp_data = conn.performance.get_storage_resource_pool_stats(
        srp_id=srp, metrics='ResponseTime', start_time=start_time,
        end_time=end_time)

# Close the session
conn.close_session()
