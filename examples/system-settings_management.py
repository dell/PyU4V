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
"""docs/source/programmers_guide_src/code/system-settings_management.py."""

import PyU4V

# Initialise PyU4V connection to Unisphere
conn = PyU4V.U4VConn()

# Download system settings for primary array defined in PyU4V.conf, exclude the
# system thresholds settings
settings_info = conn.system.download_system_settings(
    file_password='PyU4V', dir_path='~/datastore/system_settings',
    file_name='settings_gold_master', exclude_system_threshold_settings=True)

# Assert the download operation was successful and print the location of the
# downloaded file
assert settings_info.get('success') is True
print('The system settings for {array} are saved to: {loc}'.format(
    array=conn.array_id, loc=settings_info.get('settings_path')))

# Upload the settings and apply to target array
upload_details = conn.system.upload_settings(
    file_password='PyU4V', file_path=settings_info.get('settings_path'),
    array_id='000111222333')

# Close the session
conn.close_session()
