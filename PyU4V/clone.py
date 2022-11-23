# Copyright (c) 2022 Dell Inc. or its subsidiaries.
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
"""clone.py."""

import logging

from PyU4V.common import CommonFunctions
from PyU4V.provisioning import ProvisioningFunctions
from PyU4V.utils import constants
from PyU4V.utils import exception

LOG = logging.getLogger(__name__)

# Resource constants
ASYNC_UPDATE = constants.ASYNC_UPDATE
REPLICATION = constants.REPLICATION
SYMMETRIX = constants.SYMMETRIX
CAPABILITIES = constants.CAPABILITIES
STORAGEGROUP = constants.STORAGEGROUP
RDFG = constants.RDFG
RDF_GROUP = constants.RDF_GROUP
METRO_DR = constants.METRO_DR
ASYNCHRONOUS = constants.ASYNCHRONOUS_CC
ADAPTIVE_COPY = constants.ADAPTIVE_COPY


class CloneFunctions(object):
    """Clone Functions."""

    def __init__(self, array_id, rest_client):
        """__init__."""
        self.provisioning = ProvisioningFunctions(array_id, rest_client)
        self.common = CommonFunctions(rest_client)
        self.get_resource = self.common.get_resource
        self.create_resource = self.common.create_resource
        self.modify_resource = self.common.modify_resource
        self.delete_resource = self.common.delete_resource
        self.array_id = array_id
        self.version = constants.UNISPHERE_VERSION

    def get_clone_target_storage_group_list(
            self, array_id, storage_group_id, target_storage_group=None,
            target_storage_group_volume_count=None, volume_pair_count=None,
            state=None, modified_tracks=None, src_protected_tracks=None,
            src_modified_tracks=None, background_copy=None,
            differential=None, precopy=None, vse=None):
        """Get Clone target storage group list.
        :param array_id The storage array ID -- string
        :param storage_group_id The Storage Group ID -- string
        :param target_storage_group Value that filters returned list to include
               target storage groups equal to or like the provided
               name -- string
        :param target_storage_group_volume_count Value that filters returned
               list to include target storage groups with the specified
               number of volumes -- string
        :param volume_pair_count Value that filters returned list to include
               target storage groups with the specified number of volume
               pairs -- string
        :param state Value that filters returned list to include target storage
               groups with pairs in the specified states -- array
        :param modified_tracks Value that filters returned list to include
               target storage groups with the specified modified
               tracks -- string
        :param src_protected_tracks Value that filters returned list to include
               target storage groups with the specified src protected tracks
               -- string
        :param src_modified_tracks Value that filters returned list to
               include target storage groups with the specified src modified
               tracks -- string
        :param background_copy Value that filters returned list to include
               target storage groups with background copy flag -- boolean
        :param differential Value that filters returned list to include target
               storage groups with differential flag -- boolean
        :param precopy Value that filters returned list to include target
               storage groups with the precopy flag -- boolean
        :param vse Value that filters returned list to include target storage
               groups with the vse -- boolean
        """
        query_params = {
            'target_storage_group': target_storage_group,
            'target_storage_group_volume_count':
                target_storage_group_volume_count,
            'volume_pair_count': volume_pair_count, 'state': state,
            'modified_tracks': modified_tracks,
            'src_protected_tracks': src_protected_tracks,
            'src_modified_tracks': src_modified_tracks,
            'background_copy': background_copy, 'differential': differential,
            'precopy': precopy,
            'vse': vse, }
        return self.common.get_request(
            target_uri=f"/{self.version}/replication/symmetrix/{array_id}/storagegroup/"
                       f"{storage_group_id}/clone/storagegroup",
            resource_type=None, params=query_params)

    def get_clone_pairs_List(self, array_id, storage_group_id):
        """Get Clone Pairs List.
        :param array_id The storage array ID -- string
        :param storage_group_id The Storage Group ID -- string
        """
        query_params = {}
        return self.common.get_request(
            target_uri=f"/{self.version}/replication/symmetrix"
                       f"/{array_id}/storagegroup/{storage_group_id}"
                       f"/clone/volume",
            resource_type=None, params=query_params)

    def get_clone_storage_group_pair_details(
            self, storage_group_id, array_id=None):
        """Get Clone storage group pair details.
        :param array_id The storage array ID -- string
        :param storage_group_id The Storage Group ID -- string
        :param target_storage_group_id The Target Storage Group ID -- string
        """
        query_params = {}
        array_id = array_id if array_id else self.array_id
        return self.common.get_request(
            target_uri=f"/{self.version}/replication/symmetrix/{array_id}/storagegroup/"
                       f"{storage_group_id}/clone/storagegroup/"
                       f"{target_storage_group_id}",
            resource_type=None, params=query_params)
    def create_clone(
            self, storage_group_id, target_storage_group_id,
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
        array_id = array_id if array_id else self.array_id
        payload = {
                    "target_storage_group_name": target_storage_group_id,
                    "establish_terminate": establish_terminate,
                    "consistent": consistent,
                    "force": force,
                    "star": star,
                    "skip": skip
                  }
        return self.common.create_resource(
           target_uri=f"/{self.version}/replication/symmetrix"
                      f"/{array_id}/storagegroup/{storage_group_id}"
                      f"/clone/storagegroup", payload=payload)
    def terminate_clone(self, storage_group_id, array_id=None,
                        target_storage_group_id=None,force=False,
                        symforce=False, star=False, skip=False,
                        not_ready=False, restored=None):
        """Terminate Clone Session.
        :param array_id: The storage array ID -- string
        :param storage_group_id: The Storage Group ID -- string
        :param target_storage_group_id: name of storage group to contain
                                          clone devices -- string
        :param force: Attempts to force the operation even though one or more
                      volumes may not be in the normal, expected state(s) for
                      the specified operation -- bool
        :param star: Acknowledge the volumes are in an SRDF/Star
                     configuration -- bool
        :param skip: Skips the source locks action -- bool
        :param not_ready: sets clone devices to not ready
                          after operation -- bool
        :param restored: removes the restore flag from clone session,
                         leaves clone session intact for incremental clone
                         operations.  Used following restore session -- bool
        """
        array_id = array_id if array_id else self.array_id
        params = {
                    "target_storage_group": target_storage_group_id,
                    "force": force,
                    "star": star,
                    "skip": skip,
                    "symforce": symforce,
                    "not_ready": not_ready,
                    "restored": restored
                  }
        return self.common.delete_resource(
            target_uri=(f"/{self.version}/replication/symmetrix"
                        f"/{array_id}/storagegroup/{storage_group_id}"
                        f"/clone/storagegroup"),
            params=params)
    def establish_clone(self, storage_group_id,
                        target_storage_group_id, array_id=None,
                        consistent=True,
                        not_ready=False, vse=False,
                        force=False, star=False, skip=False,
                        _async=False):
        """Perform establish against a clone storage group.
        :param storage_group_id: The Storage Group ID -- string
        :param target_storage_group_id: name of storage group to contain
                                          clone devices -- string
        :param array_id: The storage array ID -- string
        :param consistent: creates the clone crash consistent using ECA
                           technology -- bool
        :param not_ready: sets target storage group to not ready following 
                          establish operation -- bool
        :param vse: uses VSE close -- bool
        :param force: Attempts to force the operation even though one or more 
                      volumes may not be in the normal, expected state(s) for 
                      the specified operation -- bool
        :param star: Acknowledge the volumes are in an SRDF/Star
                     configuration -- bool
        :param skip: Skips the source locks action -- bool
        :param _async: if call should be async -- bool
        """
        array_id = array_id if array_id else self.array_id
        if _async:
            payload.update(ASYNC_UPDATE)
        payload ={
            'action': 'Establish',
            'establish': {
                'consistent': consistent,
                'not_ready': not_ready,
                'vse': vse,
                'force': force,
                'star': star,
                'skip': skip
            }}
        return self.common.modify_resource(
            target_uri=f"/{self.version}/replication/symmetrix/{array_id}/storagegroup/"
                       f"{storage_group_id}/clone/storagegroup/"
                       f"{target_storage_group_id}",
            resource_type=None, payload=payload)

    def split_clone(
            self, storage_group_id, target_storage_group_id, array_id=None,
            star=False, skip=False, force=False, _async=False):
        """Perform split actions against a clone storage group that is in
        the restored state.
        :param storage_group_id: The Storage Group ID -- string
        :param target_storage_group_id:The Storage Group ID of Target
               storage group -- string
        :param star: Acknowledge the volumes are in an SRDF/Star
                     configuration -- bool
        :param skip: Skips the source locks action -- bool
        :param force: Attempts to force the operation even though one or more 
                      volumes may not be in the normal, expected state(s) for 
                      the specified operation -- bool
        :param array_id: The storage array ID -- string
        :param _async: if call should be async -- bool
        """
        if _async:
            payload.update(ASYNC_UPDATE)

        array_id = array_id if array_id else self.array_id
        if _async:
            payload.update(ASYNC_UPDATE)
        payload = {
            'action': 'Split',
            'split': {
                'force': force,
                'star': star,
                'skip': skip
            }}
        return self.common.modify_resource(
            target_uri=f"/{self.version}/replication/symmetrix/{array_id}/storagegroup/"
                       f"{storage_group_id}/clone/storagegroup/"
                       f"{target_storage_group_id}",
            resource_type=None, payload=payload)

    def restore_clone(
            self, storage_group_id, target_storage_group_id, array_id=None,
            star=False, force=False, _async=False):
        """Perform split actions against a clone storage group that is in
        the restored state.
        :param storage_group_id: The Storage Group ID -- string
        :param target_storage_group_id:The Storage Group ID of Target
               storage group -- string
        :param array_id: The storage array ID -- string
        :param force: Attempts to force the operation even though one or more
                      volumes may not be in the normal, expected state(s) for
                      the specified operation -- bool
        :param star: Acknowledge the volumes are in an SRDF/Star
                     configuration -- bool
        :param _async: if call should be async -- bool
        """
        if _async:
            payload.update(ASYNC_UPDATE)

        array_id = array_id if array_id else self.array_id
        if _async:
            payload.update(ASYNC_UPDATE)
        payload = {
            'action': 'Restore',
            'restore': {
                'force': force,
                'star': star,
            }}
        return self.common.modify_resource(
            target_uri=f"/{self.version}/replication/symmetrix/{array_id}/storagegroup/"
                       f"{storage_group_id}/clone/storagegroup/"
                       f"{target_storage_group_id}",
            resource_type=None, payload=payload)

    def set_clone_copy_mode(self, storage_group_id, target_storage_group_id,
                            array_id=None, mode, force=False, _async=False):
        """Set copy mode on a clone storage group.
        :param storage_group_id: The Storage Group ID -- string
        :param target_storage_group_id:The Storage Group ID of Target
               storage group -- string
        :param array_id: The storage array ID -- string
        :param mode: set copy, no_copy or pre_copy mode on clone
                     session for storage group -- str
        :param _async: if call should be async -- bool
        """
        modes = {'COPY': 'copy', 'NOCOPY': 'no_copy', 'NO_COPY': 'no_copy',
                 'PRECOPY': 'pre_copy', 'PRE_COPY':'pre_copy'}
        try:
            mode = modes.get(mode.upper())
        except:
            print("please supply a valid copy mode, Valid Values are Copy, "
                  "no_copy, or pre_copy, mode value is not case sensitive.")
        array_id = array_id if array_id else self.array_id
        payload = {
            "action": "SetMode",
            "set_mode": {
                mode: 'true',
                'force': force}}
        if _async:
            payload.update(ASYNC_UPDATE)

        return self.common.modify_resource(
            target_uri=(f"/{self.version}/replication/symmetrix"
                        f"/{array_id}/storagegroup/"
                        f"{storage_group_id}/clone/storagegroup/"
                        f"{target_storage_group_id}"),
            resource_type=None)
