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
"""docs/source/programmers_guide_src/code/performance-thresholds.py."""

import os
import PyU4V

# Initialise PyU4V connection to Unisphere
conn = PyU4V.U4VConn()

# Set the CSV file name and path
current_directory = os.getcwd()
output_csv_name = 'thresholds-test.csv'
output_csv_path = os.path.join(current_directory, output_csv_name)

# Generate a CSV file with all of the thresholds and corresponding values
conn.performance.generate_threshold_settings_csv(
    output_csv_path=output_csv_path)

# Read the CSV values into a dictionary, cast all string booleans and
# numbers to their proper types
threshold_dict = PyU4V.utils.file_handler.read_csv_values(output_csv_path,
                                                          convert=True)

# Increase all of the first threshold values by 5 and second threshold
# values by 10, alert only on the KPIs
for i in range(0, len(threshold_dict.get('metric'))):
    threshold_dict['firstThreshold'][i] += 5
    threshold_dict['secondThreshold'][i] += 5
    if threshold_dict['kpi'][i] is True:
        threshold_dict['alertError'][i] = True

# Process the CSV file and update the thresholds with their corresponding
# values, we are only going to set the threshold value if it is a KPI
conn.performance.set_thresholds_from_csv(csv_file_path=output_csv_path,
                                         kpi_only=True)

# It is also possible to set a threshold value without editing the values
# in a CSV, the threshold metric and be edited directly
threshold_settings = conn.performance.update_threshold_settings(
    category='Array', metric='PercentCacheWP', first_threshold=60,
    first_threshold_occurrences=2, first_threshold_samples=6,
    first_threshold_severity='INFORMATION', second_threshold=90,
    second_threshold_occurrences=1, second_threshold_samples=3,
    second_threshold_severity='CRITICAL', alert=True)

# Close the session
conn.close_session()
