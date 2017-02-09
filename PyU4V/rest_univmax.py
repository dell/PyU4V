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

try:
    import ConfigParser as Config
except ImportError:
    import configparser as Config
import logging.config
from PyU4V.rest_requests import RestRequests
import time

# register configuration file
LOG = logging.getLogger('PyU4V')
CONF_FILE = 'PyU4V.conf'
logging.config.fileConfig(CONF_FILE)
CFG = Config.ConfigParser()
CFG.read(CONF_FILE)

# HTTP constants
GET = 'GET'
POST = 'POST'
PUT = 'PUT'
DELETE = 'DELETE'


class rest_functions:
    def __init__(self, username=None, password=None, server_ip=None,
                 port=None, verify=False, cert=None):
        self.array_id = CFG.get('setup', 'array')
        if not username:
            username = CFG.get('setup', 'username')
        if not password:
            password = CFG.get('setup', 'password')
        if not server_ip:
            server_ip = CFG.get('setup', 'server_ip')
        if not port:
            port = CFG.get('setup', 'port')
        if not verify:
            verify = CFG.getboolean('setup', 'verify')
        if not cert:
            cert = CFG.get('setup', 'cert')
        base_url = 'https://%s:%s/univmax/restapi' % (server_ip, port)
        self.rest_client = RestRequests(username, password, verify,
                                        cert, base_url)

    def set_array(self, array):
        """Change to a different array.

        :param array: The VMAX serial number
        """
        self.array_id = array

    def close_session(self):
        """Close the current rest session
        """
        self.rest_client.close_session()

    ###############################
    # system functions
    ###############################

    def get_all_alerts(self, filters=None):
        """Queries for a list of All Alert ids across all symmetrix arrays.

        Optionally can be filtered by: create_date_milliseconds(=<>),
        description(=<>), type, severity, state, created_date, acknowledged.
        :param filters: dict of filters - optional
        :return: dict, status_code
        """
        target_uri = "univmax/restapi/system/alert"
        return self.rest_client.rest_request(target_uri, GET, filters)

    def get_all_jobs(self, filters=None):
        """Queries for a list of Job ids across all symmetrix arrays.

        Optionally can be filtered by: scheduled_date, name, completed_date,
        username, scheduled_date_milliseconds,
        last_modified_date_milliseconds, last_modified_date,
        completed_date_milliseconds (all params including =,<, or >),
        status (=).
        :param filters: dict of filters - optional
        :return: dict, status_code
        """
        target_uri = "/system/job"
        return self.rest_client.rest_request(target_uri, GET, params=filters)

    def get_symmetrix_array(self, array_id=None):
        """Returns a list of arrays, or details on a specific array.

        :param array_id: the array serial number
        :return: dict, status_code
        """
        target_uri = "/system/symmetrix"
        if array_id:
            target_uri += "/%s" % array_id
        return self.rest_client.rest_request(target_uri, GET)

    def get_array_jobs(self, jobID=None, filters=None):
        """Call queries for a list of Job ids for the specified symmetrix.

        The optional filters are: scheduled_date, name, completed_date,
        username, scheduled_date_milliseconds,
        last_modified_date_milliseconds, last_modified_date,
        completed_date_milliseconds (all params including =,<, or >),
        status (=).
        :param jobID: specific ID of the job (optional)
        :param filters: dict of filters - optional
        :return: dict, status_code
        """
        target_uri = "/system/symmetrix/%s/job" % self.array_id
        if jobID:
            target_uri += "/%s" % jobID
        if jobID and filters:
            LOG.error("jobID and filters are mutually exclusive options")
            raise Exception
        return self.rest_client.rest_request(target_uri, GET, params=filters)

    def get_array_alerts(self, alert_id=None, filters=None):
        """Queries for a list of Alert ids for the specified symmetrix.

        The optional filters are: create_date_milliseconds(=<>),
        description(=<>), type, severity, state, created_date, acknowledged.
        :param alert_id: specific id of the alert - optional
        :param filters: dict of filters - optional
        :return: dict, status_code
        """
        target_uri = "/system/symmetrix/%s/alert" % self.array_id
        if alert_id:
            target_uri += "/%s" % alert_id
        if alert_id and filters:
            LOG.error("alert_id and filters are mutually exclusive options")
            raise Exception
        return self.rest_client.rest_request(target_uri, GET, params=filters)

    def acknowledge_array_alert(self, alert_id):
        """Acknowledge a specified alert.

        Acknowledge is the only "PUT" (edit) option available.
        :param alert_id: the alert id - string
        :return: dict, status_code
        """
        target_uri = ("/system/symmetrix/%s/alert/%s" %
                      (self.array_id, alert_id))
        payload = {"editAlertActionParam": "ACKNOWLEDGE"}
        return self.rest_client.rest_request(target_uri, PUT,
                                             request_object=payload)

    def delete_alert(self, alert_id):
        """Delete a specified alert.

        :param alert_id: the alert id - string
        :return: None, status code
        """
        target_uri = ("/system/symmetrix/%s/alert/%s" %
                      (self.array_id, alert_id))
        return self.rest_client.rest_request(target_uri, DELETE)

    def get_uni_version(self):
        target_uri = "/system/version"
        return self.rest_client.rest_request(target_uri, GET)

    #############################
    ### SLOProvisioning functions
    #############################

    # director

    def get_director(self, director=None):
        """Queries for details of Symmetrix directors for a symmetrix

        :param director: the director ID e.g. FA-1D - optional
        :return: dict, status_code
        """
        target_uri = "/sloprovisioning/symmetrix/%s/director" % self.array_id
        if director:
            target_uri += "/%s" % director
        return self.rest_client.rest_request(target_uri, GET)

    def get_director_port(self, director, port_no=None, filters=None):
        """Get details of the symmetrix director port.

        Can be filtered by optional parameters, please see documentation.
        :param director: the director ID e.g. FA-1D
        :param port_no: the port number e.g. 1 - optional
        :param filters: optional filters - dict
        :return: dict, status_code
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/director/%s/port"
                      % (self.array_id, director))
        if port_no:
            target_uri += "/%s" % port_no
        if port_no and filters:
            LOG.error("portNo and filters are mutually exclusive options")
            raise Exception
        return self.rest_client.rest_request(target_uri, GET, params=filters)

    def get_port_identifier(self, director, port_no):
        """Get the identifier (if wwn or iqn) of the physical port.

        :param director: the ID of the director
        :param port_no: the number of the port
        :return: wwn (FC) or iqn (iscsi), or None
        """
        info, sc = self.get_director_port(director, port_no)
        try:
            identifier = info["symmetrixPort"][0]["identifier"]
            return identifier
        except KeyError:
            LOG.error("Cannot retrieve port information")
            return None

    # host

    def get_hosts(self, host_id=None, filters=None):
        """Get details on host(s) on the array.

        See documentation for applicable filters - only valid
        if no host is specified.
        :param host_id: the name of the host, optional
        :param filters: optional list of filters - dict
        :return: dict, status_code
        """
        target_uri = "/sloprovisioning/symmetrix/%s/host" % self.array_id
        if host_id:
            target_uri += "/%s" % host_id
        if host_id and filters:
            LOG.error("Host_id and filters are mutually exclusive options")
            raise Exception
        return self.rest_client.rest_request(target_uri, GET, filters)

    def create_host(self, host_name, initiator_list, host_flags=None):
        """Create a host with the given initiators.

        The initiators must not be associated with another host.
        :param host_name: the name of the new host
        :param initiator_list: list of initiators
        :param host_flags: dictionary of optional host flags to apply
        :return: dict, status_code
        """
        target_uri = "/sloprovisioning/symmetrix/%s/host" % self.array_id
        new_ig_data = ({"hostId": host_name, "initiatorId": initiator_list})
        if host_flags:
            new_ig_data.update({"hostFlags": host_flags})
        return self.rest_client.rest_request(target_uri, POST,
                                             request_object=new_ig_data)

    def modify_host(self, host_id, host_flag_dict=None,
                    remove_init_list=None, add_init_list=None, new_name=None):
        """Modify an existing host.

        Only one parameter can be modified at a time.
        :param host_id: the host name
        :param host_flag_dict: dictionary of host flags
        :param remove_init_list: list of initiators to be removed
        :param add_init_list: list of initiators to be added
        :param new_name: new host name
        :return: dict, status_code
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
            LOG.error("No modify host parameters chosen - please supply one "
                      "of the following: host_flag_dict, remove_init_list, "
                      "add_init_list, or new_name.")
            raise Exception
        target_uri = ("/sloprovisioning/symmetrix/%s/host/%s"
                      % (self.array_id, host_id))
        return self.rest_client.rest_request(target_uri, PUT,
                                             request_object=edit_host_data)

    def delete_host(self, host_id):
        """Delete a given host.

        Cannot delete if associated with a masking view
        :param host_id: name of the host
        :return: dict, status_code
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/host/%s"
                      % (self.array_id, host_id))
        return self.rest_client.rest_request(target_uri, DELETE)

    def get_mvs_from_host(self, host_id):
        """Retrieve masking view information for a specified host.

        :param host_id: the name of the host
        :return: list of masking views or None
        """
        response, sc = self.get_hosts(host_id=host_id)
        try:
            mv_list = response["host"][0]["maskingview"]
            return mv_list
        except KeyError:
            LOG.debug("No masking views found for host %s." % host_id)
            return None

    def get_initiator_ids_from_host(self, host_id):
        """Get initiator details from a host.

        :param host_id: the name of the host
        :return: list of initiator IDs, or None
        """
        response, sc = self.get_hosts(host_id=host_id)
        try:
            initiator_list = response["host"][0]["initiator"]
            return initiator_list
        except KeyError:
            return None

    # hostgroup

    def get_hostgroups(self, hostgroup_id=None, filters=None):
        """Get details on hostgroup(s) on the array.

        See unisphere documentation for applicable filters - only valid
        if no host is specified.
        :param hostgroup_id: the name of the hostgroup, optional
        :param filters: optional list of filters - dict
        :return: dict, status_code
        """
        target_uri = "/sloprovisioning/symmetrix/%s/hostgroup" % self.array_id
        if hostgroup_id:
            target_uri += "/%s" % hostgroup_id
        if hostgroup_id and filters:
            LOG.error("hostgroup_id and filters are mutually exclusive "
                      "options")
            raise Exception
        return self.rest_client.rest_request(target_uri, GET, filters)

    def create_hostgroup(self, hostgroup_id, host_list, host_flags=None):
        """Create a hostgroup containing the given hosts.

        :param hostgroup_id: the name of the new hostgroup
        :param host_list: list of hosts
        :param host_flags: dictionary of optional host flags to apply
        :return: dict, status_code
        """
        target_uri = "/sloprovisioning/symmetrix/%s/hostgroup" % self.array_id
        new_ig_data = ({"hostId": host_list, "hostGroupId": hostgroup_id})
        if host_flags:
            new_ig_data.update({"hostFlags": host_flags})
        return self.rest_client.rest_request(target_uri, POST,
                                             request_object=new_ig_data)

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
        :return: dict, status_code
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
            LOG.error("No modify hostgroup parameters chosen - please supply "
                      "one of the following: host_flag_dict, "
                      "remove_host_list, add_host_list, or new_name.")
            raise Exception
        target_uri = ("/sloprovisioning/symmetrix/%s/hostgroup/%s"
                      % (self.array_id, hostgroup_id))
        return self.rest_client.rest_request(target_uri, PUT,
                                             request_object=edit_host_data)

    def delete_hostgroup(self, hostgroup_id):
        """Delete a given hostgroup.

        Cannot delete if associated with a masking view
        :param hostgroup_id: name of the hostgroup
        :return: dict, status_code
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/hostgroup/%s"
                      % (self.array_id, hostgroup_id))
        return self.rest_client.rest_request(target_uri, DELETE)

    # initiators

    def get_initiators(self, initiator_id=None, filters=None):
        """Lists initiators on a given array.

        See UniSphere documenation for full list of filters.
        Can filter by initiator_id OR filters.
        :param filters: Optional filters - dict
        :return: initiator list
        """
        target_uri = "/sloprovisioning/symmetrix/%s/initiator" % self.array_id
        if initiator_id:
            target_uri += "/%s" % initiator_id
        if initiator_id and filters:
            LOG.error("Initiator_id and filters are mutually exclusive")
            raise Exception
        return self.rest_client.rest_request(target_uri, GET, params=filters)

    def modify_initiator(self, initiator_id, removeMaskingEntry=None,
                         replace_init=None, rename_alias=None,
                         set_fcid=None, initiator_flags=None):
        """Modify an initiator.

        Only one parameter can be edited at a time.
        :param initiator_id: the initiator id
        :param removeMaskingEntry: string - "true" or "false"
        :param replace_init: Id of the new initiator
        :param rename_alias: tuple ('new node name', 'new port name')
        :param set_fcid: set fcid value - string
        :param initiator_flags: dictionary of initiator flags to set
        :return: dict, status_code
        """
        if removeMaskingEntry:
            edit_init_data = ({"editInitiatorActionParam": {
                "removeMaskingEntry": removeMaskingEntry}})
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
            LOG.error("No modify initiator parameters chosen - please supply "
                      "one of the following: removeMaskingEntry, "
                      "replace_init, rename_alias, set_fcid, "
                      "initiator_flags.")
            raise Exception
        target_uri = ("/sloprovisioning/symmetrix/%s/initiator/%s"
                      % (self.array_id, initiator_id))
        return self.rest_client.rest_request(target_uri, PUT,
                                             request_object=edit_init_data)

    def is_initiator_in_host(self, initiator):
        """Check to see if a given initiator is already assigned to a host

        :param initiator: the initiator ID
        :return: bool
        """
        param = {'in_a_host': 'true', 'initiator_hba': initiator}
        response, sc = self.get_initiators(filters=param)
        try:
            if response['message'] == 'No Initiators Found':
                return False
        except KeyError:
            return True

    # masking view

    def get_masking_views(self, masking_view_id=None, filters=None):
        """Get a masking view or list of masking views.

        If masking_view_id, return details of a particular masking view.
        Either masking_view_id or filters can be set
        :param masking_view_id: the name of the masking view
        :param filters: dictionary of filters
        :return: dict, status_code
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/maskingview"
                      % self.array_id)
        if masking_view_id:
            target_uri += "/%s" % masking_view_id
        if masking_view_id and filters:
            LOG.error("masking_view_id and filters are mutually exclusive")
            raise Exception
        return self.rest_client.rest_request(target_uri, GET, params=filters)

    def create_masking_view_existing_components(
            self, port_group_name, masking_view_name,
            storage_group_name, host_name=None,
            host_group_name=None):
        """Create a new masking view using existing groups.

        Must enter either a host name or a host group name, but
        not both.
        :param port_group_name: name of the port group
        :param masking_view_name: name of the new masking view
        :param storage_group_name: name of the storage group
        :param host_name: name of the host (initiator group)
        :param host_group_name: name of host group
        :return: dict, status_code
        """
        if host_name:
            host_details = {"useExistingHostParam": {"hostId": host_name}}
        elif host_group_name:
            host_details = {"useExistingHostGroupParam": {
                "hostGroupId": host_group_name}}
        else:
            LOG.error("Must enter either a host name or a host group name")
            raise Exception()
        target_uri = ("/sloprovisioning/symmetrix/%s/maskingview"
                      % self.array_id)

        mv_payload = {"portGroupSelection": {
            "useExistingPortGroupParam": {
                "portGroupId": port_group_name}},
            "maskingViewId": masking_view_name,
            "hostOrHostGroupSelection": host_details,
            "storageGroupSelection": {
                "useExistingStorageGroupParam": {
                    "storageGroupId": storage_group_name}}}
        return self.rest_client.rest_request(target_uri, POST,
                                             request_object=mv_payload)

    def modify_masking_view(self, masking_view_id, new_name):
        """Modify an existing masking view.

        Currently, the only supported modification is "rename".
        :param masking_view_id: the current name of the masking view
        :param new_name: the new name of the masking view
        :return: dict, status_code
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/maskingview/%s"
                      % self.array_id, masking_view_id)
        mv_payload = {"editMaskingViewActionParam": {
            "renameMaskingViewParam": {"new_masking_view_name": new_name}}}
        return self.rest_client.rest_request(target_uri, PUT,
                                             request_object=mv_payload)

    def delete_masking_view(self, masking_view_id):
        """Delete a given masking view.

        :param masking_view_id: the name of the masking view
        :return: None, status code
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/maskingview/%s"
                      % (self.array_id, masking_view_id))
        return self.rest_client.rest_request(target_uri, DELETE)

    def get_host_from_mv(self, masking_view_id):
        """Given a masking view, get the associated host.

        :param masking_view_id: the name of the masking view
        :return: host ID
        """
        response, sc = self.get_masking_views(masking_view_id=masking_view_id)
        try:
            hostId = response['maskingView'][0]['hostId']
            return hostId
        except KeyError:
            LOG.error("Error retrieving host ID from masking view")

    def get_sg_from_mv(self, masking_view_id):
        """Given a masking view, get the associated storage group.

        :param masking_view_id: the masking view name
        :return: the name of the storage group
        """
        response, sc = self.get_masking_views(masking_view_id=masking_view_id)
        try:
            for r in response["maskingView"]:
                return r["storageGroupId"]
        except KeyError:
            LOG.error("Error retrieving storageGroupId from masking view")

    def get_pg_from_mv(self, masking_view_id):
        """Given a masking view, get the associated port group.

        :param masking_view_id: the masking view name
        :return: the name of the port group
        """
        response, sc = self.get_masking_views(masking_view_id=masking_view_id)
        try:
            for r in response["maskingView"]:
                return r["portGroupId"]
        except KeyError:
            LOG.error("Error retrieving portGroupId from masking view")

    def get_mv_connections(self, mv_name):
        """Get all connection information for a given masking view.

        :param mv_name: the name of the masking view
        :return: dict, status_code
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/maskingview/%s/"
                      "connections" % (self.array_id, mv_name))
        return self.rest_client.rest_request(target_uri, GET)

    # port

    def get_ports(self, filters=None):
        """Queries for a list of Symmetrix port keys.

        Note a mixture of Front end, back end and RDF port specific values
        are not allowed. See UniSphere documentation for possible values.
        :param filters: dictionary of filters e.g. {'vnx_attached': 'true'}
        :return: dict, status_code
        """
        target_uri = "/sloprovisioning/symmetrix/%s/port" % self.array_id
        return self.rest_client.rest_request(target_uri, GET, params=filters)

    # portgroup

    def get_portgroups(self, portgroup_id=None, filters=None):
        """Get portgroup(s) details.

        :param portgroup_id: the name of the portgroup
        :param filters: dictionary of filters
        :return: dict, status_code
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/portgroup"
                      % self.array_id)
        if portgroup_id:
            target_uri += "/%s" % portgroup_id
        if portgroup_id and filters:
            LOG.error("portgroup_id and filters are mutually exclusive")
            raise Exception
        return self.rest_client.rest_request(target_uri, GET, params=filters)

    def create_portgroup(self, portgroup_id, director_id, port_id):
        """Create a new portgroup.

        :param portgroup_id: the name of the new port group
        :param director_id: the directoy id
        :param port_id: the port id
        :return: dict, status_code
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/portgroup"
                      % self.array_id)
        pg_payload = ({"portGroupId": portgroup_id,
                       "symmetrixPortKey": [{"directorId": director_id,
                                             "portId": port_id}]})
        return self.rest_client.rest_request(target_uri, POST,
                                             request_object=pg_payload)

    def create_multiport_portgroup(self, portgroup_id, ports):
        """Create a new portgroup.

        :param portgroup_id: the name of the new port group
        :param ports: list of port dicts - {"directorId": director_id,
                                            "portId": port_id}
        :return: dict, status_code
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/portgroup"
                      % self.array_id)
        pg_payload = ({"portGroupId": portgroup_id,
                       "symmetrixPortKey": ports})
        return self.rest_client.rest_request(target_uri, POST,
                                             request_object=pg_payload)

    def create_list_from_file(self, file_name):
        """Given a file, create a list from its contents.

        :param file_name: the path to the file
        :return: list of contents
        """
        with open(file_name) as f:
            list_item = f.readlines()
        raw_list = map(lambda s: s.strip(), list_item)
        return list(raw_list)

    def create_portgroup_from_file(self, file_name, portgroup_id):
        """Given a file with director:port pairs, create a portgroup.

        e.g. FA-1D:4
             FA-1D:6
        Each director:port pair must be on a new line
        :param file_name: the path to the file
        :param portgroup_id: the name for the portgroup
        :return: dict, status_code
        """
        port_list = self.create_list_from_file(file_name)
        combined_payload = []
        for i in port_list:
            current_directorId, current_portId = i.split(":")
            temp_list = {}
            temp_list['directorId'] = current_directorId
            temp_list['portId'] = current_portId
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
        :return: dict, status_code
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
            LOG.error("No modify portgroup parameters set - please set one "
                      "of the following: remove_port, add_port, or "
                      "rename_portgroup.")
            raise Exception()
        target_uri = ("/sloprovisioning/symmetrix/%s/portgroup/%s"
                      % self.array_id, portgroup_id)
        return self.rest_client.rest_request(target_uri, PUT,
                                             request_object=edit_pg_data)

    def delete_portgroup(self, portgroup_id):
        """Delete a portgroup.

        :param portgroup_id: the name of the portgroup
        :return: dict, status_code
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/portgroup/%s"
                      % self.array_id, portgroup_id)
        return self.rest_client.rest_request(target_uri, DELETE)

    def extract_directorId_pg(self, portgroup):
        """Get the symm director information from the port group.

        :param portgroup: the name of the portgroup
        :return: the director information
        """
        info, sc = self.get_portgroups(portgroup_id=portgroup)
        try:
            portKey = info["portGroup"][0]["symmetrixPortKey"]
            return portKey
        except KeyError:
            LOG.error("Cannot find port key information from given portgroup")

    # SLO

    def get_SLO(self, SLO_Id=None):
        """Gets a list of available SLO's on a given array, or returns
        details on a specific SLO if one is passed in in the parameters.

        :param SLO_Id: the service level agreement, optional
        :return: dict, status_code
        """
        target_uri = "/sloprovisioning/symmetrix/%s/slo" % self.array_id
        if SLO_Id:
            target_uri += "/%s" % SLO_Id
        return self.rest_client.rest_request(target_uri, GET)

    def modify_slo(self, SLO_Id, new_name):
        """Modify an SLO.

        Currently, the only modification permitted is renaming.
        :param SLO_Id: the current name of the slo
        :param new_name: the new name for the slo
        :return: dict, status_code
        """
        edit_slo_data = ({"editSloActionParam": {
            "renameSloParam": {"sloId": new_name}}})
        target_uri = ("/sloprovisioning/symmetrix/%s/slo/%s" %
                      self.array_id, SLO_Id)
        return self.rest_client.rest_request(target_uri, PUT,
                                             request_object=edit_slo_data)

    # SRP

    def get_SRP(self, SRP=None):
        """Gets a list of available SRP's on a given array, or returns
        details on a specific SRP if one is passed in in the parameters.

        :param SRP: the storage resource pool, optional
        :return: dict, status_code
        """
        target_uri = "/sloprovisioning/symmetrix/%s/srp" % self.array_id
        if SRP:
            target_uri += "/%s" % SRP
        return self.rest_client.rest_request(target_uri, GET)

    # storage group functions.
    #  Note: Can only create a volume in relation to a sg

    def get_sg(self, sg_id=None, filters=None):
        """Gets details of all storage groups on a given array, or returns
        details on a specific sg if one is passed in in the parameters.

        :param sg_id: the storage group name, optional
        :param filters: dictionary of filters e.g.
                       {'child': 'true', 'srp_name': '=SRP_1'}
        :return: dict, status_code
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/storagegroup"
                      % self.array_id)
        if sg_id:
            target_uri += "/%s" % sg_id
        if sg_id and filters:
            LOG.error("sg_id and filters are mutually exclusive")
            raise Exception()
        return self.rest_client.rest_request(target_uri, GET)

    def create_non_empty_storagegroup(
            self, srpID, sg_id, slo, workload, num_vols, vol_size,
            capUnit, disable_compression=False):
        """Create a new storage group with the specified volumes.

        Generates a dictionary for json formatting and calls the
        create_sg function to create a new storage group with the
        specified volumes. Set the disable_compression flag for
        disabling compression on an All Flash array (where compression
        is on by default).
        :param srpID: the storage resource pool
        :param sg_id: the name of the new storage group
        :param slo: the service level agreement (e.g. Gold)
        :param workload: the workload (e.g. DSS)
        :param num_vols: the amount of volumes to be created
        :param vol_size: the size of each volume
        :param capUnit: the capacity unit (MB, GB)
        :param disable_compression: Flag for disabling compression (AF only)
        :return: dict, status_code
        """
        sg_params = {"sloId": slo, "workloadSelection": workload,
                     "volumeAttribute": {
                         "volume_size": vol_size,
                         "capacityUnit": capUnit},
                     "num_of_vols": num_vols, }
        if disable_compression:
            sg_params.update({"noCompression": 'true'})
        new_sg_data = ({"srpId": srpID,
                        "storageGroupId": sg_id,
                        "sloBasedStorageGroupParam": [sg_params]})
        if disable_compression:
            new_sg_data.update({"emulation": "FBA"})
            return self._create_sg_83(new_sg_data)
        else:
            return self._create_sg(new_sg_data)

    # create an empty storage group
    def create_empty_sg(self, srpID, sg_id, slo, workload,
                        disable_compression=False):
        """Generates a dictionary for json formatting and calls
        the create_sg function to create an empty storage group
        Set the disable_compression flag for
        disabling compression on an All Flash array (where compression
        is on by default).
        :param srpID: the storage resource pool
        :param sg_id: the name of the new storage group
        :param slo: the service level agreement (e.g. Gold)
        :param workload: the workload (e.g. DSS)
        :param disable_compression: flag for disabling compression (AF only)
        :return: dict, status_code
        """
        sg_params = {"sloId": slo, "workloadSelection": workload,
                     "volumeAttribute": {
                         "volume_size": "0",
                         "capacityUnit": "GB"},
                     "num_of_vols": 1, }
        if disable_compression:
            sg_params.update({"noCompression": "true"})
        new_sg_data = ({"srpId": srpID,
                        "storageGroupId": sg_id,
                        "sloBasedStorageGroupParam": [sg_params],
                        "create_empty_storage_group": "true"})
        if disable_compression:
            new_sg_data.update({"emulation": "FBA"})
            return self._create_sg_83(new_sg_data)
        else:
            return self._create_sg(new_sg_data)

    def _create_sg_83(self, new_sg_data):
        """Creates a new storage group with supplied specifications,
        given in dictionary form for json formatting

        :param new_sg_data: the payload of the request
        :return: dict, status_code
        """
        target_uri = ("/83/sloprovisioning/symmetrix/%s/storagegroup"
                      % self.array_id)
        return self.rest_client.rest_request(
            target_uri, POST, request_object=new_sg_data)

    def _create_sg(self, new_sg_data):
        """Creates a new storage group with supplied specifications,
        given in dictionary form for json formatting

        :param new_sg_data: the payload of the request
        :return: dict, status_code
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/storagegroup"
                      % self.array_id)
        return self.rest_client.rest_request(
            target_uri, POST, request_object=new_sg_data)

    def modify_storagegroup(self, sg_id, edit_sg_data):
        """Edits an existing storage group

        :param sg_id: the name of the storage group
        :param edit_sg_data: the payload of the request
        :return: dict, status_code
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/storagegroup/%s"
                      % (self.array_id, sg_id))
        return self.rest_client.rest_request(
            target_uri, PUT, request_object=edit_sg_data)

    def add_existing_vol_to_sg(self, sg_id, vol_id):
        """Expand an existing storage group by adding new volumes.

        :param sg_id: the name of the storage group
        :param vol_id: the device id of the volume
        :return: dict, status_code
        """
        addVolData = {"editStorageGroupActionParam": {
                                    "addVolumeParam": {
                                            "volumeId": [vol_id]}}}
        return self.modify_storagegroup(sg_id, addVolData)

    def add_new_vol_to_storagegroup(self, sg_id, num_vols, vol_size, capUnit):
        """Expand an existing storage group by adding new volumes.

        :param sg_id: the name of the storage group
        :param num_vols: the number of volumes
        :param vol_size: the size of the volumes
        :param capUnit: the capacity unit
        :return: dict, status_code
        """
        expand_sg_data = ({"editStorageGroupActionParam": {
            "expandStorageGroupParam": {
                "num_of_vols": num_vols, "volumeAttribute": {
                    "volume_size": vol_size, "capacityUnit": capUnit},
                "create_new_volumes": "true"
            }}})
        return self.modify_storagegroup(sg_id, expand_sg_data)

    def remove_vol_from_storagegroup(self, sg_id, volID):
        """Remove a volume from a given storage group

        :param sg_id: the name of the storage group
        :param volID: the device id of the volume
        :return: dict, status_code
        """
        del_vol_data = ({"editStorageGroupActionParam": {
            "removeVolumeParam": {
                "volumeId": [volID]}}})
        return self.modify_storagegroup(sg_id, del_vol_data)

    def delete_sg(self, sg_id):
        """Delete a given storage group.

        A storage group cannot be deleted if it
        is associated with a masking view
        :param sg_id: the name of the storage group
        :return: dict, status_code
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/storagegroup/%s"
                     % (self.array_id, sg_id))
        return self.rest_client.rest_request(target_uri, DELETE)

    def get_mv_from_sg(self, storageGroup):
        """Get the associated masking view(s) from a given storage group

        :param storageGroup: the name of the storage group
        :return: Masking view list, or None
        """
        response, sc = self.get_sg(storageGroup)
        mvlist = response["storageGroup"][0]["maskingview"]
        if len(mvlist) > 1:
            return mvlist
        else:
            return None

    def set_hostIO_limit_IOPS(self, storageGroup, IOPS, dynamicDistribution):
        """Set the HOSTIO Limits on an existing storage group.

        :param storageGroup: String up to 32 Characters
        :param dynamicDistribution: valid values Always, Never, OnFailure
        :param IOPS: integer value. Min Value 100, must be specified to 
                     nearest 100, e.g.202 is not a valid value
        :return: dict, status_code
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/storagegroup/%s"
                      % (self.array_id, storageGroup))
        iolimits = {"editStorageGroupActionParam": {
                        "setHostIOLimitsParam": {
                            "host_io_limit_io_sec": IOPS,
                            "dynamicDistribution": dynamicDistribution}}}
        return self.rest_client.rest_request(target_uri, PUT, request_object=iolimits)

    # volume

    def get_volumes(self, volID=None, filters=None):
        """Gets details of volume(s) from array.

        :param volID: the volume's device ID
        :param filters: dictionary of filters
        :return: dict, status_code
        """
        target_uri = "/sloprovisioning/symmetrix/%s/volume" % self.array_id
        if volID:
            target_uri += volID
        if volID and filters:
            LOG.error("volID and filters are mutually exclusive.")
            raise Exception()
        return self.rest_client.rest_request(target_uri, GET,
                                             params=filters)

    def delete_volume(self, vol_id):
        """Delete a specified volume off the array.
        Note that you cannot delete volumes with any associations/ allocations

        :param vol_id: the device ID of the volume
        :return: None, status_code
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/volume/%s"
                      % (self.array_id, vol_id))
        return self.rest_client.rest_request(target_uri, DELETE)

    def get_deviceId_from_volume(self, vol_identifier):
        """Given the volume identifier (name), return the device ID

        :param vol_identifier: the identifier of the volume
        :return: the device ID of the volume
        """
        response, sc = self.get_volumes(filters=(
            {'volume_identifier': vol_identifier}))
        result = response['resultList']['result'][0]
        return result['volumeId']

    def get_vols_from_SG(self, sgID):
        """Retrieve volume information associated with a particular sg

        :param sgID: the name of the storage group
        :return: list of device IDs of associated volumes
        """
        vols = []
        response, sc = self.get_volumes(filters={'storageGroupId': sgID})
        vol_list = response['resultList']['result']
        for vol in vol_list:
            vol_id = vol['volumeId']
            vols.append(vol_id)
        return vols

    def get_SG_from_vols(self, vol_id):
        """Retrieves sg information for a specified volume.

        Note that a FAST managed volume cannot be a
        member of more than one storage group.
        :param vol_id: the device ID of the volume
        :return: list of storage groups, or None
        """
        response, sc = self.get_volumes(volID=vol_id)
        try:
            sglist = response["volume"][0]["storageGroupId"]
            return sglist
        except KeyError:
            return None

    # workloadtype

    def get_workload(self):
        """Gets details of all available workload types.

        :return: dict, status_code
        """
        target_uri = ("/sloprovisioning/symmetrix/%s/workloadtype"
                      % self.array_id)
        return self.rest_client.rest_request(target_uri, GET)

    ###########################
    #   Replication functions
    ###########################

    def get_replication_info(self):
        """Return replication information for an array.

        :return: dict, status_code
        """
        target_uri = '/83/replication/symmetrix/%s' % self.array_id
        return self.rest_client.rest_request(target_uri, GET)
    # snapshots

    def check_snap_capabilities(self):
        """Check what replication facilities are available

        :return: dict, status_code
        """
        target_uri = "/replication/capabilities/symmetrix"
        return self.rest_client.rest_request(target_uri, GET)

    def get_snap_sg(self, sg_id):
        """get snapshot information on a particular sg

        :param sg_id: the name of the storage group
        :return: dict, status_code
        """
        target_uri = ("/replication/symmetrix/%s/storagegroup/%s/snapshot"
                      % (self.array_id, sg_id))
        return self.rest_client.rest_request(target_uri, GET)

    def get_snap_sg_generation(self, sg_id, snap_name):
        """Gets a snapshot and its generation count information for a Storage Group.
        The most recent snapshot will have a gen number of 0.
        The oldest snapshot will have a gen number = genCount - 1
        (i.e. if there are 4 generations of particular snapshot,
        the oldest will have a gen num of 3)

        :param sg_id: the name of the storage group
        :param snap_name: the name of the snapshot
        :return: dict, status_code
        """
        target_uri = ("/replication/symmetrix/%s/storagegroup/%s/snapshot/%s"
                      % (self.array_id, sg_id, snap_name))
        return self.rest_client.rest_request(target_uri, GET)

    def create_sg_snapshot(self, sg_id, snap_name):
        """Creates a new snapshot of a specified sg

        :param sg_id: the name of the storage group
        :param snap_name: the name of the snapshot
        :return: dict, status_code
        """
        target_uri = ("/replication/symmetrix/%s/storagegroup/%s/snapshot"
                      % (self.array_id, sg_id))
        snap_data = ({"snapshotName": snap_name})
        return self.rest_client.rest_request(
            target_uri, POST, request_object=snap_data)

    def create_sg_snapshot_83(self, sg_id, snap_name):
        """Creates a new snapshot of a specified sg

        :param sg_id: the name of the storage group
        :param snap_name: the name of the snapshot
        :return: dict, status_code
        """
        target_uri = ("/83/replication/symmetrix/%s/storagegroup/%s/snapshot"
                      % (self.array_id, sg_id))
        snap_data = ({"snapshotName": snap_name,
                      "daysToLive": 1
                      })
        return self.rest_client.rest_request(
            target_uri, POST, request_object=snap_data)


    def create_new_gen_snap(self, sg_id, snap_name):
        """Establish a new generation of a SnapVX snapshot for a source SG

        :param sg_id: the name of the storage group
        :param snap_name: the name of the existing snapshot
        :return: dict, status_code
        """
        target_uri = (
            "/replication/symmetrix/%s/storagegroup/%s/snapshot/%s/generation"
            % (self.array_id, sg_id, snap_name))
        data = ({})
        return self.rest_client.rest_request(target_uri, POST,
                                             request_object=data)

    def restore_snapshot(self, sg_id, snap_name, gen_num):
        """Restore a storage group to its snapshot

        :param sg_id: the name of the storage group
        :param snap_name: the name of the snapshot
        :param gen_num: the generation number of the snapshot (int)
        :return: dict, status_code
        """
        target_uri = ("/replication/symmetrix/%s/storagegroup/"
                      "%s/snapshot/%s/generation/%d"
                      % (self.array_id, sg_id, snap_name, gen_num))
        snap_data = ({"action": "Restore"})
        return self.rest_client.rest_request(target_uri, PUT,
                                             request_object=snap_data)

    def rename_gen_snapshot(self, sg_id, snap_name, gen_num, new_name):
        """Rename an existing storage group snapshot

        :param sg_id: the name of the storage group
        :param snap_name: the name of the snapshot
        :param gen_num: the generation number of the snapshot (int)
        :param new_name: the new name of the snapshot
        :return: dict, status_code
        """
        target_uri = ("/replication/symmetrix/%s/storagegroup/%s/"
                      "snapshot/%s/generation/%d"
                      % (self.array_id, sg_id, snap_name, gen_num))
        snap_data = ({"rename": {"newSnapshotName": new_name},
                      "action": "Rename"})
        return self.rest_client.rest_request(target_uri, PUT,
                                             request_object=snap_data)

    def link_gen_snapshot(self, sg_id, snap_name, gen_num, link_sg_name):
        """Link a snapshot to another storage group

        :param sg_id: Source storage group name
        :param snap_name: name of the snapshot
        :param gen_num: generation number of a snapshot (int)
        :param link_sg_name:  the target storage group name
        :return: dict, status_code
        """
        target_uri = ("/replication/symmetrix/%s/storagegroup/%s/"
                      "snapshot/%s/generation/%d"
                      % (self.array_id, sg_id, snap_name, gen_num))
        snap_data = ({{"action": "Link",
                       "link": {"linkStorageGroupName": link_sg_name},
                       }})
        return self.rest_client.rest_request(target_uri, PUT,
                                             request_object=snap_data)

    def set_snapshot_id(self,sgname):
        # simple function to parse a list of snaps for storage group and select from menu
        """
        :return:String returned with the name of the selected snapshot
        """
        snaplist = self.get_snap_sg(sgname)
        print(snaplist)
        i = 0
        for elem in snaplist[0]["name"]:
            print(i, " ", elem, "\n")
            i = int(i + 1)
        snapselection = input("Select the snapshot you want from the List \n")
        snapshot_id = (snaplist[0]["name"][int(snapselection)])
        return snapshot_id

    def link_gen_snapsthot_83(self, sg_id, snap_name, generation,link_sg_name ):
        """Creates a new snapshot of a specified sg
        83 version will automatically create linked SG if one of the specified name doesn't exist
        :param sg_id: Source storage group name
        :param snap_name: name of the snapshot
        :param gen_num: generation number of a snapshot (int)
        :param link_sg_name:  the target storage group name
        :return: dict, status_code
        """
        target_uri = ("/83/replication/symmetrix/%s/storagegroup/%s/snapshot/%s/generation/%s"
                      % (self.array_id, sg_id, snap_name, generation))
        snap_data = ({"link": {
            "linkStorageGroupName": link_sg_name
        },
            "action": "Link"})
        return self.rest_client.rest_request(
            target_uri, PUT, request_object=snap_data)


    def delete_sg_snapshot(self, sg_id, snap_name, gen_num):
        """Deletes a specified snapshot.
        Can only delete snap if generation number is known

        :param sg_id: name of the storage group
        :param snap_name: name of the snapshot
        :param gen_num: the generation number of the snapshot (int)
        :return: dict, status_code
        """
        target_uri = ("/replication/symmetrix/%s/storagegroup/"
                      "%s/snapshot/%s/generation/%d"
                      % (self.array_id, sg_id, snap_name, gen_num))
        return self.rest_client.rest_request(target_uri, DELETE)

    def get_replication_capabilities(self, array):
        """Check what replication features are licensed and enabled.

        :param array: the Symm array serial number
        :return: dict, status_code
        """
        target_uri = "/replication/capabilities/symmetrix/%s" % array
        return self.rest_client.rest_request(target_uri, GET)

    def is_snapvX_licensed(self, array):
        """Check if the snapVx feature is licensed and enabled.

        :param array: the Symm array serial number
        :return: True if licensed and enabled; False otherwise
        """
        snapCapability = False
        response, sc = self.get_replication_capabilities(array)
        try:
            symmList = response['symmetrixCapability']
            for symm in symmList:
                if symm['symmetrixId'] == array:
                    snapCapability = symm['snapVxCapable']
                    break
        except KeyError:
            LOG.error("Cannot access replication capabilities")
        return snapCapability

    # admissibility checks

    def get_wlp_timestamp(self):
        """Get the latest timestamp from WLP for processing New Worlkloads
        :return: dict, status_code
        """
        target_uri = ("/82/wlp/symmetrix/%s" % self.array_id)
        return self.rest_client.rest_request(target_uri, GET)

    def get_headroom(self,workload):
        """Get the Remaining Headroom Capacity
        :param workload:
        :return: dict, status_code (sample response
            {'headroom': [{'workloadType': 'OLTP',
            'headroomCapacity': 29076.34, 'processingDetails':
                {'lastProcessedSpaTimestamp': 1485302100000,
                'nextUpdate': 1670}, 'sloName': 'Diamond',
                'srp': 'SRP_1', 'emulation': 'FBA'}]})
        """
        target_uri = ("/82/wlp/symmetrix/%s/headroom?emulation=FBA&slo="
                      "Diamond&workloadtype=%s&srp=SRP_1"
                      % (self.array_id, workload))
        return self.rest_client.rest_request(target_uri, GET)

    def srdf_protect_sg(self, sg_id, remote_sid, srdfmode, establish=None):
        """

        :param sg_id: Unique string up to 32 Characters
        :param remote_sid: Type Integer 12 digit VMAX ID e.g. 000197000008
        :param srdfmode: String, values can be Active, AdaptiveCopyDisk,Synchronous,Asynchronous
        :param establish default is none, if passed value then we will use different
        :return: message and status Type JSON
        """
        target_uri = "/83/replication/symmetrix/%s/storagegroup/%s/rdf_group" \
                     % (self.array_id, sg_id)
        if establish:
            establish_sg = "True"
        else:
            establish_sg = "False"
        print(establish_sg)
        rdf_payload = ({"replicationMode": srdfmode,
                        "remoteSymmId": remote_sid,
                        "remoteStorageGroupName": sg_id,
                        "establish": establish_sg})
        print(rdf_payload)
        return self.rest_client.rest_request(target_uri, POST, request_object=rdf_payload)

    def get_srdf_num(self,sg_id):
        """Get the SRDF number for a storage group.

        :param sg_id: Storage Group Name of replicated group.
        :return:JSON dictionary Message and Status Sample returned
        {
          "storageGroupName": "REST_TEST_SG",
          "symmetrixId": "0001970xxxxx",
          "rdfgs": [
            4
          ]
        }
        """
        target_uri = ("/83/replication/symmetrix/%s/storagegroup/%s/rdf_group"
                     % (self.array_id, sg_id))
        return self.rest_client.rest_request(target_uri,GET)

    def get_srdf_state(self, sg_id, rdfg=None):
        """Get the current SRDF state.

        This may be a long running task depending on the size of the SRDF group,
        will switch to Async call when supported in 8.4 version of Unisphere.
        :param sg_id: name of storage group
        :param rdfg: Optional Parameter if SRDF group is known
        :return:
        """
        # Get a list of SRDF groups for storage group

        rdfg_list = self.get_srdf_num(sg_id)[0]["rdfgs"]
        # Sets the RDFG for the Get Call
        rdfg_num = rdfg_list[0]
        target_uri = ("/83/replication/symmetrix/%s/storagegroup/%s/rdf_group/%s"
                      % (self.array_id, sg_id, rdfg_num))

        return self.rest_client.rest_request(target_uri, GET)

    def change_srdf_state(self, sg_id, action, rdfg=None):
        """Modify the state of an srdf

        This may be a long running task depending on the size of the SRDF group,
        will switch to Async call when supported in 8.4 version of Unisphere.
        :param sg_id: name of storage group
        :param action
        :param rdfg: Optional Parameter if SRDF group is known
        :return:
        """
        # Get a list of SRDF groups for storage group
        rdfg_num = None
        rdfg_list = self.get_srdf_num(sg_id)[0]["rdfgs"]
        if len(rdfg_list) < 2:        # Check to see if RDF is cascaded.
            rdfg_num = rdfg_list[0]   # Sets the RDFG for the Put call to
        else:
            LOG.exception("Group is cascaded, functionality not yet added in "
                          "this python library")
        if rdfg_num:
            target_uri = ("/83/replication/symmetrix/%s/storagegroup/%s/rdf_group/%s"
                          % (self.array_id, sg_id, rdfg_num))
            action_payload = ({"action": action})
            return self.rest_client.rest_request(target_uri, PUT, request_object=action_payload)

    # Performance Metrics

    def get_fe_director_metrics(self,start_date, end_date, directorlist,
                                dataformat, metriclist):
        """Fuction to get one or more metrics for front end directors

        :param start_date: Date EPOCH Time in Milliseconds
        :param end_date: Date EPOCH Time in Milliseconds
        :param directorlist:List of FE Directors
        :param dataformat:Average or Maximum
        :param metriclist: Can contain a list of one or more of AvgWPDiscTime,
        AvgRDFSWriteResponseTime, AvgReadMissResponseTime ,PercentBusy,HostIOs,
        HostMBs, Reqs, ReadReqs, WriteReqs, HitReqs
        :return: JSON Payload, and RETURN CODE 200 for success
        """
        target_uri="/performance/FEDirector/metrics"
        feDirectorParam=({
                        "symmetrixId":self.array_id,
                        "directorId": directorlist,
                        "endDate": end_date,
                        "dataFormat": dataformat,
                        "metrics": metriclist,
                        "startDate": start_date
                         })

        return self.rest_client.rest_request(target_uri, POST,
                                             request_object=feDirectorParam)

    def get_fe_port_metrics(self, start_date, end_date, director_id,
                            port_id, dataformat, metriclist):
        """Function to get one or more Metrics for Front end Director ports

        :param start_date: Date EPOCH Time in Milliseconds
        :param end_date: Date EPOCH Time in Milliseconds
        :param directorlist: List of FE Directors
        :param dataformat:Average or Maximum
        :param metriclist: Can contain a list of one or more of PercentBusy,
        IOs, MBRead, MBWritten, MBs, AvgIOSize, SpeedGBs, MaxSpeedGBs,
        HostIOLimitIOs, HostIOLimitMBs
        :return: JSON Payload, and RETURN CODE 200 for success
        """
        target_uri = "/performance/FEPort/metrics"
        feDirectorParam = ({"symmetrixId": self.array_id,
                            "directorId": director_id,
                            "endDate": end_date,
                            "dataFormat": dataformat,
                            "metrics": [metriclist],
                            "portId": port_id,
                            "startDate": start_date})

        return self.rest_client.rest_request(target_uri, POST, request_object=feDirectorParam)

        ##################################
        # Collect VMAX Array level stats #
        ##################################

    def get_array_info(self):
        """Get array level information and performance metrics for a given VMAX Array ID

        :return: Combined payload of all metrics gathered from multiple REST calls
        """

        # Create array level target URIs
        array_info_uri = '/sloprovisioning/symmetrix/%s' % self.array_id
        perf_uri = '/performance/Array/metrics'

        # Set performance metrics payload
        # Removed XtremSWCacheMBs & PercentXtremSWCacheReadHits - no input response
        array_perf_payload = {
            'symmetrixId': self.array_id,
            'endDate': self.timestamp,
            'dataFormat': 'Average',
            'metrics': [
                'OverallCompressionRatio', 'OverallEfficiencyRatio', 'PercentVPSaved', 'VPSharedRatio',
                'VPCompressionRatio', 'VPEfficiencyRatio', 'PercentSnapshotSaved', 'SnapshotSharedRatio',
                'SnapshotCompressionRatio', 'SnapshotEfficiencyRatio', 'CopySlotCount', 'HostIOs', 'HostReads',
                'HostWrites', 'PercentReads', 'PercentWrites', 'PercentHit', 'HostMBs', 'HostMBReads',
                'HostMBWritten',
                'HostMBWritten', 'FEReqs', 'FEReadReqs', 'FEWriteReqs', 'BEIOs', 'BEReqs', 'BEReadReqs',
                'BEWriteReqs',
                'SystemWPEvents', 'DeviceWPEvents', 'WPCount', 'SystemMaxWPLimit', 'PercentCacheWP',
                'AvgFallThruTime',
                'FEHitReqs', 'FEReadHitReqs', 'FEWriteHitReqs', 'PrefetchedTracks', 'FEReadMissReqs',
                'FEWriteMissReqs',
                'ReadResponseTime', 'WriteResponseTime', 'OptimizedReadMisses',
                'OptimizedMBReadMisses', 'AvgOptimizedReadMissSize', 'QueueDepthUtilization',
                'InfoAlertCount', 'WarningAlertCount', 'CriticalAlertCount', 'RDFA_WPCount', 'AllocatedCapacity',
                'FE_Balance', 'DA_Balance', 'DX_Balance', 'RDF_Balance', 'Cache_Balance', 'SATA_Balance',
                'FC_Balance', 'EFD_Balance'
            ],
            'startDate': self.timestamp
        }

        # Perform all array level REST calls (get/post)
        array_info_payload = self.rest_client.rest_request(array_info_uri, GET)
        rep_info_payload = self.get_replication_info()
        workload_info_payload = self.get_workload()
        slo_info_payload = self.get_SLO()
        perf_payload = self.rest_client.rest_request(perf_uri, POST, request_object=array_perf_payload)

        # Set combined payload values not present in returned REST metrics
        combined_payload = dict()
        combined_payload['reporting_level'] = "Array"
        combined_payload['timestamp'] = self.timestamp
        combined_payload['symmetrixId'] = self.array_id

        # If no array level information is retrieved...
        if not array_info_payload:
            combined_payload['array_info_data'] = False
            combined_payload['array_info_msg'] = "No Array summary data available"
        else:
            # Array level information retrieved...
            for k, v in array_info_payload['symmetrix'][0].items():
                combined_payload[k] = v

            # Remove virtual capacity list, place contents at outer level
            del combined_payload['virtualCapacity']
            for k, v in array_info_payload['symmetrix'][0]['virtualCapacity'].items():
                key = 'virtual_%s' % k
                combined_payload[key] = v

            # Remove SL compliance list, place contents at outer level
            del combined_payload['sloCompliance']
            for k, v in array_info_payload['symmetrix'][0]['sloCompliance'].items():
                key = 'slo_compliance_%s' % k[4:]
                combined_payload[key] = v

        # If no array level replication information is retrieved...
        if not rep_info_payload:
            combined_payload['replication_info_data'] = False
            combined_payload['replication_info_msg'] = "No Array Replication info data available"
        else:
            # Replication metrics returned...
            for k, v in rep_info_payload.items():
                combined_payload[k] = v

        # If no array level workload information is retrieved...
        if not workload_info_payload:
            combined_payload['workload_info_data'] = False
            combined_payload['workload_info_msg'] = "No Array Workload info data available"
        else:
            # Workload metrics returned...
            for k, v in workload_info_payload.items():
                combined_payload[k] = v

        # If no array level SL information is retrieved...
        if not slo_info_payload:
            combined_payload['slo_info_data'] = False
            combined_payload['slo_info_msg'] = "No Array Service Level info data available"
        else:
            # SL metrics returned...
            for k, v in slo_info_payload.items():
                combined_payload[k] = v

        # If no array level performance information is retrieved...
        if not perf_payload:
            combined_payload['perf_data'] = False
            combined_payload['perf_msg'] = "No active Array performance data available"
        else:
            # Performance metrics returned...
            for k, v in perf_payload['resultList']['result'][0].items():
                combined_payload[k] = v

        # Rename all keys to common standardised format, dump to JSON

        self.rename_metrics(combined_payload)

        return combined_payload

    @staticmethod
    def rename_metrics(payload):
        """
        Takes the combined payload for any given VMAX reporting level, parses through each key
        and changes it to a standardised format. If a a metric has no returned value, the value is set to 'N/A'

        :param payload: The combined summary and performance metrics payload for a given
        VMAX reporting level
        """
        rename_list = {
            'AllocatedCapacity': 'allocated_capacity',
            'AsyncMBSent': 'async_mb_sent',
            'AsyncWriteReqs': 'async_write_reqs',
            'AvgFallThruTime': 'avg_fall_through_time',
            'AvgIOServiceTime': 'avg_io_service_time',
            'AvgIOSize': 'avg_io_size',
            'AvgIOSizeReceived': 'avg_io_size_received',
            'AvgIOSizeSent': 'avg_io_size_sent',
            'AvgOptimizedReadMissSize': 'avg_optimized_read_miss_size',
            'AvgRDFSWriteResponseTime': 'avg_rdfs_write_response_time',
            'AvgReadMissResponseTime': 'avg_read_miss_response_time',
            'AvgReadResponseTime6': 'avg_read_response_time_1',
            'AvgReadResponseTime7': 'avg_read_response_time_2',
            'AvgReadSize': 'avg_read_size',
            'AvgTimePerSyscall': 'avg_time_per_sys_call',
            'AvgWPDiscTime': 'avg_wp_disc_time',
            'AvgWritePacedDelay': 'avg_write_paced_delay',
            'AvgWriteResponseTime6': 'avg_write_response_time_1',
            'AvgWriteResponseTime7': 'avg_write_response_time_2',
            'AvgWriteSize': 'avg_write_size',
            'BEDiskReadResponseTime': 'be_disk_read_response_time',
            'BEIOs': 'be_ios',
            'BEMBReads': 'be_mb_reads',
            'BEMBTransferred': 'be_mb_transferred',
            'BEMBWritten': 'be_mb_written',
            'BEPercentReads': 'be_percent_reads',
            'BEPercentWrites': 'be_percent_writes',
            'BEPrefetchedMBs': 'be_prefetched_mbs',
            'BEPrefetchedTrackUsed': 'be_prefetched_track_used',
            'BEPrefetchedTrackss': 'be_prefetched_tracks',
            'BEReadReqs': 'be_read_reqs',
            'BEReadRequestTime': 'be_read_request_time',
            'BEReadTaskTime': 'be_read_task_time',
            'BEReqs': 'be_reqs',
            'BEWriteReqs': 'be_write_reqs',
            'BlockSize': 'block_size',
            'Cache_Balance': 'cache_balance',
            'CompressedMBs': 'compressed_mbs',
            'CompressedReadMBs': 'compressed_read_mbs',
            'CompressedReadReqs': 'compressed_read_reqs',
            'CompressedReqs': 'compressed_reqs',
            'CompressedTracks': 'compressed_tracks',
            'CompressedWriteMBs': 'compressed_write_mbs',
            'CompressedWriteReqs': 'compressed_write_reqs',
            'CompressionRatio': 'compression_ratio',
            'CopyIOs': 'copy_ios',
            'CopyMBs': 'copy_mbs',
            'CopySlotCount': 'copy_slot_count',
            'CriticalAlertCount': 'critical_alert_count',
            'DA_Balance': 'da_balance',
            'DX_Balance': 'dx_balance',
            'DeviceWPEvents': 'device_wp_events',
            'EFD_Balance': 'efd_balance',
            'FC_Balance': 'fc_balance',
            'FEHitReqs': 'fe_hit_reqs',
            'FEReadHitReqs': 'fe_read_hit_reqs',
            'FEReadMissReqs': 'fe_read_miss_reqs',
            'FEReadReqs': 'fe_read_reqs',
            'FEReqs': 'fe_reqs',
            'FEWriteHitReqs': 'fe_write_hit_reqs',
            'FEWriteMissReqs': 'fe_write_miss_reqs',
            'FEWriteReqs': 'fe_write_reqs',
            'FE_Balance': 'fe_balance',
            'HitReqs': 'hit_reqs',
            'HostHits': 'host_hits',
            'HostIOLimitIOs': 'host_io_limit_ios',
            'HostIOLimitMBs': 'host_io_limit_mbs',
            'HostIOLimitPercentTimeExceeded': 'host_io_limit_percent_time_exceeded',
            'HostIOs': 'host_ios',
            'HostMBReads': 'host_mb_reads',
            'HostMBWrites': 'host_mb_writes',
            'HostMBWritten': 'host_mb_written',
            'HostMBs': 'host_mbs',
            'HostMisses': 'host_misses',
            'HostReadHits': 'host_read_hits',
            'HostReadMisses': 'host_read_misses',
            'HostReads': 'host_reads',
            'HostWriteHits': 'host_write_hits',
            'HostWriteMisses': 'host_write_misses',
            'HostWrites': 'host_writes',
            'IODensity': 'io_density',
            'IOs': 'ios',
            'InfoAlertCount': 'info_alert_count',
            'MBRead': 'mb_read',
            'MBSentAndReceived': 'mb_sent_and_received',
            'MBWritten': 'mb_written',
            'MBs': 'mbs',
            'MaxWPThreshold': 'max_wp_threshold',
            'MissReqs': 'miss_reqs',
            'OptimizedMBReadMisses': 'optimized_mb_read_misses',
            'OptimizedMBReadMisss': 'optimized_mv_read_miss',
            'OptimizedReadMisses': 'optimized_read_misses',
            'OverallCompressionRatio': 'overall_compression_ratio',
            'OverallEfficiencyRatio': 'overall_efficiency_ratio',
            'PercentBusy': 'percent_busy',
            'PercentBusyLogicalCore_0': 'percent_busy_logical_core_0',
            'PercentBusyLogicalCore_1': 'percent_busy_logical_core_1',
            'PercentCacheWP': 'percent_cache_wp',
            'PercentCompressedTracks': 'percent_compressed_tracks',
            'PercentHit': 'percent_hit',
            'PercentHitReqs': 'percent_hit_reqs',
            'PercentMisses': 'percent_misses',
            'PercentNonIOBusy': 'percent_non_io_busy',
            'PercentNonIOBusyLogicalCore_0': 'percent_non_io_busy_logical_core_0',
            'PercentNonIOBusyLogicalCore_1': 'percent_non_io_busy_logical_core_1',
            'PercentRandomIO': 'percent_random_IO',
            'PercentRandomReadHit': 'percent_random_read_hit',
            'PercentRandomReadMiss': 'percent_random_read_miss',
            'PercentRandomReads': 'percent_random_reads',
            'PercentRandomWriteHit': 'percent_random_write_hit',
            'PercentRandomWriteMiss': 'percent_random_write_miss',
            'PercentRandomWrites': 'percent_random_writes',
            'PercentRead': 'percent_read',
            'PercentReadHit': 'percent_read_hit',
            'PercentReadMiss': 'percent_read_miss',
            'PercentReadReqHit': 'percent_read_req_hit',
            'PercentReadReqs': 'percent_read_reqs',
            'PercentReads': 'percent_reads',
            'PercentSeqIO': 'percent_seq_io',
            'PercentSeqRead': 'percent_seq_read',
            'PercentSeqReadHit': 'percent_seq_read_hit',
            'PercentSeqReadMiss': 'percent_seq_read_miss',
            'PercentSeqWriteHit': 'percent_seq_write_hit',
            'PercentSeqWriteMiss': 'percent_seq_write_miss',
            'PercentSeqWrites': 'percent_seq_writes',
            'PercentSnapshotSaved': 'percent_snapshot_saved',
            'PercentVPSaved': 'percent_vp_saved',
            'PercentVPSpaceSaved': 'percent_vp_space_saved',
            'PercentWrite': 'percent_write',
            'PercentWriteHit': 'percent_write_hit',
            'PercentWriteMiss': 'percent_write_miss',
            'PercentWriteReqHit': 'percent_write_req_hit',
            'PercentWriteReqs': 'percent_write_reqs',
            'PercentWrites': 'percent_writes',
            'PrefetchedTracks': 'prefetched_tracks',
            'QueueDepthUtilization': 'queue_depth_utilization',
            'RDFA_WPCount': 'rdfa_wp_count',
            'RDFRewrites': 'rdf_rewrites',
            'RDFS_WriteResponseTime': 'rdfs_write_response_time',
            'RDF_Balance': 'rdf_balance',
            'RandomIOs': 'random_ios',
            'RandomReadHits': 'random_read_hits',
            'RandomReadMissMBs': 'random_read_miss_mbs',
            'RandomReadMisses': 'random_read_misses',
            'RandomReads': 'random_reads',
            'RandomWriteHits': 'random_write_hits',
            'RandomWriteMissMBs': 'random_write_miss_mbs',
            'RandomWriteMisses': 'random_write_misses',
            'RandomWrites': 'random_writes',
            'RdfMBRead': 'rdf_mb_read',
            'RdfMBWritten': 'rdf_mb_written',
            'RdfReadHits': 'rdf_read_hits',
            'RdfReads': 'rdf_reads',
            'RdfResponseTime': 'rdf_response_time',
            'RdfWrites': 'rdf_writes',
            'ReadHitReqs': 'read_hit_reqs',
            'ReadMissReqs': 'read_miss_reqs',
            'ReadMissResponseTime': 'read_miss_response_time',
            'ReadReqs': 'read_reqs',
            'ReadResponseTime': 'read_response_time',
            'ReadResponseTimeCount1': 'read_response_time_1',
            'ReadResponseTimeCount2': 'read_response_time_2',
            'ReadResponseTimeCount3': 'read_response_time_3',
            'ReadResponseTimeCount4': 'read_response_time_4',
            'ReadResponseTimeCount5': 'read_response_time_5',
            'ReadResponseTimeCount6': 'read_response_time_6',
            'ReadResponseTimeCount7': 'read_response_time_7',
            'Reads': 'reads',
            'Reqs': 'reqs',
            'ResponseTime': 'response_time',
            'Rewrites': 'rewrites',
            'SATA_Balance': 'sata_balance',
            'SRDFA_MBSent': 'srdfa_mb_sent',
            'SRDFA_WriteReqs': 'srdfa_write_reqs',
            'SRDFS_MBSent': 'srdfs_mb_sent',
            'SRDFS_WriteReqs': 'srdfs_write_reqs',
            'SeqIOs': 'seq_ios',
            'SeqReadHits': 'seq_read_hits',
            'SeqReadMisses': 'seq_read_misses',
            'SeqReads': 'seq_reads',
            'SeqWriteHits': 'seq_write_hits',
            'SeqWriteMisses': 'seq_write_misses',
            'SeqWrites': 'seq_writes',
            'Skew': 'skew',
            'SlotCollisions': 'slot_collisions',
            'SnapshotCompressionRatio': 'snapshot_compression_ratio',
            'SnapshotEfficiencyRatio': 'snapshot_efficency_ratio',
            'SnapshotSharedRatio': 'snapshot_shared_ratio',
            'SyncMBSent': 'sync_mb_sent',
            'SyncWrites': 'sync_writes',
            'SyscallCount': 'sys_call_count',
            'SyscallRemoteDirCount': 'sys_call_remote_dir_count',
            'SyscallRemoteDirCounts': 'sys_call_remote_dir_counts',
            'SyscallTime': 'sys_call_time',
            'Syscall_RDF_DirCount': 'sys_call_rdf_dircount',
            'Syscall_RDF_DirCounts': 'sys_call_rdf_dircounts',
            'SystemMaxWPLimit': 'system_max_wp_limit',
            'SystemWPEvents': 'system_wp_events',
            'TotalReadCount': 'total_read_count',
            'TotalTracks': 'total_tracks',
            'TotalWriteCount': 'total_write_count',
            'TracksReceivedPerSec': 'tracks_received_per_sec',
            'TracksSentPerSec': 'tracks_sent_per_sec',
            'VPCompressionRatio': 'vp_compression_ratio',
            'VPEfficiencyRatio': 'vp_efficency_ratio',
            'VPSharedRatio': 'vp_shared_ratio',
            'WPCount': 'system_wp_count',
            'WarningAlertCount': 'warning_alert_count',
            'WriteHitReqs': 'write_hit_reqs',
            'WriteMissReqs': 'write_miss_reqs',
            'WriteMissResponseTime': 'write_miss_response_time',
            'WritePacedDelay': 'write_paces_delay',
            'WriteReqs': 'write_reqs',
            'WriteResponseTime': 'write_response_time',
            'WriteResponseTimeCount1': 'write_response_time_count_1',
            'WriteResponseTimeCount2': 'write_response_time_count_2',
            'WriteResponseTimeCount3': 'write_response_time_count_3',
            'WriteResponseTimeCount4': 'write_response_time_count_4',
            'WriteResponseTimeCount5': 'write_response_time_count_5',
            'WriteResponseTimeCount6': 'write_response_time_count_6',
            'WriteResponseTimeCount7': 'write_response_time_count_7',
            'Writes': 'writes',
            'directorId': 'director_id',
            'directorType': 'director_type',
            'fcid': 'fc_id',
            'fcid_lockdown': 'fc_id_lockdown',
            'fcid_value': 'fc_id_value',
            'hostId': 'host_id',
            'hostgroup': 'host_group',
            'initiatorId': 'initiator_id',
            'maskingview': 'masking_view',
            'num_of_slos': 'num_of_service_levels',
            'num_of_Workload_types': 'num_of_workload_types',
            'portGroupId': 'port_group_id',
            'rdfGroupCount': 'rdf_group_count',
            'replicationCacheUsage': 'replication_cache_usage',
            'sloCompliance': '',
            'sloId': 'slo_id',
            'storageGroupCount': 'storage_group_count',
            'storageGroupId': 'storage_group_id',
            'symmetrixId': 'symmetrix_id',
            'symmetrixPortKey': 'symmetrix_port_key',
            'virtualCapacity': 'virtual_capacity',
            'workload': 'workload',
            'workloadId': 'workload_id'
        }

        for old_key in payload.keys():
            if payload[old_key] == '':
                payload[old_key] = 'N/A'
            for new_key in rename_list.keys():
                if old_key == new_key:
                    value = rename_list[new_key]
                    payload[value] = payload.pop(old_key)

    ##########################################
    # Collect VMAX Storage Group level stats #
    ##########################################

    def _get_storage_group_performance(self, sg_id, payload):
        """

        :param sg_id:
        :param payload:
        :return:
        """
        sg_perf_uri = '/performance/StorageGroup/metrics'
        return self.rest_client.rest_request(
            sg_perf_uri, POST, request_object=payload)

    def get_storage_group_metrics(self, sg_id):
        """Get SG level information and performance metrics for a given SG ID.

        :param sg_id: Storage Group ID
        :return: Combined payload of all SG level information & performance metrics
        """

        # Set SG performance metrics payload
        sg_perf_payload = {
            'symmetrixId': self.array_id,
            'endDate': self.timestamp,
            'dataFormat': 'Average',
            'storageGroupId': sg_id,
            'metrics': [
                'CriticalAlertCount', 'InfoAlertCount', 'WarningAlertCount', 'AllocatedCapacity', 'TotalTracks',
                'BEDiskReadResponseTime', 'BEReadRequestTime', 'BEReadTaskTime', 'AvgIOSize',
                'AvgReadResponseTime6',
                'AvgReadResponseTime7', 'AvgReadSize', 'AvgWritePacedDelay', 'AvgWriteResponseTime6',
                'AvgWriteResponseTime7', 'AvgWriteSize', 'BEMBReads', 'BEMBTransferred', 'BEMBWritten',
                'BEPercentReads', 'BEPercentWrites', 'BEPrefetchedTrackss', 'BEPrefetchedTrackUsed', 'BEReadReqs',
                'BEWriteReqs', 'CompressedTracks', 'CompressionRatio', 'BlockSize', 'HostMBs', 'IODensity',
                'HostIOs',
                'MaxWPThreshold', 'HostMBReads', 'HostMBWritten', 'AvgOptimizedReadMissSize',
                'OptimizedMBReadMisss',
                'OptimizedReadMisses', 'PercentCompressedTracks', 'PercentHit', 'PercentMisses', 'PercentRandomIO',
                'PercentRandomReads', 'PercentRandomReadHit', 'PercentRandomReadMiss', 'PercentRandomWrites',
                'PercentRandomWriteHit', 'PercentRandomWriteMiss', 'PercentRead', 'PercentReadHit',
                'PercentReadMiss',
                'PercentSeqIO', 'PercentSeqRead', 'PercentSeqReadHit', 'PercentSeqReadMiss', 'PercentSeqWrites',
                'PercentSeqWriteHit', 'PercentSeqWriteMiss', 'PercentVPSpaceSaved', 'PercentWrite',
                'PercentWriteHit',
                'PercentWriteMiss', 'BEPrefetchedMBs', 'HostIOLimitPercentTimeExceeded', 'RandomIOs',
                'RandomReadHits',
                'RandomReadMisses', 'RandomReads', 'RandomWriteHits', 'RandomWriteMisses', 'RandomWrites',
                'RdfMBRead',
                'RdfMBWritten', 'RdfReads', 'RdfReadHits', 'RdfResponseTime', 'RDFRewrites', 'RdfWrites',
                'HostReads',
                'HostReadHits', 'HostReadMisses', 'ReadResponseTimeCount1', 'ReadResponseTimeCount2',
                'ReadResponseTimeCount3', 'ReadResponseTimeCount4', 'ReadResponseTimeCount5',
                'ReadResponseTimeCount6',
                'ReadResponseTimeCount7', 'ResponseTime', 'RDFS_WriteResponseTime', 'ReadMissResponseTime',
                'ReadResponseTime', 'WriteMissResponseTime', 'WriteResponseTime', 'SeqReadHits', 'SeqReadMisses',
                'SeqReads', 'SeqWriteHits', 'SeqWriteMisses', 'SeqWrites', 'Skew', 'SRDFA_MBSent',
                'SRDFA_WriteReqs',
                'SRDFS_MBSent', 'SRDFS_WriteReqs', 'BEReqs', 'HostHits', 'HostMisses', 'SeqIOs', 'WPCount',
                'HostWrites', 'HostWriteHits', 'HostWriteMisses', 'WritePacedDelay', 'WriteResponseTimeCount1',
                'WriteResponseTimeCount2', 'WriteResponseTimeCount3', 'WriteResponseTimeCount4',
                'WriteResponseTimeCount5', 'WriteResponseTimeCount6',
                'WriteResponseTimeCount7'
            ],
            'startDate': self.timestamp
        }

        # Perform all SG level REST calls (get/post)
        sg_info = self.get_sg(sg_id)
        sg_perf_response, sc = self._get_storage_group_performance(sg_perf_payload)

        # Set combined payload values not present in returned REST metrics
        combined_payload = dict()
        combined_payload['reporting_level'] = "Storage Group"
        combined_payload['timestamp'] = self.timestamp
        combined_payload['symmetrixId'] = self.array_id

        # If no SG level information is retrieved...
        if not sg_info:
            combined_payload['info_data'] = False
            combined_payload['info_msg'] = "No Storage Group info data available"

        else:
            # SG level information retrieved...
            for k, v in sg_info['storageGroup'][0].items():
                combined_payload[k] = v

        # If no SG level performance information is retrieved...
        if not sg_perf_response:
            combined_payload['perf_data'] = False
            combined_payload['perf_msg'] = "No active Storage Group performance data available"

        else:
            # Performance metrics returned...
            for k, v in sg_perf_payload['resultList']['result'][0].items():
                combined_payload[k] = v

        # Rename all keys to common standardised format, dump to JSON

        self.rename_metrics(combined_payload)

        return combined_payload

    #####################################
    # Collect VMAX Director level stats #
    #####################################

    def get_director_info(self, director_id):
        """
        Get Director level information and performance metrics for a given Director ID
        :param director_id: Director ID
        :return: Combined payload of all Director level information & performance metrics
        """
        # Create Director level target URIs
        director_info, sc = self.get_director(director_id)
        be_director_uri = '/performance/BEDirector/metrics'
        fe_director_uri = '/performance/FEDirector/metrics'
        rdf_director_uri = '/performance/RDFDirector/metrics'
        im_director_uri = '/performance/IMDirector/metrics'
        eds_director_uri = '/performance/EDSDirector/metrics'

        # Set BE Director performance metrics payload
        be_director_payload = {
            'symmetrixId': self.array_id,
            'directorId': director_id,
            'endDate': self.timestamp,
            'dataFormat': 'Average',
            'metrics': [
                'AvgTimePerSyscall', 'CompressedMBs', 'CompressedReadMBs', 'CompressedWriteMBs',
                'CompressedReadReqs',
                'CompressedReqs', 'CompressedWriteReqs', 'IOs', 'MBs', 'MBRead', 'MBWritten', 'PercentBusy',
                'PercentBusyLogicalCore_0', 'PercentBusyLogicalCore_1', 'PercentNonIOBusy',
                'PercentNonIOBusyLogicalCore_0', 'PercentNonIOBusyLogicalCore_1', 'PrefetchedTracks', 'ReadReqs',
                'Reqs', 'SyscallCount', 'Syscall_RDF_DirCount', 'SyscallRemoteDirCount', 'WriteReqs'
            ],
            'startDate': self.timestamp
        }

        # Set FE Director performance metrics payload
        fe_director_payload = {
            'symmetrixId': self.array_id,
            'directorId': director_id,
            'endDate': self.timestamp,
            'dataFormat': 'Average',
            'metrics': [
                'AvgRDFSWriteResponseTime', 'AvgReadMissResponseTime', 'AvgWPDiscTime', 'AvgTimePerSyscall',
                'DeviceWPEvents', 'HostMBs', 'HitReqs', 'HostIOs', 'MissReqs', 'AvgOptimizedReadMissSize',
                'OptimizedMBReadMisses', 'OptimizedReadMisses', 'PercentBusy', 'PercentHitReqs', 'PercentReadReqs',
                'PercentReadReqHit', 'PercentWriteReqs', 'PercentWriteReqHit', 'QueueDepthUtilization',
                'HostIOLimitIOs', 'HostIOLimitMBs', 'ReadReqs', 'ReadHitReqs', 'ReadMissReqs', 'Reqs',
                'ReadResponseTime', 'WriteResponseTime', 'SlotCollisions', 'SyscallCount', 'Syscall_RDF_DirCounts',
                'SyscallRemoteDirCounts', 'SystemWPEvents', 'TotalReadCount', 'TotalWriteCount', 'WriteReqs',
                'WriteHitReqs', 'WriteMissReqs'
            ],
            'startDate': self.timestamp
        }

        # Set RDF Director performance metrics payload
        rdf_director_payload = {
            'symmetrixId': self.array_id,
            'directorId': director_id,
            'endDate': self.timestamp,
            'dataFormat': 'Average',
            'metrics': [
                'AvgIOServiceTime', 'AvgIOSizeReceived', 'AvgIOSizeSent', 'AvgTimePerSyscall', 'CopyIOs', 'CopyMBs',
                'IOs', 'MBSentAndReceived', 'MBRead', 'MBWritten', 'PercentBusy', 'Reqs', 'Rewrites', 'AsyncMBSent',
                'AsyncWriteReqs', 'SyncMBSent', 'SyncWrites', 'SyscallCount', 'Syscall_RDF_DirCounts',
                'SyscallRemoteDirCount', 'SyscallTime', 'TracksReceivedPerSec', 'TracksSentPerSec', 'WriteReqs'
            ],
            'startDate': self.timestamp
        }

        # Set IM Director performance metrics payload
        im_director_payload = {
            'symmetrixId': self.array_id,
            'directorId': director_id,
            'endDate': self.timestamp,
            'dataFormat': 'Average',
            'metrics': [
                'PercentBusy'
            ],
            'startDate': self.timestamp
        }

        # Set EDS Director performance metrics payload
        eds_director_payload = {
            'symmetrixId': self.array_id,
            'directorId': director_id,
            'endDate': self.timestamp,
            'dataFormat': 'Average',
            'metrics': [
                'PercentBusy', 'RandomReadMissMBs', 'RandomReadMisses', 'RandomWriteMissMBs', 'RandomWriteMisses'
            ],
            'startDate': self.timestamp
        }

        # Perform Director level performance REST call dependent on Director type
        if 'DF' in director_id or 'DX' in director_id:
            perf_metrics_payload = self.rest_client.rest_request(
                be_director_uri, POST, request_object=be_director_payload)
            director_type = 'BE'
        elif 'EF' in director_id or 'FA' in director_id or 'FE' in director_id or 'SE' in director_id:
            perf_metrics_payload = self.rest_client.rest_request(
                fe_director_uri, POST, request_object=fe_director_payload)
            director_type = 'FE'
        elif 'RF' in director_id or 'RE' in director_id:
            perf_metrics_payload = self.rest_client.rest_request(
                rdf_director_uri, POST, request_object=rdf_director_payload)
            director_type = 'RDF'
        elif 'IM' in director_id:
            perf_metrics_payload = self.rest_client.rest_request(
                im_director_uri, POST,  request_object=im_director_payload)
            director_type = 'IM'
        elif 'ED' in director_id:
            perf_metrics_payload = self.rest_client.rest_request(
                eds_director_uri, POST, request_object=eds_director_payload)
            director_type = 'EDS'
        else:
            # Unable to determine Director type, set to N/A
            perf_metrics_payload = False
            director_type = 'N/A'

        # Set combined payload values not present in returned REST metrics
        combined_payload = dict()
        combined_payload['reporting_level'] = "Director"
        combined_payload['timestamp'] = self.timestamp
        combined_payload['symmetrixId'] = self.array_id
        combined_payload['directorType'] = director_type

        # If no Director level information is retrieved...
        if not director_info:
            combined_payload['info_data'] = False
            combined_payload['info_msg'] = 'No Director info data available'

        else:
            # Director level information retrieved...
            for k, v in director_info['director'][0].items():
                combined_payload[k] = v

        # If no Director level performance information is retrieved...
        if not perf_metrics_payload:
            combined_payload['perf_data'] = False
            combined_payload['perf_msg'] = "No active Director performance data available"

        else:
            # Performance metrics returned...
            for k, v in perf_metrics_payload['resultList']['result'][0].items():
                combined_payload[k] = v

        # Rename all keys to common standardised format, dump to JSON

        self.rename_metrics(combined_payload)

        return combined_payload
