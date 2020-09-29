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
"""docs/source/programmers_guide_src/code/system-audit_log_download.py."""

import PyU4V

# Initialise PyU4V connection to Unisphere
conn = PyU4V.U4VConn()

# Download PDF audit log record for the last week for primary array
audit_log_details = conn.system.download_audit_log_record(
    return_binary=False, dir_path='~/datastore/audit_records',
    file_name='audit-log-sept2020')

# Assert the download operation was successful
assert audit_log_details.get('success') is True
print('The audit log has been downloaded to: {loc}'.format(
    loc=audit_log_details.get('audit_record_path')))

# Close the session
conn.close_session()
