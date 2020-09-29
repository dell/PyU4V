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
"""docs/source/programmers_guide_src/code/performance-real_time_calls.py"""

import random
import time

import PyU4V

# Initialise PyU4V Unisphere connection
conn = PyU4V.U4VConn()

# Get a list of real-time performance categories
category_list = conn.performance.real_time.get_categories()

# Get the first and last available timestamps for my primary array
array_timestamps = conn.performance.real_time.get_timestamps(
    array_id=conn.array_id)
# Get the first and last available timestamps for all registered arrays
all_timestamps = conn.performance.real_time.get_timestamps()

# Get storage groups enabled for real-time data on primary array
rt_sg_list = conn.performance.real_time.get_storage_group_keys()
# Get the real-time metrics for storage groups
rt_sg_metrics = conn.performance.real_time.get_storage_group_metrics()

# Get the current time in milliseconds since epoch
current_time = int(time.time()) * 1000
# Set the start time as one hour previous to current time, one hour is the
# maximum amount of data that can be retrieved in one call for real-time
start_time = current_time - (60 * 60 * 1000)

# Get real-time storage group data for a random group and random selection of
# metrics
sg_metrics = random.choices(rt_sg_metrics, k=5)
sg_name = random.choice(rt_sg_list)

# Retrieve the performance data from Unisphere
rt_sg_data = conn.performance.real_time.get_storage_group_stats(
    start_date=start_time, end_date=current_time, metrics=sg_metrics,
    instance_id=sg_name)

# Close the session
conn.close_session()
