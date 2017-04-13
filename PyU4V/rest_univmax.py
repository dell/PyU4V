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
import csv
import json
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
        self.end_date = int(round(time.time() * 1000))
        self.start_date = (self.end_date - 3600000)
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
    # Utility functions
    ###############################

    def create_list_from_file(self,file_name):
        """Given a file, create a list from its contents.  

        :param file_name: the path to the file
        :return: list of contents
        """
        with open(file_name) as f:
            list_item = f.readlines()
        raw_list = map(lambda s: s.strip(), list_item)
        return list(raw_list)

    def read_csv_values(self, file_name):
        '''
        reads any csv file with headers
        You can extract the multiple lists from the headers in the CSV file in your own script call this function and 
        assign to data variable, then extract the lists to the variables example below
        data=ru.read_csv_values(mycsv.csv)
        sgnamelist = data['sgname']
        policylist = data['policy']

        :param file_name CSV file
        :return: Dictionary of data parsed from CSV
        '''
        # open the file in universal line ending mode
        with open(file_name, 'rU') as infile:
            # read the file as a dictionary for each row ({header : value})
            reader = csv.DictReader(infile)
            data = {}
            for row in reader:
                for header, value in row.items():
                    try:
                        data[header].append(value)
                    except KeyError:
                        data[header] = [value]
        return data

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
    # SLOProvisioning functions
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

    def create_host(self, host_name, initiator_list=None, host_flags=None, file=None):
        """Create a host with the given initiators. Accepts either initiator_list or file.
        The initiators must not be associated with another host.
        :param host_name: the name of the new host
        :param initiator_list: list of initiators e.g.[10000000ba873cbf,10000000ba873cba]
        :param host_flags: dictionary of optional host flags to apply
        :param file: full path and file name.
        :return: dict, status_code
        """
        if file:
            initiator_list=self.create_list_from_file(file)

        if not file and not initiator_list:
            print ("No file or initiator_list supplied, you must specify one or the other")
            exit ()
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
        :param initiator_id: initiator id, optional
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
            host_id = response['maskingView'][0]['hostId']
            return host_id
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
        """Parse a list of snaps for storage group and select from menu.

        :return:String returned with the name of the selected snapshot
        """
        snaplist = self.get_snap_sg(sgname)
        print(snaplist)
        i = 0
        for elem in snaplist[0]["name"]:
            print(i, " ", elem, "\n")
            i = int(i + 1)
        snapselection = input("Choose the snapshot you want from the "
                              "below list \n")
        snapshot_id = (snaplist[0]["name"][int(snapselection)])
        return snapshot_id

    def link_gen_snapsthot_83(self, sg_id, snap_name, generation, link_sg_name):
        """Creates a new snapshot of a specified sg

        83 version will automatically create linked SG if one of the specified
        name doesn't exist
        :param sg_id: Source storage group name
        :param snap_name: name of the snapshot
        :param generation: generation number of a snapshot (int)
        :param link_sg_name:  the target storage group name
        :return: dict, status_code
        """
        target_uri = ("/83/replication/symmetrix/%s/storagegroup/%s/"
                      "snapshot/%s/generation/%s"
                      % (self.array_id, sg_id, snap_name, generation))
        snap_data = ({"link": {"linkStorageGroupName": link_sg_name},
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
        snap_capability = False
        response, sc = self.get_replication_capabilities(array)
        try:
            symmList = response['symmetrixCapability']
            for symm in symmList:
                if symm['symmetrixId'] == array:
                    snap_capability = symm['snapVxCapable']
                    break
        except KeyError:
            LOG.error("Cannot access replication capabilities")
        return snap_capability

    # admissibility checks

    def get_wlp_timestamp(self):
        """Get the latest timestamp from WLP for processing New Worlkloads.

        :return: dict, status_code
        """
        target_uri = ("/82/wlp/symmetrix/%s" % self.array_id)
        return self.rest_client.rest_request(target_uri, GET)

    def get_headroom(self, workload, srp="SRP_1", slo="Diamond"):
        """Get the Remaining Headroom Capacity.

        Get the headroom capacity for a given srp/ slo/ workload combination.
        :param workload: the workload type (DSS, OLTP, DSS_REP, OLTP_REP)
        :param srp: the storage resource pool. Default SRP_1.
        :param slo: the service level. Default Diamond.
        :return: dict, status_code (sample response
            {'headroom': [{'workloadType': 'OLTP',
            'headroomCapacity': 29076.34, 'processingDetails':
                {'lastProcessedSpaTimestamp': 1485302100000,
                'nextUpdate': 1670}, 'sloName': 'Diamond',
                'srp': 'SRP_1', 'emulation': 'FBA'}]})
        """
        target_uri = ("/82/wlp/symmetrix/%(array)s/headroom?emulation=FBA&slo="
                      "%(slo)s&workloadtype=%(workload)s&srp=%(srp)s"
                      % {'array': self.array_id, 'workload': workload,
                         'slo': slo, 'srp': srp})
        return self.rest_client.rest_request(target_uri, GET)

    def srdf_protect_sg(self, sg_id, remote_sid, srdfmode, establish=None):
        """

        :param sg_id: Unique string up to 32 Characters
        :param remote_sid: Type Integer 12 digit VMAX ID e.g. 000197000008
        :param srdfmode: String, values can be Active, AdaptiveCopyDisk,
                         Synchronous,Asynchronous
        :param establish: default is none. Bool
        :return: message and status Type JSON
        """
        target_uri = ("/83/replication/symmetrix/%s/storagegroup/%s/rdf_group"
                      % (self.array_id, sg_id))
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
        """Modify the state of an srdf.

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
            # Sets the RDFG for the Put call to first value in list if
            # group is not cascasded.
            rdfg_num = rdfg_list[0]
        else:
            LOG.exception("Group is cascaded, functionality not yet added in "
                          "this python library")
        if rdfg_num:
            target_uri = ("/83/replication/symmetrix/%s/storagegroup/%s/rdf_group/%s"
                          % (self.array_id, sg_id, rdfg_num))
            action_payload = ({"action": action})
            return self.rest_client.rest_request(target_uri, PUT, request_object=action_payload)

    # Performance Metrics

    def get_fe_director_list(self):
        """Get list of all FE Directors.

        :return: director list
        """
        target_uri = "/performance/FEDirector/keys"
        dir_payload = ({"symmetrixId": self.array_id})

        dir_response = self.rest_client.rest_request(target_uri, POST, request_object=dir_payload)
        dir_list = []
        for director in dir_response[0]['feDirectorInfo']:
            dir_list.append(director['directorId'])
        return dir_list

    def get_fe_port_list(self):
        """Function to get a list of all front end ports in the array.

        :return: List of Directors and Ports
        """
        target_uri = "/performance/FEPort/keys"
        port_list = []
        dir_list = self.get_fe_director_list()
        for director in dir_list:
            port_payload = ({
                "symmetrixId": self.array_id,
                "directorId": director
            })
            port_details = {}
            port_response = self.rest_client.rest_request(target_uri, POST, request_object=port_payload)
            for port in port_response[0]['fePortInfo']:
                port_details[port['portId']] = director
            port_list.append(port_details)
        return port_list

    def get_fe_port_util_last4hrs(self, dir_id, port_id):
        """Get stats for last 4 hours.

        Currently only coded for one metric - can be adapted for multiple
        :return:Requested stats
        """
        end_date = int(round(time.time() * 1000))
        start_date = (end_date - 14400000)
        port_list = self.get_fe_port_list()

        target_uri = '/performance/FEPort/metrics'
        port_perf_payload = ({"startDate": start_date,
                              "endDate": end_date,
                              "symmetrixId": self.array_id,
                              "directorId": dir_id,
                              "portId": port_id,
                              "dataFormat": "Average",
                              "metrics": ["PercentBusy"]})
        return self.rest_client.rest_request(target_uri, POST, request_object=port_perf_payload)

    def get_fe_director_metrics(self, start_date, end_date, director, dataformat):
        """Function to get one or more metrics for front end directors.

        :param start_date: Date EPOCH Time in Milliseconds
        :param end_date: Date EPOCH Time in Milliseconds
        :param director:List of FE Directors
        :param dataformat:Average or Maximum
        :param dataformat:
        :return: JSON Payload, and RETURN CODE 200 for success
        """
        target_uri = "/performance/FEDirector/metrics"
        feDirectorParam = ({
                        "symmetrixId": self.array_id,
                        "directorId": director,
                        "endDate": end_date,
                        "dataFormat": dataformat,
                        "metrics": ['AvgRDFSWriteResponseTime', 'AvgReadMissResponseTime',
                                    'AvgWPDiscTime', 'AvgTimePerSyscall', 'DeviceWPEvents',
                                    'HostMBs', 'HitReqs', 'HostIOs', 'MissReqs',
                                    'AvgOptimizedReadMissSize', 'OptimizedMBReadMisses',
                                    'OptimizedReadMisses', 'PercentBusy', 'PercentHitReqs',
                                    'PercentReadReqs', 'PercentReadReqHit', 'PercentWriteReqs',
                                    'PercentWriteReqHit', 'QueueDepthUtilization',
                                    'HostIOLimitIOs', 'HostIOLimitMBs', 'ReadReqs',
                                    'ReadHitReqs', 'ReadMissReqs', 'Reqs', 'ReadResponseTime',
                                    'WriteResponseTime', 'SlotCollisions', 'SyscallCount',
                                    'Syscall_RDF_DirCounts', 'SyscallRemoteDirCounts',
                                    'SystemWPEvents', 'TotalReadCount', 'TotalWriteCount',
                                    'WriteReqs', 'WriteHitReqs', 'WriteMissReqs'],
                        "startDate": start_date})

        return self.rest_client.rest_request(target_uri, POST,
                                             request_object=feDirectorParam)


    def get_fe_port_metrics(self, start_date, end_date, director_id,
                            port_id, dataformat, metriclist):
        """Function to get one or more Metrics for Front end Director ports

        :param start_date: Date EPOCH Time in Milliseconds
        :param end_date: Date EPOCH Time in Milliseconds
        :param director_id: Director id
        :param port_id: port id
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
    def get_array_metrics(self,start_date, end_date):
        """
        Get all avaliable performance statiscics for specified time period retrun in JSON
        :param start_date: EPOCH Time
        :param end_date: Epoch Time
        :return:
        """
        target_uri = "/performance/Array/metrics"
        array_perf_payload = {
            'symmetrixId': self.array_id,
            'endDate': end_date,
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
            'startDate': start_date
        }
        array_perf_data = self.rest_client.rest_request(target_uri, POST, request_object=array_perf_payload)
        array_results_combined = dict()
        array_results_combined['symmetrixID'] = self.array_id
        array_results_combined['reporting_level'] ="array"
        array_results_combined['perf_data']= array_perf_data[0]['resultList']['result']
        return array_results_combined


    ##########################################
    # Collect VMAX Storage Group level stats #
    ##########################################

    def _get_storage_group_metrics(self, sg_id,start_date,end_date):
        """Get storage group performance metrics.

        :param payload:
        """
        target_uri = '/performance/StorageGroup/metrics'
        sg_perf_payload = {
            'symmetrixId': self.array_id,
            'endDate': end_date,
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
            'startDate': start_date
        }
        sg_perf_data = self.rest_client.rest_request(target_uri, POST, request_object=sg_perf_payload)
        sg_results_combined = dict()
        sg_results_combined['symmetrixID'] = self.array_id
        sg_results_combined['reporting_level'] = "StorageGroup"
        sg_results_combined['sgname'] = sg_id
        sg_results_combined['perf_data'] = sg_perf_data[0]['resultList']['result']
        return sg_results_combined


    #####################################
    # Collect VMAX Director level stats #
    #####################################

    def get_all_fe_director_metrics(self, start_date, end_date):
        # First Get a list of all Directors
        # Calculate start and End Dates for Gathering Performance Stats Last 1 Hour
        dir_list = self.get_fe_director_list()
        director_results_combined = dict()
        director_results_list = []
        # print("this is the director list %s" % dir_list)
        for fe_director in dir_list:
            director_metrics = self.get_fe_director_metrics(
                director=fe_director, start_date=start_date,
                end_date=end_date, dataformat='Average')
            director_results = ({
                "directorID": fe_director,
                "perfdata": director_metrics[0]['resultList']['result']})
            director_results_list.append(director_results)
        director_results_combined['symmetrixID'] = self.array_id
        director_results_combined['reporting_level'] = "FEDirector"
        director_results_combined['perf_data'] = director_results_list
        return director_results_combined


    def get_director_info(self, director_id, start_date, end_date):
        """Get Director level information and performance metrics for specified time frame,  hard coded to average numnbers.

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
            'endDate': end_date,
            'dataFormat': 'Average',
            'metrics': [
                'AvgTimePerSyscall', 'CompressedMBs', 'CompressedReadMBs', 'CompressedWriteMBs',
                'CompressedReadReqs',
                'CompressedReqs', 'CompressedWriteReqs', 'IOs', 'MBs', 'MBRead', 'MBWritten', 'PercentBusy',
                'PercentBusyLogicalCore_0', 'PercentBusyLogicalCore_1', 'PercentNonIOBusy',
                'PercentNonIOBusyLogicalCore_0', 'PercentNonIOBusyLogicalCore_1', 'PrefetchedTracks', 'ReadReqs',
                'Reqs', 'SyscallCount', 'Syscall_RDF_DirCount', 'SyscallRemoteDirCount', 'WriteReqs'
            ],
            'startDate': self.start_date
        }

        # Set FE Director performance metrics payload
        fe_director_payload = {
            'symmetrixId': self.array_id,
            'directorId': director_id,
            'endDate': end_date,
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
            'startDate': start_date
        }

        # Set RDF Director performance metrics payload
        rdf_director_payload = {
            'symmetrixId': self.array_id,
            'directorId': director_id,
            'endDate': end_date,
            'dataFormat': 'Average',
            'metrics': [
                'AvgIOServiceTime', 'AvgIOSizeReceived', 'AvgIOSizeSent', 'AvgTimePerSyscall', 'CopyIOs', 'CopyMBs',
                'IOs', 'MBSentAndReceived', 'MBRead', 'MBWritten', 'PercentBusy', 'Reqs', 'Rewrites', 'AsyncMBSent',
                'AsyncWriteReqs', 'SyncMBSent', 'SyncWrites', 'SyscallCount', 'Syscall_RDF_DirCounts',
                'SyscallRemoteDirCount', 'SyscallTime', 'TracksReceivedPerSec', 'TracksSentPerSec', 'WriteReqs'
            ],
            'startDate': start_date
        }

        # Set IM Director performance metrics payload
        im_director_payload = {
            'symmetrixId': self.array_id,
            'directorId': director_id,
            'endDate': self.end_date,
            'dataFormat': 'Average',
            'metrics': ['PercentBusy'],
            'startDate': self.start_date
        }

        # Set EDS Director performance metrics payload
        eds_director_payload = {
            'symmetrixId': self.array_id,
            'directorId': director_id,
            'endDate': self.end_date,
            'dataFormat': 'Average',
            'metrics': [
                'PercentBusy', 'RandomReadMissMBs', 'RandomReadMisses', 'RandomWriteMissMBs', 'RandomWriteMisses'
            ],
            'startDate': self.start_date
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
        combined_payload['symmetrixId'] = self.array_id
        combined_payload['director_id'] =director_id
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
            combined_payload['perf_data']=perf_metrics_payload[0]['resultList']['result']

        # Rename all keys to common standardised format, dump to JSON

        return combined_payload

    ########################
    #Get host level Metrics#
    ########################

    def get_host_metrics(self, host, start_date, end_date):
        """
                Get all avaliable host performance statiscics for specified time period retrun in JSON
                :param start_date: EPOCH Time
                :param end_date: Epoch Time
                :return: Formatted results
                """
        target_uri = "/81/performance/Host/metrics"
        host_perf_payload = {
            'symmetrixId': self.array_id,
            'endDate': end_date,
            'hostId':host,
            'dataFormat': 'Average',
            'metrics': ['HostIOs','HostMBReads','HostMBWrites','Reads','ResponseTime','ReadResponseTime','WriteResponseTime',
                        'SyscallCount','Writes','MBs'
            ],
            'startDate': start_date
        }
        host_perf_data = self.rest_client.rest_request(target_uri, POST, request_object=host_perf_payload)
        host_results = dict()
        host_results['symmetrixID'] = self.array_id
        host_results['reporting_level'] = "Host"
        host_results['HostID']=host
        host_results['perf_data'] = host_perf_data[0]['resultList']['result']
        return host_results

    # Alert Threshold Configuration
    def get_perf_threshold_categories(self):
        '''
        Written for Unisphere 84, if you are on ealier, append /83 to the endpoint 
        :return: 
        '''
        target_uri = "/performance/threshold/categories"
        categories = self.rest_client.rest_request(target_uri, GET)
        category_list=categories[0]["endpoint"]
        return category_list


    def get_perf_category_threshold_settings(self,category):
        '''
        will accept valid category, categories listed from get_threshold_categories 
        written for Unisphere 84, if earlier version append /83/ to start of uri
        :param category: 
        :return: 
        '''
        target_uri = "/performance/threshold/list/%s" % (category)
        return self.rest_client.rest_request(target_uri, GET)


    def get_kpi_metrics_config(self):
        '''
        Checks all Performance Alerting Thresholds and returns settings for KPI
        Metrics.
        :return: list of KPI metrics organised by category with each setting.
        '''''
        categories = self.get_perf_threshold_categories()
        perf_threshold_combined=dict()
        perf_threshold_list=[]
        #print (categories)
        for category in categories:
            current_perf_threshold = self.get_perf_category_threshold_settings(category)
        #    print (category, current_perf_threshold)
            data = current_perf_threshold[0]["performanceThreshold"]
            metriclist = []
            for item in data:
                if item['kpi']:
                    metriclist.append([item])
            perf_threshold = ({
                "category": category,
                "metric_settings": metriclist})
            perf_threshold_list.append(perf_threshold)
        perf_threshold_combined['perf_threshold']= perf_threshold_list
        print(perf_threshold_combined)
        # TODO export this to CSV that can be easily modified. Also create set function to read CSV
        '''    Work in Progress'''
        outputfile = open('unisettings.csv', 'w')
        csvwriter = csv.writer(outputfile)
        count = 0
        for stuff in perf_threshold_combined['perf_threshold']['category'][0]:
            print (stuff)
            if count == 0:
                header = stuff.keys()
                csvwriter.writerow(header)
                count += 1
            csvwriter.writerow(stuff.values())
        outputfile.close()

        return perf_threshold_combined



