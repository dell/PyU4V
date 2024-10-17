# Copyright (c) 2019 Dell Inc. or its subsidiaries.
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
"""provisioning.py."""

import logging
import math
import random
import re

from PyU4V.common import CommonFunctions
from PyU4V.utils import constants
from PyU4V.utils import decorators
from PyU4V.utils import exception
from PyU4V.utils import file_handler
from PyU4V.utils import utils

LOG = logging.getLogger(__name__)

# Resource constants
SLOPROVISIONING = constants.SLOPROVISIONING
CREATE_VOL_STRING = constants.CREATE_VOL_STRING
ASYNC_UPDATE = constants.ASYNC_UPDATE
SYSTEM = constants.SYSTEM
SYMMETRIX = constants.SYMMETRIX
DIRECTOR = constants.DIRECTOR
PORT = constants.PORT
HOST = constants.HOST
HOSTGROUP = constants.HOSTGROUP
INITIATOR = constants.INITIATOR
MAINFRAME = constants.MAINFRAME
MASKINGVIEW = constants.MASKINGVIEW
CONNECTIONS = constants.CONNECTIONS
PORTGROUP = constants.PORTGROUP
SLO = constants.SLO
SRP = constants.SRP
COMPRESSIBILITY_REPORT = constants.COMPRESSIBILITY_REPORT
STORAGEGROUP = constants.STORAGEGROUP
SG_DEMAND_REPORT = constants.SG_DEMAND_REPORT
VOLUME = constants.VOLUME
WORKLOADTYPE = constants.WORKLOADTYPE
PORT_STRUCTURE = constants.PORT_STRUCTURE
FICON_SPLIT = constants.FICON_SPLIT
CU_IMAGE = constants.CU_IMAGE


class ProvisioningFunctions(object):
    """ProvisioningFunctions."""

    def __init__(self, array_id, rest_client):
        """__init__."""
        self.array_id = array_id
        self.common = CommonFunctions(rest_client)
        self.get_resource = self.common.get_resource
        self.create_resource = self.common.create_resource
        self.modify_resource = self.common.modify_resource
        self.delete_resource = self.common.delete_resource
        self.version = constants.UNISPHERE_VERSION

    def get_array(self, array_id=None):
        """Query for details of an array from SLOPROVISIONING endpoint.

        :param array_id: array serial number -- str
        :returns: array details -- dict
        """
        array_id = array_id if array_id else self.array_id
        response = self.get_resource(
            category=SLOPROVISIONING, resource_level=SYMMETRIX,
            resource_level_id=array_id)
        return response if response else dict()

    def get_host(self, host_id):
        """Get details on a host on the array.

        :param host_id: the name of the host -- str
        :returns: host details -- dict
        """
        return self.get_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=HOST, resource_type_id=host_id)

    def get_host_list(self, filters=None):
        """Get list of the hosts on the array.

        See documentation for applicable filters.

        :param filters: optional list of filters -- dict
        :returns: hosts -- list
        """
        response = self.get_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=HOST, params=filters)
        return response.get('hostId', list()) if response else list()

    def create_host(self, host_name, initiator_list=None,
                    host_flags=None, init_file=None, _async=False):
        """Create a host with the given initiators.

        Accepts either initiator_list, e.g.
        [10000000ba873cbf, 10000000ba873cba], or file.
        The initiators must not be associated with another host.
        An empty host can also be created by not passing any initiator ids.

        :param host_name: name of the new host -- str
        :param initiator_list: list of initiators -- list
        :param host_flags: optional host flags to apply -- dict
        :param init_file: path to file containing initiator names -- str
        :param _async: if call should be _async -- bool
        :returns: new host details -- dict
        """
        if init_file:
            initiator_list = file_handler.create_list_from_file(init_file)
        new_ig_data = {'hostId': host_name}
        if initiator_list and len(initiator_list) > 0:
            new_ig_data.update({'initiatorId': initiator_list})
        if host_flags:
            new_ig_data.update({'hostFlags': host_flags})
        if _async:
            new_ig_data.update(ASYNC_UPDATE)
        return self.create_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=HOST, payload=new_ig_data)

    def modify_host(self, host_id, host_flag_dict=None,
                    remove_init_list=None, add_init_list=None, new_name=None):
        """Modify an existing host.

        Only one parameter can be modified at a time.

        :param host_id: host name -- str
        :param host_flag_dict: host flags -- dict
        :param remove_init_list: initiators to be removed -- list
        :param add_init_list: initiators to be added -- list
        :param new_name: new host name -- str
        :returns: modified host details -- dict
        """
        if host_flag_dict:
            edit_host_data = ({'editHostActionParam': {
                'setHostFlagsParam': {'hostFlags': host_flag_dict}}})
        elif remove_init_list:
            edit_host_data = ({'editHostActionParam': {
                'removeInitiatorParam': {'initiator': remove_init_list}}})
        elif add_init_list:
            edit_host_data = ({'editHostActionParam': {
                'addInitiatorParam': {'initiator': add_init_list}}})
        elif new_name:
            edit_host_data = ({'editHostActionParam': {
                'renameHostParam': {'new_host_name': new_name}}})
        else:
            msg = ('No modify host parameters chosen - please supply one '
                   'of the following: host_flag_dict, remove_init_list, '
                   'add_init_list, or new_name.')
            raise exception.InvalidInputException(data=msg)
        return self.modify_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=HOST, resource_type_id=host_id,
            payload=edit_host_data)

    def delete_host(self, host_id):
        """Delete a given host.

        Cannot delete if associated with a masking view.

        :param host_id: name of the host -- str
        """
        self.delete_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=HOST, resource_type_id=host_id)

    def get_masking_views_from_host(self, host_id):
        """Retrieve masking view information for a specified host.

        :param host_id: name of the host -- str
        :returns: masking views -- list
        """
        host = self.get_host(host_id)
        return host.get('maskingview', list()) if host else list()

    def get_masking_views_from_host_group(self, host_group_id):
        """Retrieve masking view information for a specified host group.

        :param host_group_id: name of the host -- str
        :returns: masking views -- list
        """
        host_group = self.get_host_group(host_group_id)
        return host_group.get('maskingview', list()) if host_group else list()

    def get_initiator_ids_from_host(self, host_id):
        """Get initiator details from a host.

        :param host_id: name of the host -- str
        :returns: initiator IDs -- list
        """
        host = self.get_host(host_id)
        return host.get('initiator', list()) if host else list()

    def get_host_group(self, host_group_id):
        """Get details on a host group on the array.

        :param host_group_id: name of the host group -- str
        :returns: host group details -- dict
        """
        return self.get_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=HOSTGROUP, resource_type_id=host_group_id)

    def get_host_group_list(self, filters=None):
        """Get list of host group(s) on the array.

        See unisphere documentation for applicable filters.

        :param filters: optional list of filters -- dict
        :returns: host group list -- list
        """
        response = self.get_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=HOSTGROUP, params=filters)
        return response.get('hostGroupId', list()) if response else list()

    def create_host_group(self, host_group_id, host_list,
                          host_flags=None, _async=False):
        """Create a host group containing the given hosts.

        :param host_group_id: name of the new host group -- str
        :param host_list: hosts -- list
        :param host_flags: optional host flags to apply -- dict
        :param _async: if call should be async -- bool
        :returns: new host group details -- dict
        """
        new_ig_data = {'hostId': host_list, 'hostGroupId': host_group_id}
        if host_flags:
            new_ig_data.update({'hostFlags': host_flags})
        if _async:
            new_ig_data.update(ASYNC_UPDATE)
        return self.create_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=HOSTGROUP, payload=new_ig_data)

    def modify_host_group(self, host_group_id, host_flag_dict=None,
                          remove_host_list=None, add_host_list=None,
                          new_name=None):
        """Modify an existing host group.

        Only one parameter can be modified at a time.

        :param host_group_id: name of the host group -- str
        :param host_flag_dict: host flags -- dict
        :param remove_host_list: hosts to be removed -- list
        :param add_host_list: hosts to be added -- list
        :param new_name: new name of the host group -- str
        :returns: modified host group details -- dict
        """
        if host_flag_dict:
            edit_host_data = ({'editHostGroupActionParam': {
                'setHostGroupFlagsParam': {'hostFlags': host_flag_dict}}})
        elif remove_host_list:
            edit_host_data = ({'editHostGroupActionParam': {
                'removeHostParam': {'host': remove_host_list}}})
        elif add_host_list:
            edit_host_data = ({'editHostGroupActionParam': {
                'addHostParam': {'host': add_host_list}}})
        elif new_name:
            edit_host_data = ({'editHostGroupActionParam': {
                'renameHostGroupParam': {'new_host_group_name': new_name}}})
        else:
            msg = ('No modify host group parameters chosen - please supply '
                   'one of the following: host_flag_dict, '
                   'remove_host_list, add_host_list, or new_name.')
            raise exception.InvalidInputException(data=msg)
        return self.modify_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=HOSTGROUP, resource_type_id=host_group_id,
            payload=edit_host_data)

    def delete_host_group(self, host_group_id):
        """Delete a given host group.

        Cannot delete if associated with a masking view.

        :param host_group_id: name of the hostgroup -- str
        """
        self.delete_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=HOSTGROUP, resource_type_id=host_group_id)

    def get_initiator(self, initiator_id):
        """Get details of an initiator.

        :param initiator_id: initiator id -- str
        :returns: initiator details -- dict
        """
        return self.get_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=INITIATOR, resource_type_id=initiator_id)

    def get_initiator_list(self, params=None):
        """Retrieve initiator list from the array.

        :param params: optional params -- dict
        :returns: initiators -- list
        """
        response = self.get_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=INITIATOR, params=params)
        return response.get('initiatorId', list()) if response else list()

    def modify_initiator(self, initiator_id, remove_masking_entry=None,
                         replace_init=None, rename_alias=None,
                         set_fcid=None, initiator_flags=None):
        """Modify an initiator.

        Only one parameter can be edited at a time.

        :param initiator_id: initiator id -- str
        :param remove_masking_entry: 'true' or 'false' -- str
        :param replace_init: new initiator id -- str
        :param rename_alias: ('new node name', 'new port name') -- tuple
        :param set_fcid: fcid  -- str
        :param initiator_flags: initiator flags to set -- dict
        :returns: modified initiator details -- dict
        """
        if remove_masking_entry:
            edit_init_data = ({'editInitiatorActionParam': {
                'removeMaskingEntry': remove_masking_entry}})
        elif replace_init:
            edit_init_data = ({'editInitiatorActionParam': {
                'replaceInitiatorParam': {'new_initiator': replace_init}}})
        elif rename_alias:
            edit_init_data = ({'editInitiatorActionParam': {
                'renameAliasParam': {'node_name': rename_alias[0],
                                     'port_name': rename_alias[1]}}})
        elif set_fcid:
            edit_init_data = ({'editInitiatorActionParam': {
                'initiatorSetAttributesParam': {'fcidValue': set_fcid}}})
        elif initiator_flags:
            edit_init_data = ({'editInitiatorActionParam': {
                'initiatorSetFlagsParam': {
                    'initiatorFlags': initiator_flags}}})
        else:
            msg = ('No modify initiator parameters chosen - please supply '
                   'one of the following: removeMaskingEntry, '
                   'replace_init, rename_alias, set_fcid, '
                   'initiator_flags.')
            raise exception.InvalidInputException(data=msg)
        return self.modify_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=INITIATOR, resource_type_id=initiator_id,
            payload=edit_init_data)

    def is_initiator_in_host(self, initiator):
        """Check to see if a given initiator is already assigned to a host.

        :param initiator: the initiator ID -- str
        :returns: if initiator is assigned -- bool
        """
        init_list = self.get_in_use_initiator_list_from_array()
        for init in init_list:
            if initiator in init:
                return True
        return False

    def get_in_use_initiator_list_from_array(self):
        """Get the list of initiators which are in-use from the array.

        Gets the list of initiators from the array which are in
        hosts/ initiator groups.

        :returns: in-use initiators -- list
        """
        return self.get_initiator_list({'in_a_host': 'true'})

    def get_initiator_group_from_initiator(self, initiator):
        """Given an initiator, get its corresponding initiator group, if any.

        :param initiator: the initiator id -- str
        :returns: found initiator group name -- str or None
        """
        init_details = self.get_initiator(initiator)
        return init_details.get('host', None) if init_details else None

    def get_masking_view_list(self, filters=None):
        """Get a masking view or list of masking views.

        See unisphere documentation for possible filters.

        :param filters: filters -- dict
        :returns: masking views -- list
        """
        response = self.get_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=MASKINGVIEW, params=filters)
        return response.get('maskingViewId', list()) if response else list()

    def get_masking_view(self, masking_view_name):
        """Get details of a masking view.

        :param masking_view_name: the masking view name -- str
        :returns: masking view details -- dict
        """
        return self.get_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=MASKINGVIEW, resource_type_id=masking_view_name)

    def create_masking_view_existing_components(
            self, port_group_name, masking_view_name,
            storage_group_name, host_name=None,
            host_group_name=None, _async=False, starting_lun_address=None):
        """Create a new masking view using existing groups.

        Must enter either a host name or a host group name, but not both.

        :param port_group_name: name of the port group -- str
        :param masking_view_name: name of the new masking view -- str
        :param storage_group_name: name of the storage group -- str
        :param host_name: name of the host (initiator group) -- str
        :param host_group_name: name of host group -- str
        :param _async: if command should be run asynchronously -- bool
        :param starting_lun_address: HLU address of starting lun for volumes
                                     -- int
        :returns: masking view details -- dict
        :raises: InvalidInputException
        """
        if host_name:
            host_details = {'useExistingHostParam': {'hostId': host_name}}
        elif host_group_name:
            host_details = ({'useExistingHostGroupParam': {
                'hostGroupId': host_group_name}})
        else:
            msg = 'Must enter either a host name or a host group name.'
            raise exception.InvalidInputException(data=msg)
        payload = ({
            'portGroupSelection': {
                'useExistingPortGroupParam': {
                    'portGroupId': port_group_name}},
            'maskingViewId': masking_view_name,
            'hostOrHostGroupSelection': host_details,
            'storageGroupSelection': {
                'useExistingStorageGroupParam': {
                    'storageGroupId': storage_group_name}}})
        if _async:
            payload.update(ASYNC_UPDATE)

        if starting_lun_address:
            payload.update({'starting_lun_address': starting_lun_address})

        return self.create_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=MASKINGVIEW, payload=payload)

    def get_masking_views_from_storage_group(self, storagegroup):
        """Return any masking views associated with a storage group.

        :param storagegroup: storage group name -- str
        :returns: masking view list -- list
        """
        sg = self.get_storage_group(storagegroup)
        return sg.get('maskingview', list()) if sg else list()

    def get_masking_views_by_initiator_group(self, initiator_group_name):
        """Given a host (initiator group), retrieve the masking view name.

        Retrieve the list of masking views associated with the
        given initiator group.

        :param initiator_group_name: name of the initiator group -- str
        :returns: masking view names -- list
        """
        ig_details = self.get_host(initiator_group_name)
        return ig_details.get('maskingview', list()) if ig_details else list()

    def get_element_from_masking_view(
            self, maskingview_name, portgroup=False, host=False,
            storagegroup=False):
        """Return the name of the specified element from a masking view.

        :param maskingview_name: masking view name -- str
        :param portgroup: port group name -- str
        :param host: the host name -- str
        :param storagegroup: storage group name -- str
        :returns: specified element name -- str
        :raises: ResourceNotFoundException
        """
        element = None
        masking_view_details = self.get_masking_view(maskingview_name)
        if masking_view_details:
            if portgroup:
                element = masking_view_details['portGroupId']
            elif host:
                if masking_view_details.get('hostId'):
                    element = masking_view_details['hostId']
                elif masking_view_details.get('hostGroupId'):
                    element = masking_view_details['hostGroupId']
            elif storagegroup:
                element = masking_view_details['storageGroupId']
        else:
            exception_message = 'Error retrieving masking group.'
            raise exception.ResourceNotFoundException(
                data=exception_message)
        return element

    def get_port_group_common_masking_views(self, port_group_name,
                                            initiator_group_name):
        """Get common masking views for a given port group and initiator group.

        :param port_group_name: port group name -- str
        :param initiator_group_name: initiator group name -- str
        :returns: masking views - list
        """
        return self.get_masking_view_list(
            {'port_group_name': port_group_name,
             'host_or_host_group_name': initiator_group_name})

    def delete_masking_view(self, maskingview_name):
        """Delete a masking view.

        :param maskingview_name: masking view name -- str
        """
        self.delete_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=MASKINGVIEW, resource_type_id=maskingview_name)

    def rename_masking_view(self, masking_view_id, new_name):
        """Rename an existing masking view.

        Currently, the only supported modification is "rename".

        :param masking_view_id: current name of the masking view -- str
        :param new_name: new name of the masking view -- str
        :returns: modified masking view details -- dict
        """
        mv_payload = {'editMaskingViewActionParam': {
            'renameMaskingViewParam': {'new_masking_view_name': new_name}}}
        return self.modify_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=MASKINGVIEW, resource_type_id=masking_view_id,
            payload=mv_payload)

    def get_host_from_masking_view(self, masking_view_id):
        """Given a masking view, get the associated host or host group.

        :param masking_view_id: name of the masking view -- str
        :returns: host id -- str
        """
        mv_details = self.get_masking_view(masking_view_id)
        return mv_details.get('hostId', None) if mv_details else None

    def get_storage_group_from_masking_view(self, masking_view_id):
        """Given a masking view, get the associated storage group.

        :param masking_view_id:  masking view name -- str
        :returns: name of the storage group -- str
        """
        mv_details = self.get_masking_view(masking_view_id)
        return mv_details.get('storageGroupId') if mv_details else None

    def get_port_group_from_masking_view(self, masking_view_id):
        """Given a masking view, get the associated port group.

        :param masking_view_id: masking view name -- str
        :returns: name of the port group -- str
        """
        mv_details = self.get_masking_view(masking_view_id)
        return mv_details.get('portGroupId', None) if mv_details else None

    def get_masking_view_connections(self, masking_view_id, filters=None):
        """Get all connection information for a given masking view.

        :param masking_view_id: masking view id -- str
        :param filters: optional filter parameters -- dict
        :returns: masking view connection dicts -- list
        """
        response = self.get_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=MASKINGVIEW, resource_type_id=masking_view_id,
            resource=CONNECTIONS, params=filters)
        return response.get(
            'maskingViewConnection', list()) if response else list()

    def find_host_lun_id_for_volume(self, masking_view_id, device_id):
        """Find the host_lun_id for a volume in a masking view.

        :param masking_view_id: masking view id -- str
        :param device_id: the device id -- str
        :returns: host lun id -- str
        """
        host_lun_id = None
        filters = {'volume_id': device_id}
        connection_info = self.get_masking_view_connections(masking_view_id,
                                                            filters)
        if len(connection_info) == 0:
            LOG.error(
                'Cannot retrieve masking view connection information for '
                '{dev} in {mv}'.format(dev=device_id, mv=masking_view_id))
        else:
            try:
                host_lun_id = (connection_info[0]['host_lun_address'])
                host_lun_id = int(host_lun_id, 16)
            except Exception as e:
                LOG.error(
                    'Unable to retrieve connection information for volume '
                    '{vol} in masking view {mv}. Exception received: '
                    '{exc}'.format(vol=device_id, mv=masking_view_id, exc=e))
        return host_lun_id

    def get_port_list(self, filters=None):
        """Query for a list of Symmetrix port keys.

        Note a mixture of Front end, back end and RDF port specific values
        are not allowed. See UniSphere documentation for possible values.

        :param filters: optional filters e.g. {'vnx_attached': 'true'} -- dict
        :returns: port key dicts -- list
        """
        response = self.get_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=PORT, params=filters)
        return response.get('symmetrixPortKey', list()) if response else list()

    def get_port_group(self, port_group_id):
        """Get port group details.

        :param port_group_id: name of the portgroup -- str
        :returns: port group details -- dict
        """
        return self.get_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=PORTGROUP, resource_type_id=port_group_id)

    def get_port_group_list(self, filters=None):
        """Get port group details.

        :param filters: optional filters -- dict
        :returns: port groups -- list
        """
        response = self.get_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=PORTGROUP, params=filters)
        return response.get('portGroupId', list()) if response else list()

    def get_ports_from_port_group(self, port_group):
        """Get a list of port identifiers from a port group.

        :param port_group: name of the portgroup -- list
        :returns: port ids -- list
        """
        port_list = list()
        port_group_info = self.get_port_group(port_group)
        if port_group_info and port_group_info.get('symmetrixPortKey'):
            port_key = port_group_info['symmetrixPortKey']
            for key in port_key:
                port = key['portId']
                port_list.append(port)
        return port_list

    def create_empty_port_group(
            self, port_group_id, port_group_protocol=None, _async=None):
        """Create an empty port group.

        :param port_group_id: name of the new port group -- str
        :param port_group_protocol: required for V4 only one of [SCSI_FC, iSCSI
                                    , NVMe_TCP] -- str
        :param _async: if call should be async -- bool
        :returns: new port group details -- dict
        """
        payload = ({'portGroupId': port_group_id})
        if self.common.is_array_v4(self.array_id):
            if not port_group_protocol:
                message = ('port_group_protocol must be set for a V4 '
                           'array. It must be one of SCSI_FC, iSCSI or '
                           'NVMe_TCP')
                raise exception.InvalidInputException(data=message)
        if port_group_protocol:
            payload['port_group_protocol'] = port_group_protocol
        if _async:
            payload.update(ASYNC_UPDATE)
        result = self.create_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=PORTGROUP, payload=payload)
        return result

    def create_new_port_group(self, port_group_id, dir_port_list,
                              port_group_protocol=None):
        """Create a new port group with one or more ports.

        :param port_group_id: name of the new port group -- str
        :param dir_port_list: port dicts Example:
               [{'directorId': director_id, 'portId': port_id}] -- list
        :param port_group_protocol: required for V4 only.
                                    one of [SCSI_FC, iSCSI, NVMe_TCP]
        :returns: new port group details -- dict
        """
        if self.common.is_array_v4(self.array_id):
            if not port_group_protocol:
                message = ('port_group_protocol must be set for a V4 '
                           'array. It must be one of SCSI_FC, iSCSI or '
                           'NVMe_TCP')
                raise exception.InvalidInputException(data=message)
        if utils.validate_input(PORT_STRUCTURE, dir_port_list):
            payload = ({'portGroupId': port_group_id,
                        'symmetrixPortKey': dir_port_list})
            if port_group_protocol:
                payload['port_group_protocol'] = port_group_protocol
            result = self.create_resource(
                category=SLOPROVISIONING,
                resource_level=SYMMETRIX, resource_level_id=self.array_id,
                resource_type=PORTGROUP, payload=payload)
            result = self._update_port_group_port_ids(result)
            return result
        else:
            error_message = (
                'Please check that your ports parameter is in '
                'the format {struct}.'.format(struct=PORT_STRUCTURE))
            LOG.error(error_message)
            return None

    def create_port_group_from_file(self, file_name, port_group_id,
                                    port_group_protocol=None):
        """Given a file with director:port pairs, create a portgroup.

        Each director:port pair must be on a new line.
        Example director:port - FA-1D:4.

        :param file_name: path to the file -- str
        :param port_group_id: name for the port group -- str
        :param port_group_protocol: required for V4 only.
                                    one of [SCSI_FC, iSCSI, NVMe_TCP] -- str
        :returns: new port group details -- dict
        """
        port_list = file_handler.create_list_from_file(file_name)
        combined_payload = list()
        for i in port_list:
            current_director_id, current_port_id = i.split(':')
            temp_list = {'directorId': current_director_id,
                         'portId': current_port_id}
            combined_payload.append(temp_list)

        return self.create_new_port_group(
            port_group_id, combined_payload, port_group_protocol)

    def modify_port_group(self, port_group_id, remove_port=None, add_port=None,
                          rename_port_group=None):
        """Modify an existing port group.

        Only one parameter can be modified at a time.

        :param port_group_id: name of the port group -- str
        :param remove_port: port details (director_id, port_id) -- tuple
        :param add_port: port details (director_id, port_id) -- tuple
        :param rename_port_group: new port group name -- str
        :returns: modified port group details -- dict
        """
        if remove_port:
            edit_pg_data = ({'editPortGroupActionParam': {'removePortParam': {
                'port': [{'directorId': remove_port[0],
                          'portId': remove_port[1]}]}}})
        elif add_port:
            edit_pg_data = ({'editPortGroupActionParam': {'addPortParam': {
                'port': [{'directorId': add_port[0],
                          'portId': add_port[1]}]}}})
        elif rename_port_group:
            edit_pg_data = ({'editPortGroupActionParam': {
                'renamePortGroupParam': {
                    'new_port_group_name': rename_port_group}}})
        else:
            message = ('No modify portgroup parameters set - please set one '
                       'of the following: remove_port, add_port, or '
                       'rename_portgroup.')
            raise exception.InvalidInputException(data=message)
        result = self.modify_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=PORTGROUP, resource_type_id=port_group_id,
            payload=edit_pg_data)
        if add_port or remove_port:
            result = self._update_port_group_port_ids(result)
        return result

    def delete_port_group(self, port_group_id):
        """Delete a port group.

        :param port_group_id: name of the port group -- str
        """
        self.delete_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=PORTGROUP, resource_type_id=port_group_id)

    def get_service_level_list(self, filters=None):
        """Retrieve the list of service levels from the array.

        :param filters: optional filters -- dict
        :returns: service level names -- list
        """
        slo_dict = self.get_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=SLO, params=filters)
        return slo_dict.get('sloId', list()) if slo_dict else list()

    def get_service_level(self, service_level_id):
        """Get details on a specific service level.

        :param service_level_id: service level agreement -- str
        :returns: service level details -- dict
        """
        return self.get_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=SLO, resource_type_id=service_level_id)

    def modify_service_level(self, service_level_id, new_name):
        """Modify an SLO.

        Currently, the only modification permitted is renaming.

        :param service_level_id: current name of the service level -- str
        :param new_name: new name for the -- str
        :returns: modified service level details -- dict
        """
        edit_slo_data = ({'editSloActionParam': {
            'renameSloParam': {'sloId': new_name}}})
        return self.modify_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=SLO, resource_type_id=service_level_id,
            payload=edit_slo_data)

    def get_srp(self, srp):
        """Get details on a specific SRP.

        :param srp: storage resource pool id -- str
        :returns: srp details -- dict
        """
        return self.get_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=SRP, resource_type_id=srp)

    def get_srp_list(self, filters=None):
        """Get a list of available SRPs on a given array.

        :param filters: filter parameters -- dict
        :returns: SRPs -- list
        """
        response = self.get_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=SRP, params=filters)
        return response.get('srpId', list()) if response else list()

    def get_compressibility_report(self, srp_id):
        """Get a specified SRP Compressibility Report.

        :param srp_id: srp id -- str
        :returns: compressibility reports -- list
        """
        response = self.get_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=SRP, resource_type_id=srp_id,
            resource=COMPRESSIBILITY_REPORT)
        return response.get(
            'storageGroupCompressibility', list()) if response else list()

    def is_compression_capable(self):
        """Check if array is compression capable.

        :returns: bool
        """
        array_list = self.common.get_v3_or_newer_array_list(
            filters={'compressionCapable': 'true'})
        return self.array_id in array_list

    def get_storage_group(self, storage_group_name):
        """Given a name, return storage group details.

        :param storage_group_name: name of the storage group -- str
        :returns: storage group details -- dict
        """
        return self.get_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=STORAGEGROUP, resource_type_id=storage_group_name)

    def get_storage_group_demand_report(self, srp_id=None):
        """Get the storage group demand report.

        Get the storage group demand report from Unisphere.

        :param srp_id: id of the Storage Resource Pool -- str
        :returns: demand report -- dict
        """
        if not srp_id:
            srp_id = 'SRP_1'
        return self.get_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=SRP, resource_type_id=srp_id,
            resource=SG_DEMAND_REPORT)

    def get_storage_group_list(self, filters=None):
        """Return a list of storage groups.

        :param filters: filter parameters e.g. {'is_link_target': True}
                        see API documentation https://developer.dell.com/
                        for full list of available filters-- dict
        :returns: storage groups -- list
        """
        sg = self.get_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=STORAGEGROUP, params=filters)
        return sg.get('storageGroupId', list()) if sg else list()

    def get_masking_view_from_storage_group(self, storage_group):
        """Get the associated masking views from a given storage group.

        :param storage_group: name of the storage group -- str
        :returns: Masking views -- list
        """
        response = self.get_storage_group(storage_group)
        return response.get('maskingview', list()) if response else list()

    def get_num_vols_in_storage_group(self, storage_group_name):
        """Get the number of volumes in a storage group.

        :param storage_group_name: storage group name -- str
        :returns: number of volumes -- int
        """
        sg = self.get_storage_group(storage_group_name)
        return int(sg.get('num_of_vols', 0)) if sg else 0

    def is_child_storage_group_in_parent_storage_group(self, child_name,
                                                       parent_name):
        """Check if a child storage group is a member of a parent group.

        :param child_name: child sg name -- str
        :param parent_name: parent sg name -- str
        :returns: bool
        """
        parent_sg = self.get_storage_group(parent_name)
        if parent_sg and parent_sg.get('child_storage_group'):
            child_sg_list = parent_sg['child_storage_group']
            if child_name in child_sg_list:
                return True
        return False

    def get_child_storage_groups_from_parent(self, parent_name):
        """Get child storage group list from parent storage group.

        :param parent_name: parent sg name -- str
        :returns: child sg details -- list
        """
        sg = self.get_storage_group(parent_name)
        return sg.get('child_storage_group', list()) if sg else list()

    def create_storage_group(
            self, srp_id, sg_id, slo=None, workload=None,
            do_disable_compression=False, num_vols=0, vol_size=0,
            cap_unit='GB', allocate_full=False, _async=False,
            vol_name=None, snapshot_policy_ids=None, enable_mobility_id=False,
            emulation_type='FBA', append_vol_id=False):
        """Create a storage group with optional volumes on create operation.

        :param srp_id: SRP id -- str
        :param sg_id: storage group id -- str
        :param slo: service level id -- str
        :param workload: workload id -- str
        :param do_disable_compression: disable compression -- bool
        :param num_vols: number of volumes to be created -- int
        :param vol_size: the volume size -- int
        :param cap_unit: capacity unit (MB, GB, TB, CYL) -- str
        :param allocate_full: allocate full capacity -- bool
        :param _async: if call should be async -- bool
        :param vol_name: name to give to the volume, optional -- str
        :param snapshot_policy_ids: list of one or more snapshot policies
                                    to associate with storage group -- list
        :param enable_mobility_id: enables unique volume WWN not tied to array
                                   serial number -- bool
        :param emulation_type: device emulation type (CKD, FBA) -- str
        :param append_vol_id: append volume id to the volume name,
                              optional -- bool
        :returns: storage group details -- dict
        """
        srp_id = srp_id if srp_id else 'None'
        slo = slo if slo else 'None'
        workload = workload if workload else 'None'

        payload = ({'srpId': srp_id,
                    'storageGroupId': sg_id,
                    'emulation': emulation_type})

        volume_attributes = {'volume_size': str(vol_size),
                             'capacityUnit': cap_unit,
                             'num_of_vols': num_vols}
        if vol_name:
            volume_identifier_choice = 'identifier_name_plus_volume_id' \
                if append_vol_id else 'identifier_name'
            volume_identifier = {'identifier_name': vol_name,
                                 'volumeIdentifierChoice':
                                     volume_identifier_choice
                                 }
            volume_attributes.update({'volumeIdentifier': volume_identifier})

        slo_param = {'sloId': slo,
                     'workloadSelection': workload,
                     'volumeAttributes': [volume_attributes]}

        if do_disable_compression:
            slo_param.update({'noCompression': 'true'})

        if allocate_full:
            # If case of full volume allocation, we must set the
            # noCompression parameter at true because fully
            # allocations and compression are exclusive parameters
            slo_param.update({'noCompression': 'true'})
            slo_param.update({'allocate_capacity_for_each_vol': 'true'})
            slo_param.update({'persist_preallocated_capacity_through_'
                              'reclaim_or_copy': 'true'})

        if snapshot_policy_ids:
            payload.update({'snapshot_policies': snapshot_policy_ids})
        payload.update({'sloBasedStorageGroupParam': [slo_param]})

        if _async:
            payload.update(ASYNC_UPDATE)

        if enable_mobility_id:
            slo_param.update({'enable_mobility_id': enable_mobility_id})

        return self.create_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=STORAGEGROUP, payload=payload)

    def create_non_empty_storage_group(
            self, srp_id, storage_group_id, service_level, workload, num_vols,
            vol_size, cap_unit, disable_compression=False, _async=False,
            vol_name=None, snapshot_policy_ids=None, enable_mobility_id=False,
            emulation_type='FBA'):
        """Create a new storage group with the specified volumes.

        Generates a dictionary for json formatting and calls the create_sg
        function to create a new storage group with the specified volumes. Set
        the disable_compression flag for disabling compression on an All Flash
        array (where compression is on by default).

        :param srp_id: SRP id -- str
        :param storage_group_id: storage group id -- str
        :param service_level: service level id -- str
        :param workload: workload id -- str
        :param num_vols: number of volumes to be created -- int
        :param vol_size: the volume size -- str
        :param cap_unit: capacity unit (MB, GB, TB, CYL) -- str
        :param disable_compression: disable compression -- bool
        :param _async: if call should be async -- bool
        :param vol_name: name to give to the volume, optional -- str
        :param snapshot_policy_ids: list of one or more snapshot policies
                                    to associate with storage group -- list
        :param enable_mobility_id: enables unique volume WWN not tied to array
                                   serial number -- bool
        :param emulation_type: device emulation type (CKD, FBA) -- str
        :returns: storage group details -- dict
        """
        return self.create_storage_group(
            srp_id, storage_group_id, service_level, workload,
            do_disable_compression=disable_compression,
            num_vols=num_vols, vol_size=vol_size, cap_unit=cap_unit,
            _async=_async, vol_name=vol_name,
            snapshot_policy_ids=snapshot_policy_ids,
            enable_mobility_id=enable_mobility_id,
            emulation_type=emulation_type)

    def create_empty_storage_group(
            self, srp_id, storage_group_id, service_level, workload,
            disable_compression=False, _async=False,
            snapshot_policy_ids=None, emulation_type='FBA'):
        """Create an empty storage group.

        Set the disable_compression flag for disabling compression on an All
        Flash array (where compression is on by default).

        :param srp_id: SRP id -- str
        :param storage_group_id: storage group id -- str
        :param service_level: service level id -- str
        :param workload: workload id -- str
        :param disable_compression: disable compression -- bool
        :param _async: if call should be async -- bool
        :param snapshot_policy_ids: list of one or more snapshot policies
                                    to associate with storage group -- list
        :param emulation_type: device emulation type (CKD, FBA) -- str
        :returns: storage group details -- dict
        """
        return self.create_storage_group(
            srp_id, storage_group_id, service_level, workload,
            do_disable_compression=disable_compression, _async=_async,
            snapshot_policy_ids=snapshot_policy_ids,
            emulation_type=emulation_type)

    def modify_storage_group(self, storage_group_id, payload):
        """Modify a storage group.

        :param storage_group_id: storage group id -- str
        :param payload: request payload -- dict
        :returns: modified storage group details -- dict
        """
        return self.modify_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=STORAGEGROUP, resource_type_id=storage_group_id,
            payload=payload)

    def add_existing_volume_to_storage_group(
            self, storage_group_id, vol_ids, _async=False,
            remote_array_1_id=None, remote_array_1_sgs=None,
            remote_array_2_id=None, remote_array_2_sgs=None,
            starting_lun_address=None):
        """Expand an existing storage group by adding existing volumes.

        :param storage_group_id: storage group id -- str
        :param vol_ids: volume device id(s) -- str or list
        :param _async: if call should be async -- bool
        :param remote_array_1_id: 12 digit serial number of remote array,
                                  optional -- str
        :param remote_array_1_sgs: list of storage groups on remote array to
                                   add Remote device, Unisphere instance must
                                   be local to R1 storage group otherwise
                                   volumes will only be added to the local
                                   group -- str or list
        :param remote_array_2_id: optional digit serial number of remote array,
                                  only used in multihop SRDF, e.g. R11, or
                                  R1 - R21 - R2 optional -- str
        :param remote_array_2_sgs: storage groups on remote array, optional
                                   -- str or list
        :param starting_lun_address: HLU address of starting lun for volumes
                                     -- int
        :returns: storage group details -- dict
        """
        if not isinstance(vol_ids, list):
            vol_ids = [vol_ids]
        add_vol_data = {'editStorageGroupActionParam': {
            'expandStorageGroupParam': {
                'addSpecificVolumeParam': {
                    'volumeId': vol_ids}}}}
        if _async:
            add_vol_data.update(ASYNC_UPDATE)
        if starting_lun_address:
            add_vol_data.update({'starting_lun_address': starting_lun_address})
        if remote_array_1_id and remote_array_1_sgs:
            if not isinstance(remote_array_1_sgs, list):
                remote_array_1_sgs = [remote_array_1_sgs]
            add_vol_data['editStorageGroupActionParam'][
                'expandStorageGroupParam']['addSpecificVolumeParam'].update(
                {'remoteSymmSGInfoParam': {
                    'remote_symmetrix_1_id': remote_array_1_id,
                    'remote_symmetrix_1_sgs': remote_array_1_sgs}})
            if remote_array_2_id and remote_array_2_sgs:
                if not isinstance(remote_array_2_sgs, list):
                    remote_array_2_sgs = [remote_array_2_sgs]
                add_vol_data['editStorageGroupActionParam'][
                    'expandStorageGroupParam'][
                    'addSpecificVolumeParam'].update(
                    {'remoteSymmSGInfoParam': {
                        'remote_symmetrix_1_id': remote_array_1_id,
                        'remote_symmetrix_1_sgs': remote_array_1_sgs,
                        'remote_symmetrix_2_id': remote_array_2_id,
                        'remote_symmetrix_2_sgs': remote_array_2_sgs}})
        return self.modify_storage_group(storage_group_id, add_vol_data)

    def add_new_volume_to_storage_group(
            self, storage_group_id, num_vols, vol_size, cap_unit, _async=False,
            vol_name=None, create_new_volumes=None,
            remote_array_1_id=None, remote_array_1_sgs=None,
            remote_array_2_id=None, remote_array_2_sgs=None,
            enable_mobility_id=False, emulation_type='FBA',
            append_vol_id=False, starting_lun_address=None):
        """Expand an existing storage group by adding new volumes.

        :param storage_group_id: storage group id -- str
        :param num_vols: number of volumes to be created -- int
        :param vol_size: the volume size -- str
        :param cap_unit: capacity unit (MB, GB, TB, CYL) -- str
        :param _async: if call should be async -- bool
        :param vol_name: name to give to the volume, optional -- str
        :param create_new_volumes: new volumes only, no ro-use -- bool
        :param remote_array_1_id: 12 digit serial number of remote array,
                                  optional -- str
        :param remote_array_1_sgs: list of storage groups on remote array to
                                   add Remote device, Unisphere instance must
                                   be local to R1 storage group otherwise
                                   volumes will only be added to the local
                                   group -- str or list
        :param remote_array_2_id: optional digit serial number of remote array,
                                  only used in multihop SRDF, e.g. R11, or
                                  R1 - R21 - R2 optional -- str
        :param remote_array_2_sgs: storage groups on remote array, optional
                                   -- str or list
        :param enable_mobility_id: enables unique volume WWN not tied to array
                                   serial number -- bool
        :param emulation_type: device emulation type (CKD, FBA) -- str
        :param append_vol_id: append volume id to the volume name,
                              optional -- bool
        :param starting_lun_address: HLU address of starting lun for volumes
                                     -- int
        :returns: storage group details -- dict
        """
        add_volume_param = {'emulation': emulation_type}

        if not create_new_volumes:
            add_volume_param.update({'create_new_volumes': False})
        if starting_lun_address:
            add_volume_param.update(
                {'starting_lun_address': starting_lun_address})

        volume_attributes = ({
            'num_of_vols': num_vols,
            'volume_size': vol_size,
            'capacityUnit': cap_unit})

        if vol_name:
            volume_identifier_choice = 'identifier_name_plus_volume_id' \
                if append_vol_id else 'identifier_name'
            volume_identifier = ({
                'identifier_name': vol_name,
                'volumeIdentifierChoice': volume_identifier_choice
            })
            volume_attributes.update({
                'volumeIdentifier': volume_identifier})

        add_volume_param.update({'volumeAttributes': [volume_attributes]})

        if enable_mobility_id:
            add_volume_param.update({'enable_mobility_id': enable_mobility_id})

        expand_sg_data = ({'editStorageGroupActionParam': {
            'expandStorageGroupParam': {
                'addVolumeParam': add_volume_param}}})
        if remote_array_1_id and remote_array_1_sgs:
            if not isinstance(remote_array_1_sgs, list):
                remote_array_1_sgs = [remote_array_1_sgs]
            add_volume_param.update({'remoteSymmSGInfoParam': {
                'remote_symmetrix_1_id': remote_array_1_id,
                'remote_symmetrix_1_sgs': remote_array_1_sgs}})
            if remote_array_2_id and remote_array_2_sgs:
                if not isinstance(remote_array_2_sgs, list):
                    remote_array_2_sgs = [remote_array_2_sgs]
                add_volume_param['remoteSymmSGInfoParam'].update({
                    'remote_symmetrix_2_id': remote_array_2_id,
                    'remote_symmetrix_2_sgs': remote_array_2_sgs})
        if _async:
            expand_sg_data.update(ASYNC_UPDATE)
        return self.modify_storage_group(storage_group_id, expand_sg_data)

    def remove_volume_from_storage_group(
            self, storage_group_id, vol_id, _async=False,
            remote_array_1_id=None, remote_array_1_sgs=None,
            remote_array_2_id=None, remote_array_2_sgs=None,
            terminate_snapshots=False):
        """Remove a volume from a given storage group.

        :param storage_group_id: storage group id -- str
        :param vol_id: device id -- str
        :param _async: if call should be async -- bool
        :param remote_array_1_id: 12 digit serial number of remote array,
               optional -- str
        :param remote_array_1_sgs: list of storage groups on remote array to
               add Remote device, Unisphere instance must be local to R1
               storage group otherwise volumes will only be added to the
               local group -- str or list
        :param remote_array_2_id: optional digit serial number of remote array,
               only used in multihop SRDF, e.g. R11, or R1 - R21 - R2 optional
               -- str
        :param remote_array_2_sgs: storage groups on remote array, optional
               -- str or list
        :param terminate_snapshots: terminate any snapshots on volume when
                                    removing from storage group -- bool
        :returns: storage group details -- dict
        """
        if not isinstance(vol_id, list):
            vol_id = [vol_id]
        payload = ({'editStorageGroupActionParam': {
            'removeVolumeParam': {'volumeId': vol_id}}})

        if remote_array_1_id and remote_array_1_sgs:
            if not isinstance(remote_array_1_sgs, list):
                remote_array_1_sgs = [remote_array_1_sgs]
            payload.update(
                {'editStorageGroupActionParam': {
                    'removeVolumeParam': {
                        'volumeId': vol_id,
                        'remoteSymmSGInfoParam': {
                            'remote_symmetrix_1_id': remote_array_1_id,
                            'remote_symmetrix_1_sgs': remote_array_1_sgs}}}})
            if remote_array_2_id and remote_array_2_sgs:
                if not isinstance(remote_array_2_sgs, list):
                    remote_array_2_sgs = [remote_array_2_sgs]
                payload.update({'editStorageGroupActionParam': {
                    'removeVolumeParam': {
                        'volumeId': vol_id,
                        'remoteSymmSGInfoParam': {
                            'remote_symmetrix_1_id': remote_array_1_id,
                            'remote_symmetrix_1_sgs': remote_array_1_sgs,
                            'remote_symmetrix_2_id': remote_array_2_id,
                            'remote_symmetrix_2_sgs': remote_array_2_sgs}}}})
        if _async:
            payload.update(ASYNC_UPDATE)
        if terminate_snapshots:
            payload['editStorageGroupActionParam']['removeVolumeParam'][
                'terminate_snapshots'] = terminate_snapshots
        return self.modify_storage_group(storage_group_id, payload)

    def move_volumes_between_storage_groups(
            self, device_ids, source_storagegroup_name,
            target_storagegroup_name, force=False, _async=False):
        """Move volumes to a different storage group.

        Requires force set to True if volume is in a masking view.

        :param device_ids: volume device id(s) -- str or list
        :param source_storagegroup_name: originating storage group name -- str
        :param target_storagegroup_name: destination storage group name -- str
        :param force: force flag -- bool
        :param _async: if call should be async -- bool
        :returns: storage group details -- dict
        """
        force_flag = 'true' if force else 'false'
        if not isinstance(device_ids, list):
            device_ids = [device_ids]
        payload = ({
            'editStorageGroupActionParam': {
                'moveVolumeToStorageGroupParam': {
                    'volumeId': device_ids,
                    'storageGroupId': target_storagegroup_name,
                    'force': force_flag}}})
        if _async:
            payload.update(ASYNC_UPDATE)
        return self.modify_storage_group(source_storagegroup_name, payload)

    def create_volume_from_storage_group_return_id(
            self, volume_name, storage_group_id, vol_size, cap_unit='GB',
            enable_mobility_id=False, emulation_type='FBA'):
        """Create a new volume in the given storage group.

        :param volume_name: volume name -- str
        :param storage_group_id: storage group id -- str
        :param vol_size: volume size -- str
        :param cap_unit: capacity unit (MB, GB, TB, CYL) -- str
        :param enable_mobility_id: enables unique volume WWN not tied to array
                                   serial number -- bool
        :param emulation_type: device emulation type (CKD, FBA) -- str
        :returns: device id -- str
        """
        job = self.add_new_volume_to_storage_group(
            storage_group_id, 1, vol_size, cap_unit,
            _async=True, vol_name=volume_name,
            enable_mobility_id=enable_mobility_id,
            emulation_type=emulation_type)

        task = self.common.wait_for_job('Create volume from storage group',
                                        202, job)

        # Find the newly created volume.
        device_id = None
        if task:
            for t in task:
                try:
                    desc = t['description']
                    if CREATE_VOL_STRING in desc:
                        t_list = desc.split()
                        device_id = t_list[(len(t_list) - 1)]
                        device_id = device_id[1:-1]
                        break
                except Exception as e:
                    LOG.info(
                        'Could not retrieve device id from job. Exception '
                        'received was {exc}. Attempting retrieval by '
                        'volume_identifier.'.format(exc=e))

        if not device_id:
            device_id = self.find_volume_device_id(volume_name)

        return device_id

    def add_child_storage_group_to_parent_group(self, child_storage_group,
                                                parent_storage_group):
        """Add a storage group to a parent storage group.

        This method adds an existing storage group to another storage
        group, i.e. cascaded storage groups.

        :param child_storage_group: child storage group id -- str
        :param parent_storage_group: parent storage group id -- str
        :returns: storage group details -- dict
        """
        payload = ({'editStorageGroupActionParam': {
            'expandStorageGroupParam': {
                'addExistingStorageGroupParam': {
                    'storageGroupId': [child_storage_group]}}}})
        return self.modify_storage_group(parent_storage_group, payload)

    def remove_child_storage_group_from_parent_group(self, child_storage_group,
                                                     parent_storage_group):
        """Remove a storage group from its parent storage group.

        This method removes a child storage group from its parent group.

        :param child_storage_group: child storage group id -- str
        :param parent_storage_group: parent storage group id -- str
        :returns: storage group details -- dict
        """
        payload = ({'editStorageGroupActionParam': {
            'removeStorageGroupParam': {
                'storageGroupId': [child_storage_group], 'force': 'true'}}})
        return self.modify_storage_group(parent_storage_group, payload)

    def update_storage_group_qos(self, storage_group_id, qos_specs):
        """Update the storage group instance with QoS details.

        If maxIOPS or maxMBPS is in qos_specs, then DistributionType can be
        modified in addition to maxIOPs or/and maxMBPS.
        If maxIOPS or maxMBPS is NOT in qos_specs, we check to see if either
        is set in Storage Group. If so, then DistributionType can be modified.
        Example qos specs:
        {'maxIOPS': '4000', 'maxMBPS': '4000', 'DistributionType': 'Dynamic'}

        :param storage_group_id: storage group id -- str
        :param qos_specs: qos specifications -- dict
        :returns: storage group details -- dict
        """
        message = None
        sg_details = self.get_storage_group(storage_group_id)
        sg_qos_details = None
        sg_max_iops = None
        sg_max_mbps = None
        sg_distribution_type = None
        max_iops = 'nolimit'
        max_mbps = 'nolimit'
        distribution_type = 'Never'
        property_list = list()
        try:
            sg_qos_details = sg_details['hostIOLimit']
            sg_max_iops = sg_qos_details['host_io_limit_io_sec']
            sg_max_mbps = sg_qos_details['host_io_limit_mb_sec']
            sg_distribution_type = sg_qos_details['dynamicDistribution']
        except KeyError:
            LOG.debug('Unable to get storage group QoS details.')
        if 'maxIOPS' in qos_specs:
            max_iops = qos_specs['maxIOPS']
            if max_iops != sg_max_iops:
                property_list.append(max_iops)
        if 'maxMBPS' in qos_specs:
            max_mbps = qos_specs['maxMBPS']
            if max_mbps != sg_max_mbps:
                property_list.append(max_mbps)
        if 'DistributionType' in qos_specs and (
                property_list or sg_qos_details):
            dynamic_list = ['never', 'onfailure', 'always']
            if (qos_specs.get('DistributionType').lower() not
                    in dynamic_list):
                exception_message = (
                    'Wrong Distribution type value {dt} entered. '
                    'Please enter one of: {dl}'.format(
                        dt=qos_specs.get('DistributionType'),
                        dl=dynamic_list))
                LOG.error(exception_message)
                raise exception.InvalidInputException(
                    data=exception_message)

            distribution_type = qos_specs['DistributionType']
            if distribution_type != sg_distribution_type:
                property_list.append(distribution_type)
        if property_list:
            payload = {'editStorageGroupActionParam': {
                'setHostIOLimitsParam': {
                    'host_io_limit_io_sec': max_iops,
                    'host_io_limit_mb_sec': max_mbps,
                    'dynamicDistribution': distribution_type}}}
            message = (
                self.modify_storage_group(storage_group_id, payload))
        return message

    def set_host_io_limit_iops_or_mbps(
            self, storage_group, iops, dynamic_distribution, mbps=None):
        """Set the Host IO Limits on an existing storage group.

        :param storage_group: storage group id -- str
        :param iops: IO per second, min Value 100, must be specified as
                     multiple of 100 -- int
        :param dynamic_distribution: 'Always', 'Never', 'OnFailure' -- str
        :param mbps: MB per second, min Value 100, must be specified as
                     multiple of 100 -- int
        :returns: storage group details -- dict
        """
        qos_specs = {'maxIOPS': iops,
                     'DistributionType': dynamic_distribution}
        if mbps:
            qos_specs.update({'maxMBPS': mbps})
        return self.update_storage_group_qos(storage_group, qos_specs)

    def delete_storage_group(self, storage_group_id):
        """Delete a given storage group.

        A storage group cannot be deleted if it is associated with a masking
        view.

        :param storage_group_id: storage group id -- str
        """
        self.delete_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=STORAGEGROUP, resource_type_id=storage_group_id)

    def get_volume(self, device_id):
        """Get a volume from array.

        :param device_id: device id -- str
        :returns: volume details -- dict
        """
        return self.get_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=VOLUME, resource_type_id=device_id)

    def get_volume_list(self, filters=None):
        """Get list of volumes from array.

        :param filters: filters parameters -- dict
        :returns: device ids -- list
        """
        vol_id_list = list()
        response = self.get_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=VOLUME, params=filters)
        if (response and response.get('count') and (
                int(response.get('count')) > 0)):
            count = response['count']
            max_page_size = response['maxPageSize']
            if int(count) > int(max_page_size):
                total_iterations = int(math.ceil(count / float(max_page_size)))
                iterator_id = response['id']
                for x in range(0, total_iterations):
                    start = x * max_page_size + 1
                    end = (x + 1) * max_page_size
                    if end > count:
                        end = count
                    vol_page = self.common.get_iterator_page_list(
                        iterator_id, start, end)
                    for vol in vol_page:
                        vol_id_list.append(vol['volumeId'])
            else:
                for vol in response['resultList']['result']:
                    vol_id_list.append(vol['volumeId'])
        return vol_id_list

    def get_volume_effective_wwn_details(self, vol_list,
                                         output_file_name=None):
        """Get the effective wwn for a list of vols.

        Get volume details for a list of volume device ids.

        :param vol_list: device id(s) -- list
        :param output_file_name: name of the output file -- str
        :returns: volume details list (nested) -- list
        """
        data = list()
        for device_id in vol_list:
            vol_details = self.get_volume(device_id)
            data.append([device_id,
                         vol_details.get('effective_wwn'),
                         vol_details.get('wwn'),
                         vol_details.get('has_effective_wwn'),
                         vol_details.get('storageGroupId')])

        if output_file_name:
            data.insert(0, ['volume_id', 'effective_wwn', 'wwn',
                            'has_effective_wwn', 'storage_group_id'])
            file_handler.write_to_csv_file(file_name=output_file_name,
                                           data=data)
        else:
            return data

    def get_volumes_from_storage_group(self, storage_group_id):
        """Retrieve volume information associated with a given storage group.

        :param storage_group_id: storage group id -- name
        :returns: device ids -- list
        """
        params = {'storageGroupId': storage_group_id}
        volume_list = self.get_volume_list(params)
        if len(volume_list) == 0:
            LOG.debug('Cannot find record for storage group {sg}'.format(
                sg=storage_group_id))
        return volume_list

    def get_storage_group_from_volume(self, volume_id):
        """Retrieve storage group information for a specified volume.

        :param volume_id: device id -- str
        :returns: storage groups -- list
        """
        vol = self.get_volume(volume_id)
        return vol.get('storageGroupId', list()) if vol else list()

    def is_volume_in_storage_group(self, device_id, storage_group_id):
        """See if a volume is a member of the given storage group.

        :param device_id: device id -- str
        :param storage_group_id: storage group id -- name
        :returns: bool
        """
        is_vol_in_sg = False
        sg_list = self.get_storage_group_from_volume(device_id)
        if storage_group_id in sg_list:
            is_vol_in_sg = True
        return is_vol_in_sg

    def find_volume_device_id(self, volume_name):
        """Given a volume identifier, find the corresponding device_id.

        :param volume_name: the volume name -- str
        :returns: device id -- str
        """
        device_id = None
        params = {'volume_identifier': volume_name}

        volume_list = self.get_volume_list(params)
        if not volume_list:
            LOG.debug('Cannot find record for volume {vol}'.format(
                vol=volume_name))
        else:
            if len(volume_list) == 1:
                device_id = volume_list[0]
            else:
                device_id = volume_list
                LOG.warning('{vol} volume name is not unique, returning '
                            'a list of device ids'.format(vol=volume_name))

        return device_id

    def find_volume_identifier(self, device_id):
        """Get the volume identifier of a volume.

        :param device_id: device id -- str
        :returns: volume identifier -- str
        """
        vol = self.get_volume(device_id)
        return vol.get('volume_identifier', None) if vol else None

    def get_size_of_device_on_array(self, device_id):
        """Get the size of the volume from the array.

        :param device_id: device id -- str
        :returns: size -- float
        """
        vol = self.get_volume(device_id)
        if vol and vol.get('cap_gb'):
            cap = vol['cap_gb']
        else:
            exception_message = (
                'Unable to retrieve size of device {device_id} on the '
                'array'.format(device_id=device_id))
            raise exception.ResourceNotFoundException(data=exception_message)
        return cap

    def _modify_volume(self, device_id, payload):
        """Modify a volume.

        Additional Payloads can be provided, check out documentation at
        https://dell.to/3HpzlJv for all supported volume operations.

        :param device_id: device id -- str
        :param payload: request payload e.g. {"editVolumeActionParam": {
                        "enable_mobility_id_param": {
                            "enable_mobility_id": "true"}}}
                              or
                              {
                        "editVolumeActionParam": {
                          "reset_wwn_param": {
                            "reset_wwn": "true"}}} -- dict
        :returns: volume details -- dict
        """
        return self.modify_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=VOLUME, resource_type_id=device_id,
            payload=payload)

    def extend_volume(self, device_id, new_size, _async=False,
                      rdf_group_num=None):
        """Extend a volume.

        :param device_id: device id -- str
        :param new_size: the new size for the device -- int
        :param _async: if call should be async -- bool
        :param rdf_group_num: RDF group number to extend R2 device in same
                              operation -- int
        :returns: volume details -- dict
        """
        LOG.info('Extending device {dev} to {num}GB.'.format(
            dev=device_id, num=new_size))
        vol_attributes = ({'expandVolumeParam': {'volumeAttribute': {
            'volume_size': str(new_size), 'capacityUnit': 'GB'}}})

        if rdf_group_num:
            LOG.info('Extending {dev} RDF paired device using online device '
                     'expansion.'.format(dev=device_id))
            vol_attributes['expandVolumeParam']['rdfGroupNumber'] = (
                rdf_group_num)
        payload = {'editVolumeActionParam': vol_attributes}
        if _async:
            payload.update(ASYNC_UPDATE)
        return self._modify_volume(device_id, payload)

    def rename_volume(self, device_id, new_name, append_vol_id=False):
        """Rename a volume.

        :param device_id: device id -- str
        :param new_name: new name for the volume -- str
        :param append_vol_id: append volume id to the volume name,
                              optional -- bool
        """
        if new_name is not None:
            volume_identifier_choice = 'identifier_name_plus_volume_id' \
                if append_vol_id else 'identifier_name'
            vol_identifier_dict = ({
                'identifier_name': new_name,
                'volumeIdentifierChoice': volume_identifier_choice})
        else:
            vol_identifier_dict = {'volumeIdentifierChoice': 'none'}
        rename_vol_payload = ({'editVolumeActionParam': {
            'modifyVolumeIdentifierParam': {
                'volumeIdentifier': vol_identifier_dict}}})
        return self._modify_volume(device_id, rename_vol_payload)

    def reset_volume_wwn(self, device_id, array_id=None):
        """reset volume wwn to remove external identify set by non
        disruptive migration.

        :param device_id: 5 digit device id -- int
        :param array_id: 16 digit array id -- int

        """
        array_id = array_id if array_id else self.array_id
        payload = {
            "editVolumeActionParam": {
                "reset_wwn_param": {
                    "reset_wwn": "true"
                }}}
        try:
            return self.common.modify_resource(
                target_uri=f"/{self.version}/sloprovisioning/"
                           f"symmetrix/{array_id}/volume/{device_id}",
                resource_type=None, payload=payload)
        except Exception as e:
            error_message = f"Failed to reset volume WWN: {str(e)}"
            raise Exception(error_message)

    def deallocate_volume(self, device_id):
        """Deallocate all tracks on a volume.

        Necessary before deletion. Please note that it is not possible
        to know exactly when a de-allocation is complete. This method
        will return when the array has accepted the request for de-allocation;
        the de-allocation itself happens as a background task on the array.

        :param device_id: device id -- str
        :returns: volume details -- dict
        """
        payload = ({'editVolumeActionParam': {
            'freeVolumeParam': {'free_volume': 'true'}}})
        return self._modify_volume(device_id, payload)

    @decorators.retry(exception.VolumeBackendAPIException)
    def delete_volume(self, device_id):
        """Delete a volume.

        :param device_id: device id -- str
        """
        self.delete_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=VOLUME, resource_type_id=device_id)

    def find_low_volume_utilization(self, low_utilization_percentage, csvname):
        """Find volumes under a certain utilization threshold.

        Function to find volumes under a specified percentage, (e.g. find
        volumes with utilization less than 10%) - may be long running as will
        check all sg on array and all storage group.  Only identifies volumes
        in storage group,  note if volume is in more than one sg it may show up
        more than once.

        :param low_utilization_percentage: low utilization percent -- int
        :param csvname: filename for CSV output file -- str
        """
        sg_list = self.get_storage_group_list()
        data = list()
        data.append(['sg_name', 'volume_id', 'identifier', 'capacity',
                     'allocated_percent'])
        for sg in sg_list:
            vol_list = self.get_volumes_from_storage_group(sg)
            for vol in vol_list:
                volume = self.get_volume(vol)
                if volume['allocated_percent'] < low_utilization_percentage:
                    if volume.get('volume_identifier'):
                        vol_identifier = volume.get('volume_identifier')
                    else:
                        vol_identifier = 'None'
                    data.append([
                        sg, vol, vol_identifier, volume['cap_gb'],
                        volume['allocated_percent']])
        if sg_list:
            file_handler.write_to_csv_file(csvname, data)
        else:
            LOG.warning('No data has been written to file {csv}.'.format(
                csv=csvname))

    def get_workload_settings(self):
        """Get valid workload options from array.

        :returns: workload settings -- list
        """
        wl_details = self.get_resource(
            category=SLOPROVISIONING,
            resource_level=SYMMETRIX, resource_level_id=self.array_id,
            resource_type=WORKLOADTYPE)
        return wl_details.get('workloadId', list()) if wl_details else list()

    @decorators.refactoring_notice(
        'SystemFunctions', 'get_any_director_port', 10.0, 10.2)
    def get_any_director_port(self, director, filters=None):
        """Get a non-GuestOS port from a director.

        DEPRECATION NOTICE:
        ProvisioningFunctions.get_any_director_port()
        will be removed in PyU4V version 10.2 in favour of
        SystemFunctions.get_any_director_port(). For further
        information please consult PyU4V 10.0 release notes.

        For V4 you must use SystemFunctions.get_any_director_port()

        :param director: director to search for ports with -- str
        :param filters: filters to apply when search for port -- str
        :returns: port -- int
        """
        selected_port = None
        if director and re.match(constants.DIRECTOR_SEARCH_PATTERN, director):
            port_list = self.get_director_port_list(
                director, filters=filters)
            # Avoid GOS ports
            port_list = [
                p for p in port_list if int(p[constants.PORT_ID]) < 30]
            if port_list:
                selected_port = port_list[0][constants.PORT_ID]
        return selected_port

    @staticmethod
    def format_director_port(director, port):
        """Format separate director port into single string.

        :param director: director e.g. FA-2D -- str
        :param port: port e.g. 4 -- str
        :returns: formatted director:port string --str
        """
        return '{d}:{p}'.format(d=director, p=port)

    def get_active_masking_view_connections(self):
        """Get list of active connections from any masking view.

        :returns: masking view name, connection details -- str, list
        """
        masking_view_list = self.get_masking_view_list()
        selected_masking_view = None
        active_connections = []
        for masking_view in masking_view_list:
            masking_view_connections = (
                self.get_masking_view_connections(masking_view))
            if masking_view_connections:
                selected_masking_view = masking_view
                active_connections = masking_view_connections
                break
        return selected_masking_view, active_connections

    def get_available_initiator_list(self, director_type=None):
        """Get list of available initiators.

        :param director_type: director type filter -- str
        :returns: single available initiator  -- str
        """
        final_initiator_list = list()
        all_initiators_set = set(self.get_initiator_list())
        in_use_initiators_set = set(
            self.get_in_use_initiator_list_from_array())
        available_initiators = list(all_initiators_set.difference(
            in_use_initiators_set))
        if len(available_initiators) > 0:
            for initiator in available_initiators:
                if director_type and director_type in initiator:
                    if self.common.is_array_v4(self.array_id):
                        print('should I specify which type?')
                    else:
                        final_initiator_list.append(initiator)
                elif not director_type:
                    final_initiator_list.append(initiator)
        return final_initiator_list

    def get_available_initiator(self, director_type=None):
        """Get an available initiator.

        :param director_type: director type filter -- str
        :returns: single available initiator  -- str
        """
        # all_initiators_set = set(self.get_initiator_list())
        # in_use_initiators_set = set(
        #     self.get_in_use_initiator_list_from_array())
        # available_initiators = list(all_initiators_set.difference(
        #     in_use_initiators_set))
        available_initiators = self.get_available_initiator_list(director_type)
        if available_initiators:
            return random.choice(available_initiators)
        return None

    def get_in_use_initiator(self, director_type=None):
        """Get an initiator that is in use.

        :param director_type: director type filter -- str
        :returns: single in-use initiator -- str
        """
        # Set manipulation introduces some unordered sorting
        # rather than directly passing back first item in in_use list.
        initiators = self.get_in_use_initiator_list_from_array()
        if len(initiators) > 0:
            return_initiator = None
            if director_type:
                for initiator in initiators:
                    if director_type in initiator:
                        return_initiator = initiator
                        break
            else:
                return_initiator = random.choice(initiators)
            return return_initiator
        else:
            return None

    def get_available_initiator_wwn_as_list(self):
        """Get an available initiator wwn string in a list.

        :returns: single available initiator wwn -- list
        """
        if self.common.is_array_v4(self.array_id):
            director_type = 'OR'
        else:
            director_type = 'FA'
        available_initiator = self.get_available_initiator(director_type)
        if available_initiator:
            available_initiator_wwn = available_initiator.split(':')[2]
            return [available_initiator_wwn]

    @staticmethod
    def _update_port_group_port_ids(port_group_details):
        """Given port_group_details, update the port id values if needed

        :param port_group_details: results from port group operations -- dict
        :returns: port_group_details with corrected symmetrix_port_key -- dict
        """
        key = constants.SYMMETRIX_PORT_KEY
        if port_group_details and key in port_group_details:
            symmetrix_port_key = port_group_details[
                constants.SYMMETRIX_PORT_KEY]
            for index, port_key in enumerate(symmetrix_port_key):
                port_id = port_key[constants.PORT_ID]
                split_port_id = port_id.split(':')
                if len(split_port_id) > 1:
                    corrected_port_id = split_port_id[-1]
                    symmetrix_port_key[index][
                        constants.PORT_ID] = corrected_port_id
            port_group_details[
                constants.SYMMETRIX_PORT_KEY] = symmetrix_port_key
        return port_group_details

    def get_split_list(self):
        """Get list of FICON splits from array.
        :returns: split ids -- list
        """
        split_id_list = list()
        response = self.common.get_resource(category=MAINFRAME,
                                            resource_level=SYMMETRIX,
                                            resource_level_id=self.array_id,
                                            resource_type=FICON_SPLIT)
        if response and response.get('splitId'):
            split_id_list = response['splitId']
        return split_id_list

    def get_split(self, split_id: str):
        """Get details of a specified FICON split.
        :param split_id: split id -- str
        :returns: split details -- dict
        """
        return self.common.get_resource(category=MAINFRAME,
                                        resource_level=SYMMETRIX,
                                        resource_level_id=self.array_id,
                                        resource_type=FICON_SPLIT,
                                        resource_type_id=split_id)

    def get_cu_image_list(self, split_id: str):
        """Get list of CU Image SSIDs within a specific FICON Split.
        :param split_id: split id -- str
        :returns: CU Image ssids -- list
        """
        cu_image_ssid_list = list()
        response = self.common.get_resource(category=MAINFRAME,
                                            resource_level=SYMMETRIX,
                                            resource_level_id=self.array_id,
                                            resource_type=FICON_SPLIT,
                                            resource_type_id=split_id,
                                            resource=CU_IMAGE)
        if response and response.get('cuImageSSID'):
            cu_image_ssid_list = response['cuImageSSID']
        return cu_image_ssid_list

    def get_cu_image(self, split_id: str, cu_ssid: str):
        """Get details of a specified CU Image.
        :param split_id: split id -- str
        :param cu_ssid: cu image ssid -- str
        :returns: CU Image details -- dict
        """
        return self.common.get_resource(category=MAINFRAME,
                                        resource_level=SYMMETRIX,
                                        resource_level_id=self.array_id,
                                        resource_type=FICON_SPLIT,
                                        resource_type_id=split_id,
                                        resource=CU_IMAGE,
                                        resource_id=cu_ssid)

    def create_cu_image(self, split_id: str,
                        cu_number: str, cu_ssid: str, cu_base_address: str,
                        vol_id: str):
        """Creates a new CU image under the specified split.
        :param split_id: split id -- str
        :param cu_number: cu image number -- str
        :param cu_ssid: cu image ssid -- str
        :param cu_base_address: cu image ssid -- str
        :param vol_id volume device id be mapped to the cu -- str
        :returns: None
        """
        new_cu_data = {"cuImageSSID": cu_ssid,
                       "cuImageNumber": cu_number,
                       "startBaseAddress": cu_base_address,
                       "volumeId": [vol_id]
                       }

        new_cu_data.update(ASYNC_UPDATE)

        create_cu_async_job = (
            self.common.create_resource(category=MAINFRAME,
                                        resource_level=SYMMETRIX,
                                        resource_level_id=self.array_id,
                                        resource_type=FICON_SPLIT,
                                        resource_type_id=split_id,
                                        resource=CU_IMAGE,
                                        payload=new_cu_data))
        return self.common.wait_for_job(
            operation='Create CU Image with volume',
            status_code=constants.STATUS_202,
            job=create_cu_async_job)

    def get_cu_image_volumes(self, split_id: str, cu_ssid: str):
        """Get list of Volumes from a specified CU Image.
        :param split_id: split id -- str
        :param cu_ssid: cu image ssid -- str
        :returns: Volume ids -- list
        """
        volume_id_list = list()
        response = self.common.get_resource(category=MAINFRAME,
                                            resource_level=SYMMETRIX,
                                            resource_level_id=self.array_id,
                                            resource_type=FICON_SPLIT,
                                            resource_type_id=split_id,
                                            resource=CU_IMAGE,
                                            resource_id=cu_ssid,
                                            object_type=VOLUME)
        if response and response.get('volumeId'):
            volume_id_list = response['volumeId']
        return volume_id_list

    def get_cu_image_volume(self, split_id: str, cu_ssid: str, vol_id: str):
        """Get details of a volume mapped to a specified CU Image.
        :param split_id: split id -- str
        :param cu_ssid: cu image ssid -- str
        :pamam vol_id volume device id to be mapped to the cu -- str
        :returns: volume details -- dict
        """
        return self.common.get_resource(category=MAINFRAME,
                                        resource_level=SYMMETRIX,
                                        resource_level_id=self.array_id,
                                        resource_type=FICON_SPLIT,
                                        resource_type_id=split_id,
                                        resource=CU_IMAGE,
                                        resource_id=cu_ssid,
                                        object_type=VOLUME,
                                        object_type_id=vol_id)

    def modify_cu_image(self, split_id: str, cu_ssid: str,
                        assign_alias_dict=None,
                        remove_alias_dict=None,
                        map_start_address=None,
                        map_volume_list=None,
                        unmap_volume_list=None):
        """Modify an existing cu image.
        :param split_id: split id -- str
        :param cu_ssid: cu image ssid -- str
        :param assign_alias_dict: alias range to be assigned -- dict
        :param remove_alias_dict: alias range to be removed -- dict
        :param map_start_address:
        :param map_volume_list: volumes to be mapped -- list
        :param unmap_volume_list: volumes to be unmapped -- list
        """
        if assign_alias_dict:
            operation = 'Edit CU Image - Assign Alias'
            edit_cu_data = {
                'editCUImageActionParam': {
                    'assignAliasRangeParam': assign_alias_dict
                }
            }
        elif remove_alias_dict:
            operation = 'Edit CU Image - Remove Alias'
            edit_cu_data = {
                'editCUImageActionParam': {
                    'removeAliasRangeParam': remove_alias_dict
                }
            }
        elif map_volume_list:
            operation = 'Edit CU Image - Map Volume(s)'
            edit_cu_data = {
                'editCUImageActionParam': {
                    'mapVolumeParam': {
                        'startBaseAddress': map_start_address,
                        'volumeId': map_volume_list
                    }
                }
            }
        elif unmap_volume_list:
            operation = 'Edit CU Image - Unmap Volume(s)'
            edit_cu_data = {
                'editCUImageActionParam': {
                    'unmapVolumeParam': {
                        'volumeId': unmap_volume_list
                    }
                }
            }
        else:
            msg = ('No modify cu image parameters chosen - please supply '
                   'one of the following: assign_alias_dict, '
                   'remove_alias_dict, map_volume_list, or unmap_volume_list.')
            raise exception.InvalidInputException(data=msg)

        edit_cu_data.update(ASYNC_UPDATE)

        edit_cu_async_job = (
            self.common.modify_resource(category=MAINFRAME,
                                        resource_level=SYMMETRIX,
                                        resource_level_id=self.array_id,
                                        resource_type=FICON_SPLIT,
                                        resource_type_id=split_id,
                                        resource=CU_IMAGE,
                                        resource_id=cu_ssid,
                                        payload=edit_cu_data))
        return self.common.wait_for_job(
            operation=operation, status_code=constants.STATUS_202,
            job=edit_cu_async_job)
