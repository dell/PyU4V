# The MIT License (MIT)
# Copyright (c) 2016 Dell Inc. or its subsidiaries.

# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""provisioning.py."""
import csv
import logging
import math

from PyU4V.utils import constants
from PyU4V.utils import exception

LOG = logging.getLogger(__name__)

SLOPROVISIONING = constants.SLOPROVISIONING
CREATE_VOL_STRING = constants.CREATE_VOL_STRING
ASYNC_UPDATE = constants.ASYNC_UPDATE


class ProvisioningFunctions(object):
    """ProvisioningFunctions."""

    def __init__(self, array_id, request, common, u4v_version):
        """__init__."""
        self.array_id = array_id
        self.common = common
        self.request = request
        self.U4V_VERSION = u4v_version
        self.get_resource = self.common.get_resource
        self.create_resource = self.common.create_resource
        self.modify_resource = self.common.modify_resource
        self.delete_resource = self.common.delete_resource

    def get_director(self, director):
        """Query for details of a director for a symmetrix.

        :param director: the director ID e.g. FA-1D
        :return: dict
        """
        if int(self.U4V_VERSION) >= 90:
            return self.get_resource(self.array_id, "system", 'director',
                                     resource_name=director)
        else:
            return self.get_resource(self.array_id, SLOPROVISIONING,
                                     'director', resource_name=director)

    def get_director_list(self):
        """Query for details of Symmetrix directors for a symmetrix.

        :return: director list
        """
        if int(self.U4V_VERSION) < 90:
            response = self.get_resource(
                self.array_id, SLOPROVISIONING, 'director')
        else:
            response = self.get_resource(
                self.array_id, "system", 'director')
        director_list = response.get('directorId', []) if response else []
        return director_list

    def get_director_port(self, director, port_no):
        """Get details of the symmetrix director port.

        :param director: the director ID e.g. FA-1D
        :param port_no: the port number e.g. 1
        :return: dict
        """
        res_name = "%s/port/%s" % (director, port_no)
        if int(self.U4V_VERSION) < 90:
            return self.get_resource(self.array_id, SLOPROVISIONING,
                                     'director',
                                     resource_name=res_name)
        else:
            return self.get_resource(self.array_id, "system", 'director',
                                     resource_name=res_name)

    def get_director_port_list(self, director, filters=None):
        """Get list of the ports on a particular director.

        Can be filtered by optional parameters, please see documentation.

        :param director: the director ID e.g. FA-1D
        :param filters: optional filters - dict
        :return: list of port key dicts
        """
        resource_name = "%s/port" % director
        if int(self.U4V_VERSION) < 90:
            response = self.get_resource(
                self.array_id, SLOPROVISIONING, 'director',
                resource_name=resource_name, params=filters)
        else:
            response = self.get_resource(
                self.array_id, "system", 'director',
                resource_name=resource_name, params=filters)

        port_key_list = response.get('symmetrixPortKey') if response else []
        return port_key_list

    def get_port_identifier(self, director, port_no):
        """Get the identifier (wwn) of the physical port.

        :param director: the ID of the director
        :param port_no: the number of the port
        :return: wwn (FC) or iqn (iscsi), or None
        """
        wwn = None
        port_info = self.get_director_port(director, port_no)
        if port_info:
            try:
                wwn = port_info['symmetrixPort']['identifier']
            except KeyError:
                LOG.error("Cannot retrieve port information")
        return wwn

    def get_host(self, host_id):
        """Get details on a host on the array.

        :param host_id: the name of the host, optional
        :return: dict
        """
        return self.get_resource(self.array_id, SLOPROVISIONING, 'host',
                                 resource_name=host_id)

    def get_host_list(self, filters=None):
        """Get list of the hosts on the array.

        See documentation for applicable filters.

        :param filters: optional list of filters - dict
        :return: list of hosts
        """
        response = self.get_resource(
            self.array_id, SLOPROVISIONING, 'host', params=filters)
        host_list = response.get('hostId', []) if response else []
        return host_list

    def create_host(self, host_name, initiator_list=None,
                    host_flags=None, init_file=None, _async=False):
        """Create a host with the given initiators.

        Accepts either initiator_list, e.g.
        [10000000ba873cbf, 10000000ba873cba], or file.
        The initiators must not be associated with another host.
        An empty host can also be created by not passing any initiator ids.

        :param host_name: the name of the new host
        :param initiator_list: list of initiators
        :param host_flags: dictionary of optional host flags to apply
        :param init_file: full path to file that contains initiator names
        :param _async: Flag to indicate if call should be _async
        :return: dict
        """
        if init_file:
            initiator_list = self.common.create_list_from_file(init_file)
        new_ig_data = ({"hostId": host_name})
        if initiator_list and len(initiator_list) > 0:
            new_ig_data.update({"initiatorId": initiator_list})
        if host_flags:
            new_ig_data.update({"hostFlags": host_flags})
        if _async:
            new_ig_data.update(ASYNC_UPDATE)
        return self.create_resource(self.array_id, SLOPROVISIONING,
                                    'host', payload=new_ig_data)

    def modify_host(self, host_id, host_flag_dict=None,
                    remove_init_list=None, add_init_list=None, new_name=None):
        """Modify an existing host.

        Only one parameter can be modified at a time.

        :param host_id: the host name
        :param host_flag_dict: dictionary of host flags
        :param remove_init_list: list of initiators to be removed
        :param add_init_list: list of initiators to be added
        :param new_name: new host name
        :return: dict
        """
        if host_flag_dict:
            edit_host_data = ({"editHostActionParam": {
                "setHostFlagsParam": {"hostFlags": host_flag_dict}}})
        elif remove_init_list:
            edit_host_data = ({"editHostActionParam": {
                "removeInitiatorParam": {"initiator": remove_init_list}}})
        elif add_init_list:
            edit_host_data = ({"editHostActionParam": {
                "addInitiatorParam": {"initiator": add_init_list}}})
        elif new_name:
            edit_host_data = {"editHostActionParam": {
                "renameHostParam": {"new_host_name": new_name}}}
        else:
            msg = ("No modify host parameters chosen - please supply one "
                   "of the following: host_flag_dict, remove_init_list, "
                   "add_init_list, or new_name.")
            raise exception.InvalidInputException(data=msg)
        return self.modify_resource(
            self.array_id, SLOPROVISIONING, 'host', payload=edit_host_data,
            resource_name=host_id)

    def delete_host(self, host_id):
        """Delete a given host.

        Cannot delete if associated with a masking view.

        :param host_id: name of the host
        """
        self.delete_resource(self.array_id, SLOPROVISIONING, 'host',
                             resource_name=host_id)

    def get_mvs_from_host(self, host_id):
        """Retrieve masking view information for a specified host.

        :param host_id: the name of the host
        :return: list of masking views
        """
        mv_list = []
        host_details = self.get_host(host_id)
        if host_details and host_details.get('maskingview'):
            mv_list = host_details["maskingview"]
        return mv_list

    def get_initiator_ids_from_host(self, host_id):
        """Get initiator details from a host.

        :param host_id: the name of the host
        :return: list of initiator IDs
        """
        initiator_list = []
        host_details = self.get_host(host_id)
        if host_details and host_details.get('initiator'):
            initiator_list = host_details["initiator"]
        return initiator_list

    def get_hostgroup(self, hostgroup_id):
        """Get details on a hostgroup on the array.

        :param hostgroup_id: the name of the hostgroup
        :return: dict
        """
        return self.get_resource(self.array_id, SLOPROVISIONING, 'hostgroup',
                                 resource_name=hostgroup_id)

    def get_hostgroup_list(self, filters=None):
        """Get list of hostgroup(s) on the array.

        See unisphere documentation for applicable filters.

        :param filters: optional list of filters - dict
        :return: dict
        """
        response = self.get_resource(
            self.array_id, SLOPROVISIONING, 'hostgroup', params=filters)
        hostgroup_list = response.get('hostGroupId', []) if response else []
        return hostgroup_list

    def create_hostgroup(self, hostgroup_id, host_list,
                         host_flags=None, _async=False):
        """Create a hostgroup containing the given hosts.

        :param hostgroup_id: the name of the new hostgroup
        :param host_list: list of hosts
        :param host_flags: dictionary of optional host flags to apply
        :param _async: Flag to indicate if call should be async
        :return: dict
        """
        new_ig_data = ({"hostId": host_list, "hostGroupId": hostgroup_id})
        if host_flags:
            new_ig_data.update({"hostFlags": host_flags})
        if _async:
            new_ig_data.update(ASYNC_UPDATE)
        return self.create_resource(self.array_id, SLOPROVISIONING,
                                    'hostgroup', payload=new_ig_data)

    def modify_hostgroup(self, hostgroup_id, host_flag_dict=None,
                         remove_host_list=None, add_host_list=None,
                         new_name=None):
        """Modify an existing hostgroup.

        Only one parameter can be modified at a time.

        :param hostgroup_id: the name of the hostgroup
        :param host_flag_dict: dictionary of host flags
        :param remove_host_list: list of hosts to be removed
        :param add_host_list: list of hosts to be added
        :param new_name: new name of the hostgroup
        :return: dict
        """
        if host_flag_dict:
            edit_host_data = ({"editHostGroupActionParam": {
                "setHostGroupFlagsParam": {"hostFlags": host_flag_dict}}})
        elif remove_host_list:
            edit_host_data = ({"editHostGroupActionParam": {
                "removeHostParam": {"host": remove_host_list}}})
        elif add_host_list:
            edit_host_data = ({"editHostGroupActionParam": {
                "addHostParam": {"host": add_host_list}}})
        elif new_name:
            edit_host_data = {"editHostGroupActionParam": {
                "renameHostGroupParam": {"new_host_group_name": new_name}}}
        else:
            msg = ("No modify hostgroup parameters chosen - please supply "
                   "one of the following: host_flag_dict, "
                   "remove_host_list, add_host_list, or new_name.")
            raise exception.InvalidInputException(data=msg)
        return self.modify_resource(
            self.array_id, SLOPROVISIONING, 'hostgroup',
            payload=edit_host_data, resource_name=hostgroup_id)

    def delete_hostgroup(self, hostgroup_id):
        """Delete a given hostgroup.

        Cannot delete if associated with a masking view.

        :param hostgroup_id: name of the hostgroup
        """
        self.delete_resource(self.array_id, SLOPROVISIONING,
                             'hostgroup', resource_name=hostgroup_id)

    def get_initiator(self, initiator_id):
        """Get details of an initiator.

        :param initiator_id: initiator id, optional
        :return: initiator details
        """
        return self.get_resource(self.array_id, SLOPROVISIONING, 'initiator',
                                 resource_name=initiator_id)

    def get_initiator_list(self, params=None):
        """Retrieve initiator list from the array.

        :param params: dict of optional params
        :returns: list of initiators
        """
        response = self.get_resource(
            self.array_id, SLOPROVISIONING, 'initiator', params=params)
        init_list = response.get('initiatorId', []) if response else []
        return init_list

    def modify_initiator(self, initiator_id, remove_masking_entry=None,
                         replace_init=None, rename_alias=None,
                         set_fcid=None, initiator_flags=None):
        """Modify an initiator.

        Only one parameter can be edited at a time.

        :param initiator_id: the initiator id
        :param remove_masking_entry: string - "true" or "false"
        :param replace_init: Id of the new initiator
        :param rename_alias: tuple ('new node name', 'new port name')
        :param set_fcid: set fcid value - string
        :param initiator_flags: dictionary of initiator flags to set
        :return: dict
        """
        if remove_masking_entry:
            edit_init_data = ({"editInitiatorActionParam": {
                "removeMaskingEntry": remove_masking_entry}})
        elif replace_init:
            edit_init_data = ({"editInitiatorActionParam": {
                "replaceInitiatorParam": {"new_initiator": replace_init}}})
        elif rename_alias:
            edit_init_data = ({"editInitiatorActionParam": {
                "renameAliasParam": {"port_name": rename_alias[0],
                                     "node_name": rename_alias[1]}}})
        elif set_fcid:
            edit_init_data = ({"editInitiatorActionParam": {
                "initiatorSetAttributesParam": {"fcidValue": set_fcid}}})
        elif initiator_flags:
            edit_init_data = ({"editInitiatorActionParam": {
                "initiatorSetFlagsParam": {
                    "initiatorFlags": initiator_flags}}})
        else:
            msg = ("No modify initiator parameters chosen - please supply "
                   "one of the following: removeMaskingEntry, "
                   "replace_init, rename_alias, set_fcid, "
                   "initiator_flags.")
            raise exception.InvalidInputException(data=msg)
        return self.modify_resource(
            self.array_id, SLOPROVISIONING, 'initiator',
            payload=edit_init_data, resource_name=initiator_id)

    def is_initiator_in_host(self, initiator):
        """Check to see if a given initiator is already assigned to a host.

        :param initiator: the initiator ID
        :returns: bool
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

        :returns: list of in-use initiators
        """
        params = {'in_a_host': 'true'}
        return self.get_initiator_list(params)

    def get_initiator_group_from_initiator(self, initiator):
        """Given an initiator, get its corresponding initiator group, if any.

        :param initiator: the initiator id
        :returns: found_init_group_name -- string, or None
        """
        init_details = self.get_initiator(initiator)
        found_ig_name = init_details.get('host') if init_details else None
        return found_ig_name

    def get_masking_view_list(self, filters=None):
        """Get a masking view or list of masking views.

        See unisphere documentation for possible filters.

        :param filters: dictionary of filters
        :return: list of masking views
        """
        response = self.get_resource(
            self.array_id, SLOPROVISIONING, 'maskingview', params=filters)
        masking_view_list = response.get(
            'maskingViewId', []) if response else []
        return masking_view_list

    def get_masking_view(self, masking_view_name):
        """Get details of a masking view.

        :param masking_view_name: the masking view name
        :returns: masking view dict
        """
        return self.get_resource(
            self.array_id, SLOPROVISIONING,
            'maskingview', resource_name=masking_view_name)

    def create_masking_view_existing_components(
            self, port_group_name, masking_view_name,
            storage_group_name, host_name=None,
            host_group_name=None, _async=False):
        """Create a new masking view using existing groups.

        Must enter either a host name or a host group name, but
        not both.

        :param port_group_name: name of the port group
        :param masking_view_name: name of the new masking view
        :param storage_group_name: name of the storage group
        :param host_name: name of the host (initiator group)
        :param host_group_name: name of host group
        :param _async: flag to indicate if command should be run asynchronously
        :return: dict
        :raises: InvalidInputException
        """
        if host_name:
            host_details = {"useExistingHostParam": {"hostId": host_name}}
        elif host_group_name:
            host_details = {"useExistingHostGroupParam": {
                "hostGroupId": host_group_name}}
        else:
            msg = "Must enter either a host name or a host group name"
            raise exception.InvalidInputException(data=msg)
        payload = ({
            "portGroupSelection": {
                "useExistingPortGroupParam": {
                    "portGroupId": port_group_name}},
            "maskingViewId": masking_view_name,
            "hostOrHostGroupSelection": host_details,
            "storageGroupSelection": {
                "useExistingStorageGroupParam": {
                    "storageGroupId": storage_group_name}}})
        if _async:
            payload.update(ASYNC_UPDATE)

        return self.create_resource(
            self.array_id, SLOPROVISIONING, 'maskingview', payload=payload)

    def get_masking_views_from_storage_group(self, storagegroup):
        """Return any masking views associated with a storage group.

        :param storagegroup: the storage group name
        :returns: masking view list
        """
        storagegroup = self.get_storage_group(storagegroup)
        return storagegroup.get('maskingview', []) if storagegroup else []

    def get_masking_views_by_host(self, initiatorgroup_name):
        """Given a host (initiator group), retrieve the masking view name.

        Retrieve the list of masking views associated with the
        given initiator group.

        :param initiatorgroup_name: the name of the initiator group
        :returns: list of masking view names
        """
        ig_details = self.get_host(initiatorgroup_name)
        masking_view_list = ig_details.get(
            'maskingview', []) if ig_details else []
        return masking_view_list

    def get_element_from_masking_view(
            self, maskingview_name, portgroup=False, host=False,
            storagegroup=False):
        """Return the name of the specified element from a masking view.

        :param maskingview_name: the masking view name
        :param portgroup: the port group name - optional
        :param host: the host name - optional
        :param storagegroup: the storage group name - optional
        :returns: name of the specified element -- string
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
            exception_message = "Error retrieving masking group."
            raise exception.ResourceNotFoundException(
                data=exception_message)
        return element

    def get_common_masking_views(self, portgroup_name, ig_name):
        """Get common masking views for a given portgroup and initiator group.

        :param portgroup_name: the port group name
        :param ig_name: the initiator group name
        :returns: masking view list
        """
        params = {'port_group_name': portgroup_name,
                  'host_or_host_group_name': ig_name}
        return self.get_masking_view_list(params)

    def delete_masking_view(self, maskingview_name):
        """Delete a masking view.

        :param maskingview_name: the masking view name
        """
        self.delete_resource(
            self.array_id, SLOPROVISIONING, 'maskingview',
            resource_name=maskingview_name)

    def rename_masking_view(self, masking_view_id, new_name):
        """Rename an existing masking view.

        Currently, the only supported modification is "rename".

        :param masking_view_id: the current name of the masking view
        :param new_name: the new name of the masking view
        :return: dict
        """
        mv_payload = {"editMaskingViewActionParam": {
            "renameMaskingViewParam": {"new_masking_view_name": new_name}}}
        return self.modify_resource(
            self.array_id, SLOPROVISIONING, 'maskingview', payload=mv_payload,
            version='', resource_name=masking_view_id)

    def get_host_from_maskingview(self, masking_view_id):
        """Given a masking view, get the associated host or host group.

        :param masking_view_id: the name of the masking view
        :return: host ID
        """
        return self.get_element_from_masking_view(masking_view_id, host=True)

    def get_storagegroup_from_maskingview(self, masking_view_id):
        """Given a masking view, get the associated storage group.

        :param masking_view_id: the masking view name
        :return: the name of the storage group
        """
        return self.get_element_from_masking_view(
            masking_view_id, storagegroup=True)

    def get_portgroup_from_maskingview(self, masking_view_id):
        """Given a masking view, get the associated port group.

        :param masking_view_id: the masking view name
        :return: the name of the port group
        """
        return self.get_element_from_masking_view(
            masking_view_id, portgroup=True)

    def get_maskingview_connections(self, mv_name, filters=None):
        """Get all connection information for a given masking view.

        :param mv_name: the name of the masking view
        :param filters: dict of optional filter parameters
        :return: list of masking view connection dicts
        """
        res_name = "%s/connections" % mv_name
        response = self.get_resource(
            self.array_id, SLOPROVISIONING,
            'maskingview', resource_name=res_name, params=filters)
        mv_conn_list = response.get(
            'maskingViewConnection') if response else []
        return mv_conn_list

    def find_host_lun_id_for_vol(self, maskingview, device_id):
        """Find the host_lun_id for a volume in a masking view.

        :param maskingview: the masking view name
        :param device_id: the device ID
        :returns: host_lun_id -- int
        """
        host_lun_id = None
        filters = {'volume_id': device_id}
        connection_info = self.get_maskingview_connections(
            maskingview, filters)
        if len(connection_info) == 0:
            LOG.error("Cannot retrieve masking view connection information "
                      "for %(device_id)s in %(maskingview)s.",
                      {'device_id': device_id,
                       'maskingview': maskingview})
        else:
            try:
                host_lun_id = (connection_info[0]['host_lun_address'])
                host_lun_id = int(host_lun_id, 16)
            except Exception as e:
                LOG.error("Unable to retrieve connection information "
                          "for volume %(vol)s in masking view %(mv)s. "
                          "Exception received: %(e)s.",
                          {'vol': device_id, 'mv': maskingview,
                           'e': e})
        return host_lun_id

    def get_port_list(self, filters=None):
        """Query for a list of Symmetrix port keys.

        Note a mixture of Front end, back end and RDF port specific values
        are not allowed. See UniSphere documentation for possible values.

        :param filters: dictionary of filters e.g. {'vnx_attached': 'true'}
        :returns: list of port key dicts
        """
        response = self.get_resource(
            self.array_id, SLOPROVISIONING, 'port', params=filters)
        port_key_list = response.get(
            'symmetrixPortKey', []) if response else []
        return port_key_list

    def get_portgroup(self, portgroup_id):
        """Get portgroup details.

        :param portgroup_id: the name of the portgroup
        :return: dict
        """
        return self.get_resource(self.array_id, SLOPROVISIONING, 'portgroup',
                                 resource_name=portgroup_id)

    def get_portgroup_list(self, filters=None):
        """Get portgroup details.

        :param filters: dict of optional filters
        :return: list of portgroups
        """
        response = self.get_resource(self.array_id, SLOPROVISIONING,
                                     'portgroup', params=filters)
        port_group_list = response.get('portGroupId', []) if response else []
        return port_group_list

    def get_ports_from_pg(self, portgroup):
        """Get a list of port identifiers from a port group.

        :param portgroup: the name of the portgroup
        :returns: list of port ids, e.g. ['FA-3D:35', 'FA-4D:32']
        """
        portlist = []
        portgroup_info = self.get_portgroup(portgroup)
        if portgroup_info and portgroup_info.get("symmetrixPortKey"):
            port_key = portgroup_info["symmetrixPortKey"]
            for key in port_key:
                port = key['portId']
                portlist.append(port)
        return portlist

    def get_target_wwns_from_pg(self, portgroup_id):
        """Get the director ports' wwns.

        :param portgroup_id: the name of the portgroup
        :returns: target_wwns -- the list of target wwns for the pg
        """
        target_wwns = []
        port_ids = self.get_ports_from_pg(portgroup_id)
        for port in port_ids:
            dir_id = port.split(':')[0]
            port_no = port.split(':')[1]
            wwn = self.get_port_identifier(dir_id, port_no)
            target_wwns.append(wwn)
        return target_wwns

    def get_iscsi_ip_address_and_iqn(self, port_id):
        """Get the ip addresses from the director port.

        :param port_id: the director port identifier
        :returns: (list of ip_addresses, iqn)
        """
        ip_addresses, iqn = [], None
        dir_id = port_id.split(':')[0]
        port_no = port_id.split(':')[1]
        port_details = self.get_director_port(dir_id, port_no)
        if port_details:
            try:
                ip_addresses = port_details['symmetrixPort']['ip_addresses']
                iqn = port_details['symmetrixPort']['identifier']
            except (KeyError, TypeError):
                pass
        return ip_addresses, iqn

    def create_portgroup(self, portgroup_id, director_id, port_id):
        """Create a new portgroup.

        :param portgroup_id: the name of the new port group
        :param director_id: the directoy id
        :param port_id: the port id
        :return: dict
        """
        payload = ({"portGroupId": portgroup_id,
                    "symmetrixPortKey": [{"directorId": director_id,
                                          "portId": port_id}]})
        return self.create_resource(
            self.array_id, SLOPROVISIONING, 'portgroup', payload=payload)

    def create_multiport_portgroup(self, portgroup_id, ports):
        """Create a new portgroup.

        :param portgroup_id: the name of the new port group
        :param ports: list of port dicts - {"directorId": director_id,
                                            "portId": port_id}
        :return: dict
        """
        payload = ({"portGroupId": portgroup_id,
                    "symmetrixPortKey": ports})
        return self.create_resource(
            self.array_id, SLOPROVISIONING, 'portgroup', payload=payload)

    def create_portgroup_from_file(self, file_name, portgroup_id):
        """Given a file with director:port pairs, create a portgroup.

        Each director:port pair must be on a new line.
        Example director:port - FA-1D:4.

        :param file_name: the path to the file
        :param portgroup_id: the name for the portgroup
        :return: dict, status_code
        """
        port_list = self.common.create_list_from_file(file_name)
        combined_payload = []
        for i in port_list:
            current_director_id, current_port_id = i.split(":")
            temp_list = {'directorId': current_director_id,
                         'portId': current_port_id}
            combined_payload.append(temp_list)

        return self.create_multiport_portgroup(portgroup_id, combined_payload)

    def modify_portgroup(self, portgroup_id, remove_port=None, add_port=None,
                         rename_portgroup=None):
        """Modify an existing portgroup.

        Only one parameter can be modified at a time.

        :param portgroup_id: the name of the portgroup
        :param remove_port: tuple of port details ($director_id, $portId)
        :param add_port: tuple of port details ($director_id, $portId)
        :param rename_portgroup: new portgroup name
        :return: dict
        """
        if remove_port:
            edit_pg_data = ({"editPortGroupActionParam": {"removePortParam": {
                "port": [{"directorId": remove_port[0],
                          "portId": remove_port[1]}]}}})
        elif add_port:
            edit_pg_data = ({"editPortGroupActionParam": {"addPortParam": {
                "port": [{"directorId": add_port[0],
                          "portId": add_port[1]}]}}})
        elif rename_portgroup:
            edit_pg_data = ({"editPortGroupActionParam": {
                "renamePortGroupParam": {
                    "new_port_group_name": rename_portgroup}}})
        else:
            message = ("No modify portgroup parameters set - please set one "
                       "of the following: remove_port, add_port, or "
                       "rename_portgroup.")
            raise exception.InvalidInputException(data=message)
        return self.modify_resource(
            self.array_id, SLOPROVISIONING, 'portgroup', payload=edit_pg_data,
            resource_name=portgroup_id)

    def delete_portgroup(self, portgroup_id):
        """Delete a portgroup.

        :param portgroup_id: the name of the portgroup
        """
        self.delete_resource(self.array_id, SLOPROVISIONING,
                             'portgroup', resource_name=portgroup_id)

    def get_slo_list(self, filters=None):
        """Retrieve the list of slo's from the array.

        :returns: slo_list -- list of service level names
        """
        slo_dict = self.get_resource(
            self.array_id, SLOPROVISIONING, 'slo', params=filters)
        slo_list = slo_dict.get('sloId', []) if slo_dict else []
        return slo_list

    def get_slo(self, slo_id):
        """Get details on a specific service level.

        :param slo_id: the service level agreement
        :return: dict
        """
        return self.get_resource(self.array_id, SLOPROVISIONING, 'slo',
                                 resource_name=slo_id)

    def modify_slo(self, slo_id, new_name):
        """Modify an SLO.

        Currently, the only modification permitted is renaming.

        :param slo_id: the current name of the slo
        :param new_name: the new name for the slo
        :return: dict
        """
        edit_slo_data = ({"editSloActionParam": {
            "renameSloParam": {"sloId": new_name}}})
        return self.modify_resource(
            self.array_id, SLOPROVISIONING, 'host', payload=edit_slo_data,
            resource_name=slo_id)

    def get_srp(self, srp):
        """Get details on a specific SRP.

        :param srp: the storage resource pool
        :returns: dict
        """
        return self.get_resource(self.array_id, SLOPROVISIONING, 'srp',
                                 resource_name=srp)

    def get_srp_list(self, filters=None):
        """Get a list of available SRP's on a given array.

        :param filters: optional dict of filter parameters
        :returns: list
        """
        response = self.get_resource(
            self.array_id, SLOPROVISIONING, 'srp', params=filters)
        srp_list = response.get('srpId', []) if response else []
        return srp_list

    def get_compressibility_report(self, srp_id):
        """Get a specified SRP Compressibility Report.

        :param srp_id: the srp id
        :returns: list of compressibility reports
        """
        res_name = "%s/compressibility_report" % srp_id
        response = self.get_resource(
            self.array_id, SLOPROVISIONING, 'srp', resource_name=res_name)
        report_list = response.get(
            'storageGroupCompressibility', []) if response else []
        return report_list

    def is_compression_capable(self):
        """Check if array is compression capable.

        :returns: bool
        """
        array_list = self.common.get_v3_or_newer_array_list(
            filters={'compressionCapable': 'true'})
        return True if self.array_id in array_list else False

    def get_storage_group(self, storage_group_name):
        """Given a name, return storage group details.

        :param storage_group_name: the name of the storage group
        :returns: storage group dict
        """
        return self.get_resource(
            self.array_id, SLOPROVISIONING, 'storagegroup',
            resource_name=storage_group_name)

    def get_storage_group_demand_report(self):
        """Get the storage group demand report.

        Get the storage group demand report from Unisphere.
        Functionality only available in unisphere 9.0
        assumes single SRP SRP_1
        :returns: returns report
        """
        return self.get_resource(
            self.array_id, SLOPROVISIONING, 'srp',
            resource_name="SRP_1/storage_group_demand_report")

    def get_storage_group_list(self, filters=None):
        """Return a list of storage groups.

        :param filters: optional filter parameters
        :returns: storage group list
        """
        sg_details = self.get_resource(
            self.array_id, SLOPROVISIONING, 'storagegroup', params=filters)
        sg_list = sg_details.get('storageGroupId', []) if sg_details else []
        return sg_list

    def get_mv_from_sg(self, storage_group):
        """Get the associated masking views from a given storage group.

        :param storage_group: the name of the storage group
        :return: Masking view list
        """
        response = self.get_storage_group(storage_group)
        maskingview_list = response.get('maskingview', []) if response else []
        return maskingview_list

    def get_num_vols_in_sg(self, storage_group_name):
        """Get the number of volumes in a storage group.

        :param storage_group_name: the storage group name
        :returns: num_vols -- int
        """
        storagegroup = self.get_storage_group(storage_group_name)
        num_vols = (int(storagegroup['num_of_vols']) if storagegroup and (
            storagegroup.get('num_of_vols')) else 0)
        return num_vols

    def is_child_sg_in_parent_sg(self, child_name, parent_name):
        """Check if a child storage group is a member of a parent group.

        :param child_name: the child sg name
        :param parent_name: the parent sg name
        :returns: bool
        """
        parent_sg = self.get_storage_group(parent_name)
        if parent_sg and parent_sg.get('child_storage_group'):
            child_sg_list = parent_sg['child_storage_group']
            if child_name in child_sg_list:
                return True
        return False

    def get_child_sg_from_parent(self, parent_name):
        """Get child storage group list.

        :param parent_name: the parent sg name
        :returns: list
        """
        child_list = []
        parent_sg = self.get_storage_group(parent_name)
        if parent_sg and parent_sg.get('child_storage_group'):
            return parent_sg['child_storage_group']
        return child_list

    def create_storage_group(self, srp_id, sg_id, slo, workload=None,
                             do_disable_compression=False,
                             num_vols=0, vol_size="0", cap_unit="GB",
                             allocate_full=False, _async=False, vol_name=None):
        """Create the volume in the specified storage group.

        :param srp_id: the SRP (String)
        :param sg_id: the group name (String)
        :param slo: the SLO (String)
        :param workload: the workload (String)
        :param do_disable_compression: flag for disabling compression
        :param num_vols: number of volumes to be created
        :param vol_size: the volume size
        :param cap_unit: the capacity unit (MB, GB, TB, CYL)
        :param allocate_full: boolean to indicate if you want a thick volume
        :param async: Flag to indicate if call should be async
        :param vol_name: name to give to the volume, optional
        :returns: dict
        """
        srp_id = srp_id if slo else "None"
        payload = ({"srpId": srp_id,
                    "storageGroupId": sg_id,
                    "emulation": "FBA"})

        if slo:
            slo_param = {"num_of_vols": num_vols,
                         "sloId": slo,
                         "workloadSelection": workload,
                         "volumeAttribute": {
                             "volume_size": vol_size,
                             "capacityUnit": cap_unit}}
            if do_disable_compression:
                slo_param.update({"noCompression": "true"})
            elif self.is_compression_capable():
                slo_param.update({"noCompression": "false"})
            if vol_name:
                slo_param.update({
                    "volumeIdentifier": {
                        "identifier_name": vol_name,
                        "volumeIdentifierChoice": "identifier_name"}})

            if allocate_full:
                # If case of full volume allocation, we must set the
                # noCompression parameter at true because fully
                # allocations and compression are exclusive parameters
                slo_param.update({"noCompression": "true"})
                slo_param.update({"allocate_capacity_for_each_vol": "true"})
                slo_param.update({"persist_preallocated_capacity_through_"
                                  "reclaim_or_copy": "true"})

            payload.update({"sloBasedStorageGroupParam": [slo_param]})

        if _async:
            payload.update(ASYNC_UPDATE)

        return self.create_resource(
            self.array_id, SLOPROVISIONING, 'storagegroup', payload=payload)

    def create_non_empty_storagegroup(
            self, srp_id, sg_id, slo, workload, num_vols, vol_size,
            cap_unit, disable_compression=False, _async=False):
        """Create a new storage group with the specified volumes.

        Generates a dictionary for json formatting and calls the
        create_sg function to create a new storage group with the
        specified volumes. Set the disable_compression flag for
        disabling compression on an All Flash array (where compression
        is on by default).

        :param srp_id: the storage resource pool
        :param sg_id: the name of the new storage group
        :param slo: the service level agreement (e.g. Gold)
        :param workload: the workload (e.g. DSS)
        :param num_vols: the amount of volumes to be created -- int
        :param vol_size: the size of each volume -- string
        :param cap_unit: the capacity unit (MB, GB)
        :param disable_compression: Flag for disabling compression (AF only)
        :param _async: Flag to indicate if this call should be async
        :return: dict
        """
        return self.create_storage_group(
            srp_id, sg_id, slo, workload,
            do_disable_compression=disable_compression,
            num_vols=num_vols, vol_size=vol_size, cap_unit=cap_unit,
            _async=_async)

    def create_empty_sg(self, srp_id, sg_id, slo, workload,
                        disable_compression=False, _async=False):
        """Create an empty storage group.

        Set the disable_compression flag for disabling compression
        on an All Flash array (where compression is on by default).

        :param srp_id: the storage resource pool
        :param sg_id: the name of the new storage group
        :param slo: the service level agreement (e.g. Gold)
        :param workload: the workload (e.g. DSS)
        :param disable_compression: flag for disabling compression (AF only)
        :param _async: Flag to indicate if this call should be asyncronously
        executed
        :return: dict
        """
        return self.create_storage_group(
            srp_id, sg_id, slo, workload,
            do_disable_compression=disable_compression, _async=_async)

    def modify_storage_group(self, storagegroup, payload):
        """Modify a storage group (PUT operation).

        :param storagegroup: storage group name
        :param payload: the request payload
        :returns: message -- dict, server response
        """
        return self.modify_resource(
            self.array_id, SLOPROVISIONING, 'storagegroup',
            payload=payload, resource_name=storagegroup)

    def add_existing_vol_to_sg(self, sg_id, vol_ids, _async=False):
        """Expand an existing storage group by adding existing volumes.

        :param sg_id: the name of the storage group
        :param vol_ids: the device id of the volume - can be list
        :param _async: Flag to indicate if the call should be async
        :return: dict
        """
        if not isinstance(vol_ids, list):
            vol_ids = [vol_ids]
        add_vol_data = {"editStorageGroupActionParam": {
            "expandStorageGroupParam": {
                "addSpecificVolumeParam": {
                    "volumeId": vol_ids}}}}
        if _async:
            add_vol_data.update(ASYNC_UPDATE)
        return self.modify_storage_group(sg_id, add_vol_data)

    def add_new_vol_to_storagegroup(self, sg_id, num_vols, vol_size,
                                    cap_unit, _async=False, vol_name=None,
                                    create_new_volumes=None):
        """Expand an existing storage group by adding new volumes.

        :param sg_id: the name of the storage group
        :param num_vols: the number of volumes
        :param vol_size: the size of the volumes
        :param cap_unit: the capacity unit
        :param _async: Flag to indicate if call should be async
        :param vol_name: name to give to the volume, optional
        :param create_new_volumes: when true will force create new
        volumes, optional
        :return: dict
        """
        add_vol_info = {
            "num_of_vols": num_vols,
            "emulation": "FBA",
            "volumeAttribute": {
                "volume_size": vol_size,
                "capacityUnit": cap_unit}}
        if vol_name:
            add_vol_info.update({
                "volumeIdentifier": {
                    "identifier_name": vol_name,
                    "volumeIdentifierChoice": "identifier_name"}})
        expand_sg_data = {"editStorageGroupActionParam": {
            "expandStorageGroupParam": {
                "addVolumeParam": add_vol_info}}}
        if not create_new_volumes:
            add_vol_info.update({
                "create_new_volumes": False})
        if _async:
            expand_sg_data.update(ASYNC_UPDATE)
        return self.modify_storage_group(sg_id, expand_sg_data)

    def remove_vol_from_storagegroup(self, sg_id, vol_id, _async=False):
        """Remove a volume from a given storage group.

        :param sg_id: the name of the storage group
        :param vol_id: the device id of the volume
        :param _async: Flag to indicate if call should be async
        :return: dict
        """
        if not isinstance(vol_id, list):
            vol_id = [vol_id]
        payload = {"editStorageGroupActionParam": {
            "removeVolumeParam": {"volumeId": vol_id}}}
        if _async:
            payload.update(ASYNC_UPDATE)
        return self.modify_storage_group(sg_id, payload)

    def move_volumes_between_storage_groups(
            self, device_ids, source_storagegroup_name,
            target_storagegroup_name, force=False, _async=False):
        """Move volumes to a different storage group.

        Note: 8.4.0.7 or later

        :param source_storagegroup_name: the originating storage group name
        :param target_storagegroup_name: the destination storage group name
        :param device_ids: the device ids - can be list
        :param force: force flag (necessary if volume is in masking view)
        :param _async: _async flag
        """
        force_flag = "true" if force else "false"
        if not isinstance(device_ids, list):
            device_ids = [device_ids]
        payload = ({
            "editStorageGroupActionParam": {
                "moveVolumeToStorageGroupParam": {
                    "volumeId": device_ids,
                    "storageGroupId": target_storagegroup_name,
                    "force": force_flag}}})
        if _async:
            payload.update(ASYNC_UPDATE)
        return self.modify_storage_group(source_storagegroup_name, payload)

    def create_volume_from_sg_return_dev_id(
            self, volume_name, storagegroup_name,
            vol_size, cap_unit='GB'):
        """Create a new volume in the given storage group.

        :param volume_name: the volume name (String)
        :param storagegroup_name: the storage group name
        :param vol_size: volume size (String)
        :param cap_unit: the capacity unit, default 'GB'
        :returns: device_id
        """
        job = self.add_new_vol_to_storagegroup(
            storagegroup_name, 1, vol_size, cap_unit,
            _async=True, vol_name=volume_name)

        task = self.common.wait_for_job("Create volume from sg", 202, job)

        # Find the newly created volume.
        device_id = None
        if task:
            for t in task:
                try:
                    desc = t["description"]
                    if CREATE_VOL_STRING in desc:
                        t_list = desc.split()
                        device_id = t_list[(len(t_list) - 1)]
                        device_id = device_id[1:-1]
                        break
                    if device_id:
                        self.get_volume(device_id)
                except Exception as e:
                    LOG.info("Could not retrieve device id from job. "
                             "Exception received was %(e)s. Attempting "
                             "retrieval by volume_identifier.",
                             {'e': e})

        if not device_id:
            device_id = self.find_volume_device_id(volume_name)

        return device_id

    def add_child_sg_to_parent_sg(self, child_sg, parent_sg):
        """Add a storage group to a parent storage group.

        This method adds an existing storage group to another storage
        group, i.e. cascaded storage groups.

        :param child_sg: the name of the child sg
        :param parent_sg: the name of the parent sg
        """
        payload = {"editStorageGroupActionParam": {
            "expandStorageGroupParam": {
                "addExistingStorageGroupParam": {
                    "storageGroupId": [child_sg]}}}}
        return self.modify_storage_group(parent_sg, payload)

    def remove_child_sg_from_parent_sg(self, child_sg, parent_sg):
        """Remove a storage group from its parent storage group.

        This method removes a child storage group from its parent group.

        :param child_sg: the name of the child sg
        :param parent_sg: the name of the parent sg
        """
        payload = {"editStorageGroupActionParam": {
            "removeStorageGroupParam": {
                "storageGroupId": [child_sg], "force": 'true'}}}
        return self.modify_storage_group(parent_sg, payload)

    def update_storagegroup_qos(self, storage_group_name, qos_specs):
        """Update the storagegroupinstance with qos details.

        If maxIOPS or maxMBPS is in qos_specs, then DistributionType can be
        modified in addition to maxIOPS or/and maxMBPS
        If maxIOPS or maxMBPS is NOT in qos_specs, we check to see if
        either is set in StorageGroup. If so, then DistributionType can be
        modified. Example qos specs:
        {'maxIOPS': '4000', 'maxMBPS': '4000', 'DistributionType': 'Dynamic'}.

        :param storage_group_name: the storagegroup instance name
        :param qos_specs: the qos specifications
        :returns: dict
        """
        message = None
        sg_details = self.get_storage_group(storage_group_name)
        sg_qos_details = None
        sg_maxiops = None
        sg_maxmbps = None
        sg_distribution_type = None
        maxiops = "nolimit"
        maxmbps = "nolimit"
        distribution_type = "Never"
        propertylist = []
        try:
            sg_qos_details = sg_details['hostIOLimit']
            sg_maxiops = sg_qos_details['host_io_limit_io_sec']
            sg_maxmbps = sg_qos_details['host_io_limit_mb_sec']
            sg_distribution_type = sg_qos_details['dynamicDistribution']
        except KeyError:
            LOG.debug("Unable to get storage group QoS details.")
        if 'maxIOPS' in qos_specs:
            maxiops = qos_specs['maxIOPS']
            if maxiops != sg_maxiops:
                propertylist.append(maxiops)
        if 'maxMBPS' in qos_specs:
            maxmbps = qos_specs['maxMBPS']
            if maxmbps != sg_maxmbps:
                propertylist.append(maxmbps)
        if 'DistributionType' in qos_specs and (
                propertylist or sg_qos_details):
            dynamic_list = ['never', 'onfailure', 'always']
            if (qos_specs.get('DistributionType').lower() not
                    in dynamic_list):
                exception_message = (
                    "Wrong Distribution type value %(dt)s entered. "
                    "Please enter one of: %(dl)s" %
                    {'dt': qos_specs.get('DistributionType'),
                     'dl': dynamic_list})
                LOG.error(exception_message)
                raise exception.InvalidInputException(
                    data=exception_message)
            else:
                distribution_type = qos_specs['DistributionType']
                if distribution_type != sg_distribution_type:
                    propertylist.append(distribution_type)
        if propertylist:
            payload = {"editStorageGroupActionParam": {
                "setHostIOLimitsParam": {
                    "host_io_limit_io_sec": maxiops,
                    "host_io_limit_mb_sec": maxmbps,
                    "dynamicDistribution": distribution_type}}}
            message = (
                self.modify_storage_group(storage_group_name, payload))
        return message

    def set_host_io_limit_iops_or_mbps(
            self, storage_group, iops, dynamic_distribution, mbps=None):
        """Set the HOSTIO Limits on an existing storage group.

        :param storage_group: String up to 32 Characters
        :param dynamic_distribution: valid values Always, Never, OnFailure
        :param iops: integer value. Min Value 100, must be specified to
                     nearest 100, e.g.202 is not a valid value
        :param mbps: MB per second, integer value. Min Value 100
        :return: dict
        """
        qos_specs = {'maxIOPS': iops,
                     'DistributionType': dynamic_distribution}
        if mbps:
            qos_specs.update({'maxMBPS': mbps})
        return self.update_storagegroup_qos(storage_group, qos_specs)

    def delete_storagegroup(self, storagegroup_id):
        """Delete a given storage group.

        A storage group cannot be deleted if it
        is associated with a masking view.

        :param storagegroup_id: the name of the storage group
        """
        self.delete_resource(
            self.array_id, SLOPROVISIONING, 'storagegroup',
            resource_name=storagegroup_id)

    def get_volume(self, device_id):
        """Get a VMAX volume from array.

        :param device_id: the volume device id
        :returns: volume dict
        """
        return self.get_resource(
            self.array_id, SLOPROVISIONING, 'volume', resource_name=device_id)

    def get_volume_list(self, filters=None):
        """Get list of volumes from array.

        :param filters: optional dictionary of filters
        :return: list of device ids
        """
        vol_id_list = []
        response = self.get_resource(
            self.array_id, SLOPROVISIONING, 'volume', params=filters)
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

    def get_vol_effective_wwn_details_84(self, vol_list):
        """Get the effective wwn for a list of vols.

        Get volume details for a list of volume device ids,
        and write results to a csv file.

        :param vol_list: list of device ids
        :return: Dictionary
        """
        # Create CSV and set headings
        with open(bytes('wwn_data.csv', 'UTF-8'), 'wt') as csvfile:
            eventwriter = csv.writer(csvfile,
                                     delimiter=',',
                                     quotechar='|',
                                     quoting=csv.QUOTE_MINIMAL)

            eventwriter.writerow(['volumeId', 'effective_wwn', 'wwn',
                                  'has_effective_wwn', 'storageGroupId'])
        for device_id in vol_list:
            voldetails = self.get_volume(device_id)
            effective_wwn = voldetails.get('effective_wwn')
            wwn = voldetails.get('wwn')
            has_effective_wwn = voldetails.get('has_effective_wwn')
            storage_group_id = voldetails.get('storageGroupId')
            with open(bytes('wwn_data.csv', 'UTF-8'), 'a') as csvfile:
                eventwriter = csv.writer(csvfile,
                                         delimiter=',',
                                         quotechar='|',
                                         quoting=csv.QUOTE_MINIMAL)
                eventwriter.writerow([device_id, effective_wwn, wwn,
                                      has_effective_wwn, storage_group_id])

    def get_vols_from_storagegroup(self, storagegroup_id):
        """Retrieve volume information associated with a particular sg.

        :param storagegroup_id: the name of the storage group
        :return: list of device IDs of associated volumes
        """
        params = {"storageGroupId": storagegroup_id}

        volume_list = self.get_volume_list(params)
        if len(volume_list) == 0:
            LOG.debug("Cannot find record for storage group %(sg_id)s",
                      {'sg_id': storagegroup_id})
        return volume_list

    def get_storagegroup_from_vol(self, vol_id):
        """Retrieve sg information for a specified volume.

        :param vol_id: the device ID of the volume
        :return: list of storage groups
        """
        vol = self.get_volume(vol_id)
        sg_list = vol.get('storageGroupId', []) if vol else []
        return sg_list

    def is_volume_in_storagegroup(self, device_id, storagegroup):
        """See if a volume is a member of the given storage group.

        :param device_id: the device id
        :param storagegroup: the storage group name
        :returns: bool
        """
        is_vol_in_sg = False
        sg_list = self.get_storagegroup_from_vol(device_id)
        if storagegroup in sg_list:
            is_vol_in_sg = True
        return is_vol_in_sg

    def find_volume_device_id(self, volume_name):
        """Given a volume identifier, find the corresponding device_id.

        :param volume_name: the volume name
        :returns: device_id
        """
        device_id = None
        params = {"volume_identifier": volume_name}

        volume_list = self.get_volume_list(params)
        if not volume_list:
            LOG.debug("Cannot find record for volume %(volumeId)s.",
                      {'volumeId': volume_name})
        else:
            device_id = volume_list[0]
        return device_id

    def find_volume_identifier(self, device_id):
        """Get the volume identifier of a VMAX volume.

        :param device_id: the device id
        :returns: the volume identifier -- string
        """
        vol = self.get_volume(device_id)
        return vol.get('volume_identifier', None) if vol else None

    def get_size_of_device_on_array(self, device_id):
        """Get the size of the volume from the array.

        :param device_id: the volume device id
        :returns: size
        """
        vol = self.get_volume(device_id)
        if vol and vol.get('cap_gb'):
            cap = vol['cap_gb']
        else:
            exception_message = ("Unable to retrieve size of device "
                                 "%s on the array" % device_id)
            raise exception.ResourceNotFoundException(data=exception_message)
        return cap

    def _modify_volume(self, device_id, payload):
        """Modify a volume (PUT operation).

        :param device_id: volume device id
        :param payload: the request payload
        """
        return self.modify_resource(self.array_id, SLOPROVISIONING, 'volume',
                                    payload=payload, resource_name=device_id)

    def extend_volume(self, device_id, new_size, _async=False):
        """Extend a VMAX volume.

        :param device_id: volume device id
        :param new_size: the new required size for the device
        :param _async: flag to indicate if call should be async
        """
        extend_vol_payload = {"editVolumeActionParam": {
            "expandVolumeParam": {
                "volumeAttribute": {
                    "volume_size": new_size,
                    "capacityUnit": "GB"}}}}
        if _async:
            extend_vol_payload.update(ASYNC_UPDATE)
        return self._modify_volume(device_id, extend_vol_payload)

    def rename_volume(self, device_id, new_name):
        """Rename a volume.

        :param device_id: the volume device id
        :param new_name: the new name for the volume
        """
        if new_name is not None:
            vol_identifier_dict = {
                "identifier_name": new_name,
                "volumeIdentifierChoice": "identifier_name"}
        else:
            vol_identifier_dict = {"volumeIdentifierChoice": "none"}
        rename_vol_payload = {"editVolumeActionParam": {
            "modifyVolumeIdentifierParam": {
                "volumeIdentifier": vol_identifier_dict}}}
        return self._modify_volume(device_id, rename_vol_payload)

    def deallocate_volume(self, device_id):
        """Deallocate all tracks on a volume.

        Necessary before deletion. Please note that it is not possible
        to know exactly when a deallocation is complete. This method
        will return when the array has accepted the request for deallocation;
        the deallocation itself happens as a background task on the array.

        :param device_id: the device id
        :return: dict
        """
        payload = {"editVolumeActionParam": {
            "freeVolumeParam": {"free_volume": 'true'}}}
        return self._modify_volume(device_id, payload)

    def delete_volume(self, device_id):
        """Delete a volume.

        :param device_id: volume device id
        """
        self.delete_resource(
            self.array_id, SLOPROVISIONING, "volume", resource_name=device_id)

    def find_low_volume_utilization(self, low_utilization_percentage, csvname):
        """Find volumes under a certain utilization threshold.

        Function to find volumes under a specified percentage,
        (e.g. find volumes with utilization less than 10%) - may be long
        running as will check all sg on array and all storage group.  Only
        identifies volumes in storage group,  note if volume is in more
        than one sg it may show up more than once.

        :param low_utilization_percentage: low utilization watermark percent
        :param csvname: filename for CFV output file
        :return: will create csvfile with name passed
        """
        sg_list = self.get_storage_group_list()

        with open(bytes(csvname, 'UTF-8'), 'w', newline='') as csvfile:
            eventwriter = csv.writer(csvfile,
                                     delimiter=',',
                                     quotechar='|',
                                     quoting=csv.QUOTE_MINIMAL)

            eventwriter.writerow(["sgname", "volumeid", "identifier",
                                  "capacity", "allocated_Percent"])

            for sg in sg_list:
                vollist = self.get_vols_from_storagegroup(sg)

                for vol in vollist:
                    volume = self.get_volume(vol)
                    vol_identifier = "No Identifier"
                    if (volume["allocated_percent"] < (
                            low_utilization_percentage)):
                        allocated = volume["allocated_percent"]
                        if volume.get("volume_identifier"):
                            vol_identifier = (volume["volume_identifier"])
                        vol_cap = (volume["cap_gb"])
                        eventwriter.writerow(
                            [sg, vol, vol_identifier, vol_cap, allocated])

    def get_workload_settings(self):
        """Get valid workload options from array.

        :returns: workload_setting -- list of workload names
        """
        wl_details = self.get_resource(
            self.array_id, SLOPROVISIONING, 'workloadtype')
        wl_setting = wl_details.get('workloadId', []) if wl_details else []
        return wl_setting
