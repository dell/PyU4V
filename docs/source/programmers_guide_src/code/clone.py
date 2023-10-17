# Copyright (c) 2023 Dell Inc. or its subsidiaries.
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
"""docs/source/programmers_guide_src/code/clone.py."""

import PyU4V

# Initialise PyU4V connection to Unisphere
conn = PyU4V.U4VConn()

# Create a Clone Copy of a Storage group, The Target Storage Group will be
# created with all required volumes for the clone copy if it does not exist
# already.
# Using the Establish & Terminate Boolean value in the example removes the
# clone session leaving the source and target devices indepenent of
# each other, the default value of false will allow you to create
# differential copies, updating the data on target storage group volumes.

conn.clone.create_clone(
    storage_group_id="clonesrc", target_storage_group_id="clonetgt",
    establish_terminate=True)

# Close the session
conn.close_session()
