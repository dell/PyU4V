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
"""docs/source/programmers_guide_src/code/custom_call.py."""
import PyU4V

# Initialise PyU4V connection to Unisphere
conn = PyU4V.U4VConn()

# Create a Clone Copy of a Stoage group, The Target Storage Group will be
# created with all required volumes for the clone copy if it does not exist
# already.


def my_custom_api_Call(
        storage_group_id, target_storage_group_id,
        consistent=True, establish_terminate=False,
        array_id=None, force=False, star=False, skip=False):
    """Create Clone.
    :param storage_group_id: The Storage Group ID -- string
    :param consistent: creates the clone crash consistent using ECA
                       technology -- bool
    :param establish_terminate: creates the clone and immediately
                                terminates, very useful if you want to
                                make an independent copy available
                                immediately but don't intend to use for
                                restore purposes -- bool
    :param array_id: The storage array ID -- string
    :param target_storage_group_id: name of storage group to contain
                                      clone devices -- string
    :param force: Attempts to force the operation even though one or more
                  volumes may not be in the normal, expected state(s) for
                  the specified operation -- bool
    :param star: Acknowledge the volumes are in an SRDF/Star
                 configuration -- bool
    :param skip: Skips the source locks action -- bool

    """
    array_id = array_id if array_id else conn.array_id
    payload = {
        "target_storage_group_name": target_storage_group_id,
        "establish_terminate": establish_terminate,
        "consistent": consistent,
        "force": force,
        "star": star,
        "skip": skip
    }
    return conn.common.create_resource(
        target_uri=f"/100/replication/symmetrix"
                   f"/{array_id}/storagegroup/{storage_group_id}"
                   f"/clone/storagegroup", payload=payload)


# Close the session
conn.close_session()
