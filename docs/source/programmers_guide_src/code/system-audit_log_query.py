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
"""docs/source/programmers_guide_src/code/system-audit_log_query.py."""

import random
import time

import PyU4V

# Initialise PyU4V connection to Unisphere
conn = PyU4V.U4VConn()

# Get a list of audit logs for the last ten minutes where the user name and
# host name are defined as filters to return only matching results. Note, the
# time interval here, similar to performance calls, is also in milliseconds
# since epoch
current_time = int(time.time()) * 1000
start_time = current_time - (60 * 10 * 1000)
audit_log_list = conn.system.get_audit_log_list(
    start_time=start_time, end_time=current_time, user_name='PyU4V',
    host_name='PyU4V-Host')

# Select an audit log record from the list of audit logs and get the
# associated audit log record ID
audit_log_record = random.choice(audit_log_list)
audit_log_record_id = audit_log_record.get('record_id')

# Retrieve detailed information on a record returned in the audit log list
audit_log_detailed = conn.system.get_audit_log_record(
    record_id=audit_log_record_id)

# Close the session
conn.close_session()
