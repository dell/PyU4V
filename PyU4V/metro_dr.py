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
"""metro_dr.py."""

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


class MetroDRFunctions(object):
    """Metro DR Functions."""

    def __init__(self, array_id, rest_client):
        """__init__."""
        self.provisioning = ProvisioningFunctions(array_id, rest_client)
        self.common = CommonFunctions(rest_client)
        self.get_resource = self.common.get_resource
        self.create_resource = self.common.create_resource
        self.modify_resource = self.common.modify_resource
        self.delete_resource = self.common.delete_resource
        self.array_id = array_id

    def get_metrodr_environment_list(self, array_id=None):
        """Gets a list of metro dr environments.

        :param array_id: 12 Digit Serial Number of Array -- int
        :returns: list of metro dr environments --list
        """
        if not array_id:
            array_id = self.array_id
        response = self.get_resource(
            category=REPLICATION, resource_level=SYMMETRIX,
            resource_level_id=array_id, resource_type=METRO_DR)
        return response.get('names', list()) if response else list()

    def get_metrodr_environment_details(self, environment_name,
                                        array_id=None, config=True):
        """Get details for metro DR environment.

        :param environment_name: Unique name to identify Metro DR environment
                                 -- str
        :param array_id: 12 Digit Serial Number of Array -- int
        :param config: return full environment config details or
                       summary -- bool
        :returns: details of the metro dr environments -- dict
        """
        if not array_id:
            array_id = self.array_id
        response = self.get_resource(
            category=REPLICATION, resource_level=SYMMETRIX,
            resource_level_id=array_id, resource_type=METRO_DR,
            resource_type_id=environment_name, params={'config': config})

        return response

    def create_metrodr_environment(
            self, storage_group_name, environment_name, metro_r1_array_id,
            metro_r2_array_id, dr_array_id, dr_replication_mode,
            metro_r2_storage_group_name=None, dr_storage_group_name=None,
            force_new_metro_r1_dr_rdfg=True, force_new_metro_r2_dr_rdfg=True,
            _async=True):
        """Protects Non-SRDF Storage Group with Metro and DR legs.

        Note: This function is set to run as an Asynchronous job on the
        server by default as there is the potential for this task to take a
        few minutes. Storage Groups and SRDF groups are created
        automatically for the user end result is R2--SRDF/A--R11--Metro--R2.

        :param storage_group_name: name of storage group containing devices to
                                   be replicated in Metro DR environment -- str
        :param environment_name: name of Metro Dr Environment up to 16
                                 characters-- str
        :param metro_r1_array_id: 12 Digit Serial Number of R1 Array for
                                  SRDF Metro Source Array -- int
        :param metro_r2_array_id: 12 Digit Serial Number of SRDF Metro R2
                                  Array -- int
        :param dr_array_id: 12 Digit Serial Number of Disaster Recovery
                            Array, replication  -- int
        :param dr_replication_mode: Asynchronous or AdaptiveCopyDisk -- str
        :param metro_r2_storage_group_name: Name for R2 Storage Group of
                                            metro SRDF pairing, only used if R2
                                            group naming is required to be
                                            different from source - str
        :param dr_storage_group_name: Name for Storage Group at DR,
                                      only used if group naming is required
                                      to be different from source - str
        :param force_new_metro_r1_dr_rdfg: whether or not to create a new RDFG
                                           to be created for Metro R1 array
                                           to DR array, or will autoselect
                                           from existing -- bool
        :param force_new_metro_r2_dr_rdfg: whether or not to create a new RDFG
                                           to be created for Metro R2 array
                                           to DR array, or will autoselect
                                           from existing -- bool
        :param _async: if call should be executed asynchronously or
                       synchronously  -- bool
        :returns: details of newly created metro dr environment-- dict
        """
        if not dr_storage_group_name:
            dr_storage_group_name = storage_group_name
        if not metro_r2_storage_group_name:
            metro_r2_storage_group_name = storage_group_name

        if dr_replication_mode:
            if 'ASYNCHRONOUS' in dr_replication_mode.upper():
                dr_replication_mode = ASYNCHRONOUS
            elif 'ADAPTIVECOPY' in dr_replication_mode.upper():
                dr_replication_mode = ADAPTIVE_COPY
            else:
                msg = (
                    'DR Replication Mode must be either Asynchronous or '
                    'AdaptiveCopyDisk')
                LOG.exception(msg)
                raise exception.InvalidInputException(message=msg)

        payload = {
            'action': 'CreateEnvironment',
            'create_environment_param': {
                'storage_group_name': storage_group_name,
                'environment_name': environment_name,
                'metro_r2_array_id': metro_r2_array_id,
                'metro_r2_storage_group_name': metro_r2_storage_group_name,
                'dr_array_id': dr_array_id,
                'force_new_metro_r1_dr_rdfg': force_new_metro_r1_dr_rdfg,
                'force_new_metro_r2_dr_rdfg': force_new_metro_r2_dr_rdfg,
                'dr_replication_mode': dr_replication_mode,
                'dr_storage_group_name': dr_storage_group_name,
                'metro_establish': True,
                'dr_establish': True}}
        if _async:
            payload.update(ASYNC_UPDATE)

        response = self.create_resource(
            category=REPLICATION, resource_level=SYMMETRIX,
            resource_level_id=metro_r1_array_id,
            resource_type=METRO_DR, payload=payload)
        return response

    def convert_to_metrodr_environment(
            self, storage_group_name, environment_name,
            metro_r1_array_id=None, metro_r2_dr_rdfg=None, _async=True):
        """Converts existing R2--Async--R11--Metro--R2 to Metro DR Environment.

        Automatically adds recovery RDFG between Metro R2 and Async R2.

        :param storage_group_name: storage group name containing source
                                   devices -- str
        :param environment_name: name of Metro Dr Environment up to 16
                                 characters -- str
        :param metro_r1_array_id: 12 Digit Serial Number of R1 Array for
                                  SRDF Metro Source Array, optional -- int
        :param metro_r2_dr_rdfg: DR SRDF group that should be used to pair
                                 Metro R2 volumes with DR volumes,
                                 optional -- int
        :param _async: if call should be executed asynchronously or
                       synchronously  -- bool
        :returns: details of newly created metro dr environment -- dict
        """
        if metro_r1_array_id:
            array_id = metro_r1_array_id
        else:
            array_id = self.array_id
        payload = {
            'action': 'ConvertToMetroDR',
            'convert_to_metrodr_param': {
                'storage_group_name': storage_group_name,
                'environment_name': environment_name}}
        if metro_r2_dr_rdfg:
            payload['convert_to_metrodr_param'][
                'metro_r2_dr_rdfg'] = metro_r2_dr_rdfg
        if _async:
            payload.update(ASYNC_UPDATE)

        response = self.create_resource(
            category=REPLICATION, resource_level=SYMMETRIX,
            resource_level_id=array_id, resource_type=METRO_DR,
            payload=payload)
        return response

    def delete_metrodr_environment(
            self, environment_name, remove_r1_dr_rdfg=False, force=False,
            metro_r1_array_id=None):
        """Deletes Metro DR Environment.

        SRDF replication will remain in place for Metro and SRDF/A
        configuration, be default this function simply removes the standby
        SRDF group for Metro DR environment on R2 site. If you intend to
        remove SRDF replication completely, suspend and delete SRDF
        pairings using suspend_storage_group_srdf and
        suspend_storage_group_srdf functions.

        :param environment_name: name of Metro Dr Environment up to 16
                                 characters-- str
        :param remove_r1_dr_rdfg: override default behavior and delete R11-R2
                                  RDFG from metro R1 side -- bool
        :param force: required True if deleting R1 DR group -- bool
        :param metro_r1_array_id: 12 Digit Serial of Metro R1 source
                                  array -- str
        """
        if metro_r1_array_id:
            array_id = metro_r1_array_id
        else:
            array_id = self.array_id

        self.delete_resource(
            category=REPLICATION, resource_level=SYMMETRIX,
            resource_level_id=array_id, resource_type=METRO_DR,
            resource_type_id=environment_name, params={
                'remove_r1_dr_rdfg': remove_r1_dr_rdfg, 'force': force})

    def modify_metrodr_environment(
            self, environment_name, action, metro=False,
            dr=False, keep_r2=False, force=False, symforce=False,
            _async=False, dr_replication_mode=None, reverse=False):
        """Performs Functions to modify state of MetroDR environment.

        :param environment_name: name of Metro Dr Environment up to 16
                                 characters-- str
        :param action: action to be performed on Environment, Establish,
                       Failover, Failback, Restore, SetMode, Split, UpdateR1
                       --str
        :param metro: directs action towards R11--R21 Metro Device leg of
                      Metro DR environment -- bool
        :param dr: directs action towards Device Pairs on Disaster
                   Recovery leg of Metro DR environment -- bool
        :param keep_r2: Used with Suspend Option, Ensures that the R2 data
                        on Metro remains available to host -- bool
        :param force: forces operation to complete, used with caution, not
                      recommended as part of fully automated workflow --bool
        :param symforce: forces operation to complete, used with caution,
                         requires ALLOW_SRDF_SYMFORCE parameter to be set in
                         solutions enabler options file, default is not
                         enabled,not recommended as part of fully automated
                         workflow  -- bool
        :param _async: if call should be executed asynchronously or
                       synchronously  -- bool
        :param dr_replication_mode: set mode of DR link, AdaptiveCopyDisk or
                                    Asynchronous -- str
        :param reverse: reverse the direction of the link -- bool
        :returns: details of metro dr environment and state -- dict
        """
        metro_dr_action = constants.METRO_DR_ACTIONS.get(action.upper())
        if metro_dr_action:
            payload = {'action': metro_dr_action}
        else:
            msg = (
                'SRDF Action must be one of [Establish, Split, Suspend, '
                'Recover, Restore, Resume, Failover, Failback, Update_R1, '
                'SetMode]')
            LOG.exception(msg)
            raise exception.VolumeBackendAPIException(data=msg)
        action_params = constants.METRO_DR_ACTION_PARAMS.get(
            metro_dr_action.upper())
        if metro_dr_action == 'Suspend':
            payload.update({
                action_params: {
                    'metro': metro,
                    'force': force,
                    'keep_r2': keep_r2,
                    'dr': dr,
                    'symforce': symforce}})
        elif metro_dr_action in ['Failover', 'Failback', 'Split', 'UpdateR1']:
            payload.update({
                action_params: {
                    'force': force,
                    'symforce': symforce}})
        elif metro_dr_action in ['Establish', 'Restore']:
            if (metro and dr) and metro_dr_action == 'Restore':
                msg = (
                    'Restore Operation can only be performed on a single '
                    'SRDF leg, please choice either Metro or DR not both')
                LOG.exception(msg)
                raise exception.InvalidInputException(message=msg)
            if metro and not dr and metro_dr_action == 'Establish':
                payload.update({action_params: {
                    'metro': metro, 'force': force, 'dr': dr,
                    'symforce': symforce, 'reverse': reverse}})
            else:
                payload.update({action_params: {
                    'metro': metro, 'force': force, 'dr': dr,
                    'symforce': symforce}})
        elif metro_dr_action == 'SetMode':
            payload.update({
                action_params: {
                    "mode": dr_replication_mode,
                    "force": force,
                    "symforce": symforce}})
        if _async:
            payload.update(ASYNC_UPDATE)
        return self.modify_resource(
            category=REPLICATION, resource_level=SYMMETRIX,
            resource_level_id=self.array_id, resource_type=METRO_DR,
            resource_type_id=environment_name, payload=payload)
