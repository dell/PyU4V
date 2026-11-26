# Copyright (c) 2026 Dell Inc. or its subsidiaries.
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
"""srdf.py."""

import logging
from typing import Any

from PyU4V.common import CommonFunctions
from PyU4V.provisioning import ProvisioningFunctions
from PyU4V.utils import constants
from PyU4V.utils import exception

LOG = logging.getLogger(__name__)

# SRDF action constants
ESTABLISH = constants.ESTABLISH
FAILBACK = constants.FAILBACK
FAILOVER = constants.FAILOVER
RESTORE = constants.RESTORE
RESUME = constants.RESUME
SETBIAS = constants.SETBIAS
SETMODE = constants.SETMODE
ENABLECONSISTENCY = constants.ENABLECONSISTENCY
DISABLECONSISTENCY = constants.DISABLECONSISTENCY
SPLIT = constants.SPLIT
SUSPEND = constants.SUSPEND
SWAP = constants.SWAP

# Resource constants
ASYNC_UPDATE = constants.ASYNC_UPDATE
REPLICATION = constants.REPLICATION
SYMMETRIX = constants.SYMMETRIX
STORAGEGROUP = constants.STORAGEGROUP
RDFG = constants.RDFG
VOLUME = constants.VOLUME
RDF_DIRECTOR = constants.RDF_DIRECTOR
PORT = constants.PORT
REMOTE_PORT = constants.REMOTE_PORT
RDF_GROUP = constants.RDF_GROUP


class SRDFFunctions(object):
    """SRDFFunctions."""

    def __init__(self, array_id: str, rest_client: Any) -> None:
        """__init__."""
        self.provisioning = ProvisioningFunctions(array_id, rest_client)
        self.common = CommonFunctions(rest_client)
        self.array_id = array_id

    def get_rdf_group(self, rdf_number: int, array_id: str | None = None) -> dict[str, Any]:
        """Get specific rdf group details.

        :param rdf_number: rdf group number -- int
        :param array_id: array serial number -- str
        :returns: rdf group details -- dict
        """
        array_id = self.array_id if not array_id else array_id
        return self.common.get_request(
            target_uri=f"/{self.common.UNI_VERSION}/replication"
            f"/symmetrix/{array_id}/rdf_group/{rdf_number}",
            resource_type=None)

    def get_rdf_group_list(self, array_id: str | None = None, remote_symmetrix_id: str | None = None,
                           rdf_mode: str | None = None, volume_count: int | None = None, group_type: str | None = None) -> list[dict[str, Any]]:
        """Get rdf group list from array.

        :param array_id: local array serial number -- str
        :param remote_symmetrix_id: Optional value that filters returned list
                                    to display only SRDF Groups between the
                                    local array and specified remote
                                    array, 12 Digit array_id
                                    e.g. 000297900330  -- str
        :param rdf_mode: Optional value that filters returned list to display
                         only SRDF Groups of a specified RDF mode,
                         Synchronous, Asynchronous, Active, or AdaptiveCopy
                         -- str
        :param volume_count: Optional value that filters returned list to
                             display only SRDF Groups that have a specified
                             volume count -- int
        :param group_type: 	Optional value that filters returned list to
                            display only SRDF Groups of a specified group type
                            valid options are Witness, Global_Mirror,
                            Data_Migration, VVOL_ASYNC, MetroDR_Metro,
                            MetroDR_DR, Metro, Star_Normal,
                            Star_Recovery, Sqar_Normal, Sqar_Recovery,
                            PPRC, FILE_SYNC, FILE_ASYNC, Dynamic -- str
        :returns: rdf group list -- list
        """
        filters = {'remote_symmetrix_id': remote_symmetrix_id,
                   'rdf_mode': rdf_mode,
                   'volume_count': volume_count,
                   'group_type': group_type}
        array_id = self.array_id if not array_id else array_id
        response = self.common.get_request(
            target_uri=f"/{self.common.UNI_VERSION}/replication"
            f"/symmetrix/{array_id}/rdf_group",
            resource_type=None, params=filters)
        return response.get('rdfGroupID', list()) if response else list()

    def get_rdf_group_volume(self, rdf_number, device_id):
        """Get specific volume details, from an RDF group.

        :param rdf_number: rdf group number -- int
        :param device_id: device id -- str
        :returns: rdf group volume details -- dict
        """
        return self.common.get_request(
            target_uri=f"/{self.common.UNI_VERSION}/replication"
            f"/symmetrix/{self.array_id}/rdf_group"
            f"/{rdf_number}/volume/{device_id}",
            resource_type=None)

    def get_rdf_group_volume_list(self, rdf_number):
        """Get specific volume details, from an RDF group.

        :param rdf_number: rdf group number -- int
        :returns: device ids -- list
        """
        response = self.common.get_request(
            target_uri=f"/{self.common.UNI_VERSION}/replication"
            f"/symmetrix/{self.array_id}/rdf_group"
            f"/{rdf_number}/volume",
            resource_type=None)
        return response.get('name', list()) if response else list()

    def are_volumes_rdf_paired(self, remote_array, device_id,
                               target_device, rdf_group):
        """Check if a pair of volumes are RDF paired.

        :param remote_array: remote array serial number -- str
        :param device_id: device id -- str
        :param target_device: target device id -- str
        :param rdf_group: rdf group number -- int
        :returns: paired, state -- bool, string
        """
        paired, local_vol_state, rdf_pair_state = False, '', ''
        volume = self.get_rdf_group_volume(rdf_group, device_id)
        if volume:
            remote_volume = volume['remoteVolumeName']
            remote_symm = volume['remoteSymmetrixId']
            if (remote_volume == target_device and (
                    remote_array == remote_symm)):
                paired = True
                local_vol_state = volume['localVolumeState']
                rdf_pair_state = volume['rdfpairState']
        else:
            LOG.warning('Cannot find source RDF volume {vol}.'.format(
                vol=device_id))
        return paired, local_vol_state, rdf_pair_state

    def get_rdf_group_number(self, rdf_group_label):
        """Given a group label, return the associated group number.

        :param rdf_group_label: rdf group label -- str
        :returns: rdf group number -- int
        """
        number = None
        rdf_list = self.get_rdf_group_list()
        if rdf_list:
            number = ([rdf['rdfgNumber'] for rdf in rdf_list
                       if rdf['label'] == rdf_group_label][0])
        if number:
            rdf_group = self.get_rdf_group(number)
            if not rdf_group:
                number = None
        return number

    def get_storage_group_srdf_group_list(self, storage_group_id,
                                          array_id=None):
        """Get the rdf group numbers for a storage group.

        :param storage_group_id: replicated storage group id -- str
        :param array_id: array serial number -- str
        :returns: rdf group numbers -- list
        """
        array_id = self.array_id if not array_id else array_id
        response = self.common.get_request(
            target_uri=f"/{self.common.UNI_VERSION}/replication"
            f"/symmetrix/{array_id}/storagegroup"
            f"/{storage_group_id}/rdf_group",
            resource_type=None)
        return response.get('rdfgs', list()) if response else list()

    def get_storage_group_srdf_details(self, storage_group_id, rdfg_num):
        """Get the details for an rdf group on a particular storage group.

        :param storage_group_id: replicated storage group id -- str
        :param rdfg_num: rdf group number -- int
        :returns: storage group rdf details -- dict
        """
        return self.common.get_request(
            target_uri=f"/{self.common.UNI_VERSION}/replication"
            f"/symmetrix/{self.array_id}/storagegroup"
            f"/{storage_group_id}/rdf_group/{rdfg_num}",
            resource_type=None)

    def create_storage_group_srdf_pairings(
            self, storage_group_id, remote_sid, srdf_mode, establish=None,
            _async=False, rdfg_number=None, force_new_rdf_group=False,
            remote_storage_group_id=None):
        """SRDF protect a storage group.

        Valid modes are 'Active', 'AdaptiveCopyDisk', 'Synchronous', and
        'Asynchronous'.

        :param storage_group_id: storage group id -- str
        :param remote_sid: remote array id -- str
        :param srdf_mode: replication mode -- str
        :param establish: establish srdf -- bool
        :param _async: if call should be async -- bool
        :param rdfg_number: rdf group number -- int
        :param force_new_rdf_group: ignored, present for backward
                                    compatibility -- bool
        :param remote_storage_group_id: remote storage group id, offers
                                        flexibiliity to have remote storage
                                        group name different from local -- str
        :returns: storage group rdf details -- dict
        """
        establish_sg = 'True' if establish else 'False'
        rdf_payload = {'replicationMode': srdf_mode,
                       'remoteSymmId': remote_sid,
                       'remoteStorageGroupName': (
                           remote_storage_group_id or storage_group_id),
                       'establish': establish_sg}
        if rdfg_number is not None:
            rdf_payload['rdfgNumber'] = rdfg_number
        if _async:
            rdf_payload.update(ASYNC_UPDATE)
        if force_new_rdf_group:
            LOG.warning("Parameter 'force_new_rdf_group' is no longer "
                        "supported and will be ignored.")
        return self.common.create_resource(
            target_uri=f"/{self.common.UNI_VERSION}/replication"
            f"/symmetrix/{self.array_id}/storagegroup"
            f"/{storage_group_id}/rdf_group",
            payload=rdf_payload)

    def modify_storage_group_srdf(
            self, storage_group_id, action, srdf_group_number, options=None,
            _async=False):
        """Modify the state of a rdf group.

        This may be a long running task depending on the size of the SRDF
        group, can switch to async call if required. Available actions are
        'Establish', 'EnableConsistency', 'DisableConsistency', 'Split',
        'Suspend', 'Restore', 'Resume', 'Failover', 'Failback', 'Swap',
        'SetBias', and 'SetMode'.

        :param storage_group_id: storage group id -- str
        :param action: the rdf action, note enable/disable consistency
                       feature requires Unisphere 9.2.1.6 or higher -- str
        :param srdf_group_number: srdf group number -- int
        :param options: srdf options e.g.
                        {setMode': {'mode': 'Asynchronous'}} -- dict
        :param _async: if call should be async -- bool
        :returns: storage group rdf details -- dict
        """
        srdf_actions = {
            'ESTABLISH': ESTABLISH, 'SPLIT': SPLIT, 'SUSPEND': SUSPEND,
            'RESTORE': RESTORE, 'RESUME': RESUME, 'FAILOVER': FAILOVER,
            'FAILBACK': FAILBACK, 'SWAP': SWAP, 'SETBIAS': SETBIAS,
            'SETMODE': SETMODE, 'DISABLECONSISTENCY': DISABLECONSISTENCY,
            'ENABLECONSISTENCY': ENABLECONSISTENCY}
        srdf_action = srdf_actions.get(action.upper())

        if srdf_action:
            payload = {'action': srdf_action}
        else:
            msg = ('SRDF Action must be one of [Establish, Split, Suspend, '
                   'Restore, Resume, Failover, Failback, Swap, SetBias, '
                   'SetMode]')
            LOG.exception(msg)
            raise exception.VolumeBackendAPIException(data=msg)
        if _async:
            payload.update(ASYNC_UPDATE)
        if options and action:
            payload.update(options)
        return self.common.modify_resource(
            target_uri=f"/{self.common.UNI_VERSION}/replication"
            f"/symmetrix/{self.array_id}/storagegroup"
            f"/{storage_group_id}/rdf_group"
            f"/{srdf_group_number}",
            resource_type=None, payload=payload)

    def suspend_storage_group_srdf(self, storage_group_id, srdf_group_number,
                                   suspend_options=None, _async=False):
        """Suspend IO on the links for the given storage group.

        Optional boolean parameters to set are "bypass", "metroBias", "star",
        "immediate", "hop2", "consExempt", "force", "symForce".

        :param storage_group_id: storage group id -- str
        :param srdf_group_number: srdf group number -- int
        :param suspend_options: suspend parameters -- dict
        :param _async: if call should be async -- bool
        :returns: storage group rdf details -- dict
        """
        return self.modify_storage_group_srdf(
            storage_group_id, 'suspend', srdf_group_number,
            options=suspend_options, _async=_async)

    def establish_storage_group_srdf(
            self, storage_group_id, srdf_group_number,
            establish_options=None, _async=False):
        """Establish io on the links for the given storage group.

        Optional boolean parameters to set are 'bypass', 'metroBias', 'star',
        'hop2', 'force', 'symForce', 'full'.

        :param storage_group_id: storage group id -- str
        :param srdf_group_number: srdf group number -- int
        :param establish_options: establish parameters -- dict
        :param _async: if call should be async -- bool
        :returns: storage group rdf details -- dict
        """
        return self.modify_storage_group_srdf(
            storage_group_id, 'establish', srdf_group_number,
            options=establish_options, _async=_async)

    def failover_storage_group_srdf(
            self, storage_group_id, srdf_group_number,
            failover_options=None, _async=False):
        """Failover a given storage group.

        Optional boolean parameters to set are 'bypass', 'star', 'restore',
        'immediate', 'hop2', 'force', 'symForce', 'remote', 'establish'.

        :param storage_group_id: storage group id -- str
        :param srdf_group_number: srdf group number -- int
        :param failover_options: failover parameters -- dict
        :param _async: if call should be async -- bool
        :returns: storage group rdf details -- dict
        """
        return self.modify_storage_group_srdf(
            storage_group_id, 'failover', srdf_group_number,
            options=failover_options, _async=_async)

    def failback_storage_group_srdf(
            self, storage_group_id, srdf_group_number, failback_options=None,
            _async=False):
        """Failback a given storage group.

        Optional boolean parameters to set are 'bypass', 'recoverPoint',
        'star', 'hop2', 'force', 'symForce', 'remote'.

        :param storage_group_id: storage group id -- str
        :param srdf_group_number: srdf group number -- int
        :param failback_options: failback parameters -- dict
        :param _async: if call should be async -- bool
        :returns: storage group rdf details -- dict
        """
        return self.modify_storage_group_srdf(
            storage_group_id, 'failback', srdf_group_number,
            options=failback_options, _async=_async)

    def delete_storage_group_srdf(
            self, storage_group_id, srdf_group_number, filters=None):
        """Delete srdf pairings for a given storage group.

        :param storage_group_id: storage group id -- str
        :param srdf_group_number: srdf group number -- int
        :param filters: optional boolean filters, half_delete,hop2, force,
                        symforce, star, bypass, keepR1, keepR2,
                        usage example filters={'keepR1': 'true'} -- dict
        :returns: storage group rdf details -- dict
        """
        if srdf_group_number:
            self.common.delete_resource(
                target_uri=f"/{self.common.UNI_VERSION}/replication"
                f"/symmetrix/{self.array_id}/storagegroup"
                f"/{storage_group_id}/rdf_group"
                f"/{srdf_group_number}",
                params=filters)

    def get_rdf_director_list(self, array_id=None, filters=None):
        """Finds out directors configured for SRDF on the specified array.

        :param array_id: 12 digit serial number for PowerMax array -- str
        :param filters: optional filters - dict
        :returns: list of directors -- list
        """
        if not array_id:
            array_id = self.array_id
        try:
            response = self.common.get_request(
                target_uri=f"/{self.common.UNI_VERSION}/replication"
                f"/symmetrix/{array_id}/rdf_director",
                resource_type=None, params=filters)
        except exception.ResourceNotFoundException:
            return list()
        director_list = (
            response.get('directorId', list()) if response else list())
        return director_list

    def get_rdf_director_detail(self, director_id, array_id=None):
        """Retrieves details for specified RDF_director.

        :param director_id: identifier for director e.g. RF-1F -- str
        :param array_id: 12 digit serial number for PowerMax array -- str
        :returns: director details --dict
        """
        if not array_id:
            array_id = self.array_id
        return self.common.get_request(
            target_uri=f"/{self.common.UNI_VERSION}/replication"
            f"/symmetrix/{array_id}/rdf_director"
            f"/{director_id}",
            resource_type=None)

    def get_rdf_director_port_list(self, director_id, array_id=None,
                                   filters=None):
        """Retrieves list of ports available on RDF_director.

        :param director_id: identifier for director e.g. RF-1F -- str
        :param array_id: 12 digit serial number for PowerMax array -- str
        :param filters: optional filters -- dict
        :returns: list of RDF ports -- list
        """
        if not array_id:
            array_id = self.array_id
        response = self.common.get_request(
            target_uri=f"/{self.common.UNI_VERSION}/replication"
            f"/symmetrix/{array_id}/rdf_director"
            f"/{director_id}/port",
            resource_type=None, params=filters)
        port_list = (
            response.get('portNumber', list()) if response else list())
        return port_list

    def get_rdf_director_port_details(self, director_id, port_id,
                                      array_id=None):
        """Retrieves details of specified RDF ports.

        :param director_id: identifier for director e.g. RF-1F -- str
        :param port_id: port number -- int
        :param array_id: 12 digit serial number for  PowerMax array -- str
        :returns: port details -- dict
        """
        if not array_id:
            array_id = self.array_id
        return self.common.get_request(
            target_uri=f"/{self.common.UNI_VERSION}/replication"
            f"/symmetrix/{array_id}/rdf_director"
            f"/{director_id}/port/{port_id}",
            resource_type=None)

    def get_rdf_port_remote_connections(self, director_id, port_id,
                                        array_id=None):
        """Performs a scan of the RDF environment via specified port.

        This function should be run on initial SRDF configuration once zoning
        or IP routing is configured, prior to first RDF group being configured.

        :param director_id: identifier for director e.g. RF-1F -- str
        :param port_id: port number -- int
        :param array_id: 12 digit serial number for Source  -- str
        :returns: remote port details -- dict
        """

        if not array_id:
            array_id = self.array_id
        return self.common.get_request(
            target_uri=f"/{self.common.UNI_VERSION}/replication"
            f"/symmetrix/{array_id}/rdf_director"
            f"/{director_id}/port/{port_id}/remote_port",
            resource_type=None)

    def create_rdf_group(self, local_director_port_list, remote_array_id,
                         label, local_rdfg_number, remote_rdfg_number,
                         remote_director_port_list, array_id=None):
        """Create a new RDF group between directors and ports on two PowerMax.

        If this is the first connection between 2 arrays please ensure that you
        run get_rdf_remote_port_details and create the initial connection
        group using only the first source port you can extract details for one
        or more remote ports for the desired target array and feed into this
        function. Additional Ports can be added with modify_rdf_group function.

        :param local_director_port_list: list of local directors and ports for
                                         group e.g [RF-1E:1, RF-2E:1] -- list
        :param remote_array_id: 12 digit serial number of remote array  -- str
        :param label: label for group up to 10 characters -- str
        :param local_rdfg_number: rdfg for the local array -- int
        :param remote_rdfg_number: rdfg for the remote array -- int
        :param remote_director_port_list: list of remote directors and ports
                                          to group e.g [RF-1E:1, RF-2E:1]
                                          -- list
        :param array_id: 12 digit serial number of Source (R1) array,
                         if no array is specified the array in config file or
                         api connection will be default -- str
        """
        if not array_id:
            array_id = self.array_id
        local_ports = list()
        remote_ports = list()
        for port in local_director_port_list:
            dir_id = port.split(':')[0]
            port_no = port.split(':')[1]
            local_ports.append({'symmetrixID': array_id,
                                'directorId': dir_id,
                                'portNumber': port_no})
        for port in remote_director_port_list:
            dir_id = port.split(':')[0]
            port_no = port.split(':')[1]
            remote_ports.append({'symmetrixID': remote_array_id,
                                 'directorId': dir_id, 'portNumber': port_no})

        payload = {
            'local_ports': local_ports,
            'remote_rdfg_number': remote_rdfg_number,
            'remote_ports': remote_ports,
            'label': label,
            'local_rdfg_number': local_rdfg_number}

        self.common.create_resource(
            target_uri=f"/{self.common.UNI_VERSION}/replication"
            f"/symmetrix/{array_id}/rdf_group",
            payload=payload)

    def modify_rdf_group(self, action, srdf_group_number, array_id=None,
                         port_list=None, label=None, dev_list=None,
                         target_rdf_group=None, consistency_exempt=None,
                         keepR1=None, keepR2=None):
        """Function to Modify Ports, devices or change label of RDF group.

        Function can be used to Add ports, move volumes between rdf groups,
        remove ports or rename RDF group.

        :param action: add_ports, remove_ports, move -- str
        :param srdf_group_number: srdf group number
                                  for action on local array: int
        :param array_id: 12 digit serial of array -- str
        :param port_list: list of ports to be added or removed e.g.
                          [RF-1E:10, RF-2E:10] --list
        :param label: label for group up to 10 characters -- str
        :param dev_list: list of volumes to be moved between RDF groups -- list
        :param target_rdf_group: rdfg group to move volumes to -- int
        :param consistency_exempt: ignore device for consistency checks -- bool
        :param keepR1: preserves data on R1 -- bool
        :param keepR2: preserves data on R2 -- bool
        """

        rdfg_action = constants.RDFG_ACTIONS.get(action.upper())
        payload = dict()

        if not rdfg_action:
            msg = ('RDFG Action must be one [add_ports, remove_ports, move, '
                   'set_label]')
            LOG.exception(msg)
            raise exception.VolumeBackendAPIException(data=msg)
        if not array_id:
            array_id = self.array_id
        if rdfg_action == 'Move':
            if not consistency_exempt:
                consistency_exempt = False
            payload = {
                'move': {
                    'targetRdfGroup': target_rdf_group,
                    'volumesToMove': dev_list,
                    'exempt': consistency_exempt},
                'action': 'Move'}
            if keepR1 is not None:
                payload['move']['keepR1'] = keepR1
            if keepR2 is not None:
                payload['move']['keepR2'] = keepR2

        elif rdfg_action == 'set_label':
            payload = {
                "set_label": {
                    "label": label},
                "action": "set_label"}

        elif rdfg_action in ['add_ports', 'remove_ports']:
            if not port_list:
                msg = ('list of ports must be supplied when adding or '
                       'removing ports from RDFG e.g. [RF-1E:10, RF-2E:10]')
                LOG.exception(msg)
                raise exception.InvalidInputException(data=msg)
            port_payload = list()
            for port in port_list:
                dir_id, port_no = port.split(':')
                port_payload.append(
                    {'symmetrixID': array_id,
                     'directorId': dir_id,
                     'portNumber': port_no})
                payload = {'action': rdfg_action,
                           rdfg_action: {
                               'ports': port_payload}}

        self.common.modify_resource(
            target_uri=f"/{self.common.UNI_VERSION}/replication"
            f"/symmetrix/{array_id}/rdf_group"
            f"/{srdf_group_number}",
            resource_type=None, payload=payload)

    def delete_rdf_group(self, srdf_group_number, array_id=None):
        """Function to Delete SRDF groups between VMAX or PowerMax arrays.

        :param srdf_group_number: number of RDF group to be deleted -- int
        :param array_id: 12 digit serial of array -- str
        """

        if not array_id:
            array_id = self.array_id

        self.common.delete_resource(
            target_uri=f"/{self.common.UNI_VERSION}/replication"
            f"/symmetrix/{array_id}/rdf_group"
            f"/{srdf_group_number}")

    def create_storage_group_from_rdfg(
            self, storage_group_name, srdf_group_number, array_id=None,
            rdf_type=None, remote_storage_group_name=None):
        """Creates management storage group from all devices in SRDF group.

        Note SRDF management storage group will be created without a service
        level, it is assumed that this group is created solely for the purpose
        of managing SRDF device and replication state, devices in an SRDF
        group may span multiple applications and storage groups.

        :param storage_group_name: Name of storage group -- str
        :param srdf_group_number: number of RDF group volumes are in -- int
        :param array_id: number of RDF group volumes are in -- int
        :param rdf_type: The SRDF type of the volumes in the SRDF group to be
                         added to the Storage Group. Only needs to be populated
                         if the SRDF group contains both RDF1 and RDF2 volumes
                         valid values RDF1 or RDF2 -- str
        :param remote_storage_group_name: Name of remote storage group -- str
        """
        if not array_id:
            array_id = self.array_id

        create_sg_payload = {
            'rdf_group_number': srdf_group_number}
        payload = {
            'create_sg_from_rdfg': create_sg_payload,
            'storage_group_name': storage_group_name,
            'action': 'CreateSgFromRdfg'}
        if rdf_type:
            create_sg_payload.update({'rdf_type': rdf_type})
        if remote_storage_group_name:
            create_sg_payload.update(
                {'remote_storage_group_name': remote_storage_group_name})

        self.common.create_resource(
            target_uri=f"/{self.common.UNI_VERSION}/replication"
            f"/symmetrix/{array_id}/storagegroup",
            payload=payload)
