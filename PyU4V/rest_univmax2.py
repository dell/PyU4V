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
import csv
import logging
import time

import six

from PyU4V.rest_requests import RestRequests
from PyU4V.utils import config_handler
from PyU4V.utils import exception

logger = logging.getLogger(__name__)
LOG, CFG = config_handler.set_logger_and_config(logger)

# HTTP constants
GET = 'GET'
POST = 'POST'
PUT = 'PUT'
DELETE = 'DELETE'

# U4V constants
REPLICATION = 'replication'
SLOPROVISIONING = 'sloprovisioning'
WLP = 'wlp'
MIGRATION = 'migration'
DSA = 'dsa'
SYSTEM = 'system'
VVOL = 'vvol'
PROVISIONING = 'provisioning'
STATUS_200 = 200
STATUS_201 = 201
STATUS_202 = 202
STATUS_204 = 204
# Job constants
INCOMPLETE_LIST = ['created', 'scheduled', 'running',
                   'validating', 'validated']
CREATED = 'created'
SUCCEEDED = 'succeeded'
CREATE_VOL_STRING = "Creating new Volumes"
ASYNCHRONOUS = "ASYNCHRONOUS"


class RestFunctions:
    def __init__(self, username=None, password=None, server_ip=None,
                 port=None, verify=None, u4v_version='84',
                 interval=5, retries=200, array_id=None):
        self.end_date = int(round(time.time() * 1000))
        self.start_date = (self.end_date - 3600000)
        self.array_id = array_id
        if not self.array_id:
            try:
                self.array_id = CFG.get('setup', 'array')
            except Exception:
                LOG.warning("No array id specified. Please set "
                            "array ID using the 'set_array_id(array_id)' "
                            "function.")
        if CFG is not None:
            if not username:
                username = CFG.get('setup', 'username')
            if not password:
                password = CFG.get('setup', 'password')
            if not server_ip:
                server_ip = CFG.get('setup', 'server_ip')
            if not port:
                port = CFG.get('setup', 'port')
        if verify is None:
            try:
                verify = CFG.get('setup', 'verify')
                if verify.lower() == 'false':
                    verify = False
                elif verify.lower() == 'true':
                    verify = True
            except Exception:
                verify = True
        base_url = 'https://%s:%s/univmax/restapi' % (server_ip, port)
        self.rest_client = RestRequests(username, password, verify,
                                        base_url)
        self.request = self.rest_client.rest_request
        self.interval = interval
        self.retries = retries
        self.U4V_VERSION = u4v_version

    def close_session(self):
        """Close the current rest session
        """
        self.rest_client.close_session()

    def set_requests_timeout(self, timeout_value):
        """Set the requests timeout.

        :param timeout_value: the new timeout value - int
        """
        self.rest_client.timeout = timeout_value

    def set_array_id(self, array_id):
        """Set the array serial number.

        :param array_id: the array serial number
        """
        self.array_id = array_id

    def wait_for_job_complete(self, job):
        """Given the job wait for it to complete.

        :param job: the job dict
        :returns: rc -- int, result -- string, status -- string,
                  task -- list of dicts detailing tasks in the job
        :raises: VolumeBackendAPIException
        """
        res, tasks = None, None
        if job['status'].lower() == SUCCEEDED:
            try:
                res, tasks = job['result'], job['task']
            except KeyError:
                pass
            return 0, res, job['status'], tasks

        def _wait_for_job_complete():
            # Called at an interval until the job is finished.
            retries = kwargs['retries']
            try:
                kwargs['retries'] = retries + 1
                if not kwargs['wait_for_job_called']:
                    is_complete, result, rc, status, task = (
                        self._is_job_finished(job_id))
                    if is_complete is True:
                        kwargs['wait_for_job_called'] = True
                        kwargs['rc'], kwargs['status'] = rc, status
                        kwargs['result'], kwargs['task'] = result, task
            except Exception:
                exception_message = "Issue encountered waiting for job."
                LOG.exception(exception_message)
                raise exception.VolumeBackendAPIException(
                    data=exception_message)

            return kwargs

        job_id = job['jobId']
        kwargs = {'retries': 0, 'wait_for_job_called': False,
                  'rc': 0, 'result': None}

        while not kwargs['wait_for_job_called']:
            time.sleep(self.interval)
            kwargs = _wait_for_job_complete()
            if kwargs['retries'] > self.retries:
                LOG.error("_wait_for_job_complete failed after "
                          "%(retries)d tries.", {'retries': kwargs['retries']})
                kwargs['rc'], kwargs['result'] = -1, kwargs['result']
                break

        LOG.debug("Return code is: %(rc)lu. Result is %(res)s.",
                  {'rc': kwargs['rc'], 'res': kwargs['result']})
        return (kwargs['rc'], kwargs['result'],
                kwargs['status'], kwargs['task'])

    def _is_job_finished(self, job_id):
        """Check if the job is finished.

        :param job_id: the id of the job
        :returns: complete -- bool, result -- string,
                  rc -- int, status -- string, task -- list of dicts
        """
        complete, rc, status, result, task = False, 0, None, None, None
        job_url = "/%s/system/job/%s" % (self.U4V_VERSION, job_id)
        job, status_code = self._get_request(job_url, 'job')
        if job:
            status = job['status']
            try:
                result, task = job['result'], job['task']
            except KeyError:
                pass
            if status.lower() == SUCCEEDED:
                complete = True
            elif status.lower() in INCOMPLETE_LIST:
                complete = False
            else:
                rc, complete = -1, True
        return complete, result, rc, status, task

    @staticmethod
    def check_status_code_success(operation, status_code, message):
        """Check if a status code indicates success.

        :param operation: the operation
        :param status_code: the status code
        :param message: the server response
        :raises: VolumeBackendAPIException
        """
        if status_code not in [STATUS_200, STATUS_201,
                               STATUS_202, STATUS_204]:
            exception_message = (
                'Error %(operation)s. The status code received '
                'is %(sc)s and the message is %(message)s.'
                % {'operation': operation,
                   'sc': status_code, 'message': message})
            raise exception.VolumeBackendAPIException(
                data=exception_message)

    def wait_for_job(self, operation, status_code, job):
        """Check if call is async, wait for it to complete.

        :param operation: the operation being performed
        :param status_code: the status code
        :param job: the job
        :returns: task -- list of dicts detailing tasks in the job
        :raises: VolumeBackendAPIException
        """
        task = None
        if status_code == STATUS_202:
            rc, result, status, task = self.wait_for_job_complete(job)
            if rc != 0:
                exception_message = (
                    "Error %(operation)s. Status code: %(sc)lu. "
                    "Error: %(error)s. Status: %(status)s."
                    % {'operation': operation, 'sc': rc,
                       'error': six.text_type(result),
                       'status': status})
                LOG.error(exception_message)
                raise exception.VolumeBackendAPIException(
                    data=exception_message)
        return task

    def _build_uri(self, array, category, resource_type,
                   resource_name=None, version=None):
        """Build the target url.
.
        :param array: the array serial number
        :param category: the resource category e.g. sloprovisioning
        :param resource_type: the resource type e.g. maskingview
        :param resource_name: the name of a specific resource
        :param version: the U4V version
        :returns: target url, string
        """
        if version is None:
            version = self.U4V_VERSION
        target_uri = ('/%(category)s/symmetrix/'
                      '%(array)s/%(resource_type)s'
                      % {'version': version,
                         'category': category, 'array': array,
                         'resource_type': resource_type})
        if resource_name:
            target_uri += '/%(resource_name)s' % {
                'resource_name': resource_name}
        if version:
            target_uri = ('/%(version)s%(target)s'
                          % {'version': version, 'target': target_uri})
        return target_uri

    def _get_request(self, target_uri, resource_type, params=None):
        """Send a GET request to the array.

        :param target_uri: the target uri
        :param resource_type: the resource type, e.g. maskingview
        :param params: optional dict of filter params
        :returns: resource_object -- dict or None
        """
        resource_object = None
        message, sc = self.request(target_uri, GET, params=params)
        operation = 'get %(res)s' % {'res': resource_type}
        try:
            self.check_status_code_success(operation, sc, message)
        except Exception as e:
            LOG.debug("Get resource failed with %(e)s",
                      {'e': e})
        if sc == STATUS_200:
            resource_object = message
        return resource_object, sc

    def get_resource(self, array, category, resource_type,
                     resource_name=None, params=None):
        """Get resource details from array.

        :param array: the array serial number
        :param category: the resource category e.g. sloprovisioning
        :param resource_type: the resource type e.g. maskingview
        :param resource_name: the name of a specific resource
        :param params: query parameters
        :returns: resource object -- dict or None
        """
        target_uri = self._build_uri(array, category, resource_type,
                                     resource_name)
        return self._get_request(target_uri, resource_type, params)

    def create_resource(self, array, category, resource_type, payload,
                        version=None):
        """Create a provisioning resource.

        :param array: the array serial number
        :param category: the category
        :param resource_type: the resource type
        :param payload: the payload
        :param version: the U4V version
        :returns: status_code -- int, message -- string, server response
        """
        target_uri = self._build_uri(array, category, resource_type,
                                     version)
        message, status_code = self.request(target_uri, POST,
                                            request_object=payload)
        operation = 'Create %(res)s resource' % {'res': resource_type}
        self.check_status_code_success(
            operation, status_code, message)
        return message, status_code

    def modify_resource(self, array, category, resource_type, payload,
                        version=None, resource_name=None):
        """Modify a resource.

        :param version: the uv4 version
        :param array: the array serial number
        :param category: the category
        :param resource_type: the resource type
        :param payload: the payload
        :param resource_name: the resource name
        :returns: status_code -- int, message -- string (server response)
        """
        if version is None:
            version = self.U4V_VERSION
        target_uri = self._build_uri(array, category, resource_type,
                                     resource_name, version)
        message, status_code = self.request(target_uri, PUT,
                                            request_object=payload)
        operation = 'modify %(res)s resource' % {'res': resource_type}
        self.check_status_code_success(operation, status_code, message)
        return message, status_code

    def delete_resource(
            self, array, category, resource_type, resource_name,
            payload=None, params=None):
        """Delete a provisioning resource.

        :param array: the array serial number
        :param category: the resource category e.g. sloprovisioning
        :param resource_type: the type of resource to be deleted
        :param resource_name: the name of the resource to be deleted
        :param payload: the payload, optional
        :param params: dict of optional query params
        """
        version = self.U4V_VERSION
        target_uri = self._build_uri(array, category, resource_type,
                                     resource_name, version=version)
        message, status_code = self.request(target_uri, DELETE,
                                            request_object=payload,
                                            params=params, stream=False)
        operation = 'delete %(res)s resource' % {'res': resource_type}
        self.check_status_code_success(operation, status_code, message)

    @staticmethod
    def create_list_from_file(file_name):
        """Given a file, create a list from its contents.

        :param file_name: the path to the file
        :return: list of contents
        """
        with open(file_name) as f:
            list_item = f.readlines()
        raw_list = map(lambda s: s.strip(), list_item)
        return list(raw_list)

    @staticmethod
    def read_csv_values(file_name):
        """Reads any csv file with headers.

        You can extract the multiple lists from the headers in the CSV file.
        In your own script, call this function and assign to data variable,
        then extract the lists to the variables. Example:
        data=ru.read_csv_values(mycsv.csv)
        sgnamelist = data['sgname']
        policylist = data['policy']
        :param file_name CSV file
        :return: Dictionary of data parsed from CSV
        """
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

    def get_all_alerts(self, filters=None):
        """Queries for a list of All Alert ids across all symmetrix arrays.

        Optionally can be filtered by: create_date_milliseconds(=<>),
        description(=<>), type, severity, state, created_date, acknowledged.
        :param filters: dict of filters - optional
        :return: dict, status_code
        """
        target_uri = "/%s/univmax/restapi/system/alert" % self.U4V_VERSION
        return self._get_request(target_uri, 'alert', params=filters)

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
        target_uri = "/%s/system/job" % self.U4V_VERSION
        return self._get_request(target_uri, 'job', params=filters)

    def get_symmetrix_array(self, array_id=None):
        """Returns a list of arrays, or details on a specific array.

        :param array_id: the array serial number
        :return: dict, status_code
        """
        target_uri = "/%s/system/symmetrix" % self.U4V_VERSION
        if array_id:
            target_uri += "/%s" % array_id
        return self._get_request(target_uri, 'symmetrix')

    def get_array_jobs(self, job_id=None, filters=None):
        """Call queries for a list of Job ids for the specified symmetrix.

        The optional filters are: scheduled_date, name, completed_date,
        username, scheduled_date_milliseconds,
        last_modified_date_milliseconds, last_modified_date,
        completed_date_milliseconds (all params including =,<, or >),
        status (=).
        :param job_id: specific ID of the job (optional)
        :param filters: dict of filters - optional
        :return: dict, status_code
        """
        if job_id and filters:
            msg = "job_id and filters are mutually exclusive options"
            LOG.error(msg)
            raise exception.InvalidInputException(data=msg)
        return self.get_resource(self.array_id, 'system', 'job',
                                 resource_name=job_id, params=filters)

    def get_array_alerts(self, alert_id=None, filters=None):
        """Queries for a list of Alert ids for the specified symmetrix.

        The optional filters are: create_date_milliseconds(=<>),
        description(=<>), type, severity, state, created_date, acknowledged.
        :param alert_id: specific id of the alert - optional
        :param filters: dict of filters - optional
        :return: dict, status_code
        """
        if alert_id and filters:
            msg = "alert_id and filters are mutually exclusive options"
            LOG.error(msg)
            raise exception.InvalidInputException(data=msg)
        return self.get_resource(self.array_id, 'system', 'alert',
                                 resource_name=alert_id, params=filters)

    def acknowledge_array_alert(self, alert_id):
        """Acknowledge a specified alert.

        Acknowledge is the only "PUT" (edit) option available.
        :param alert_id: the alert id - string
        :return: dict, status_code
        """
        payload = {"editAlertActionParam": "ACKNOWLEDGE"}
        return self.modify_resource(self.array_id, 'system', 'alert', payload,
                                    resource_name=alert_id)

    def delete_alert(self, alert_id):
        """Delete a specified alert.

        :param alert_id: the alert id - string
        :return: None, status code
        """
        return self.delete_resource(self.array_id, 'system',
                                    'alert', alert_id)

    def get_uni_version(self):
        target_uri = "/%s/system/version" % self.U4V_VERSION
        return self._get_request(target_uri, 'version')

    def get_vmax3_array_list(self):
        """Returns a list of V3 arrays in the environment.

        :return: server response
        """
        target_uri = "/%s/sloprovisioning/symmetrix" % self.U4V_VERSION
        return self._get_request(target_uri, 'symmetrix')

    def get_hosts(self, host_id=None, filters=None):
        """Get details on host(s) on the array.

        See documentation for applicable filters - only valid
        if no host is specified.
        :param host_id: the name of the host, optional
        :param filters: optional list of filters - dict
        :return: dict, status_code
        """
        if host_id and filters:
            LOG.error("Host_id and filters are mutually exclusive options")
            raise Exception
        return self.get_resource(self.array_id, SLOPROVISIONING, 'host',
                                 resource_name=host_id, params=filters)

    def create_host(self, host_name, initiator_list=None,
                    host_flags=None, init_file=None, async=False):
        """Create a host with the given initiators.

        Accepts either initiator_list or file.
        The initiators must not be associated with another host.
        :param host_name: the name of the new host
        :param initiator_list: list of initiators
                               e.g.[10000000ba873cbf, 10000000ba873cba]
        :param host_flags: dictionary of optional host flags to apply
        :param init_file: full path and file name.
        :param async: Flag to indicate if call should be async
        :return: dict, status_code
        """
        if init_file:
            initiator_list = self.create_list_from_file(init_file)

        if not init_file and not initiator_list:
            msg = ("No file or initiator_list supplied, "
                   "you must specify one or the other")
            raise exception.InvalidInputException(data=msg)
        new_ig_data = ({"hostId": host_name, "initiatorId": initiator_list})
        if host_flags:
            new_ig_data.update({"hostFlags": host_flags})
        if async:
            new_ig_data.update({"executionOption": ASYNCHRONOUS})
        return self.create_resource(self.array_id, SLOPROVISIONING,
                                    'host', new_ig_data)

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
        return self.modify_resource(
            self.array_id, SLOPROVISIONING, 'host', edit_host_data,
            resource_name=host_id)

    def delete_host(self, host_id):
        """Delete a given host.

        Cannot delete if associated with a masking view
        :param host_id: name of the host
        :return: dict, status_code
        """
        return self.delete_resource(self.array_id, SLOPROVISIONING,
                                    'host', host_id)

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

    def get_hostgroups(self, hostgroup_id=None, filters=None):
        """Get details on hostgroup(s) on the array.

        See unisphere documentation for applicable filters - only valid
        if no host is specified.
        :param hostgroup_id: the name of the hostgroup, optional
        :param filters: optional list of filters - dict
        :return: dict, status_code
        """
        if hostgroup_id and filters:
            LOG.error("hostgroup_id and filters are mutually exclusive "
                      "options")
            raise Exception
        return self.get_resource(self.array_id, SLOPROVISIONING, 'hostgroup',
                                 resource_name=hostgroup_id, params=filters)

    def create_hostgroup(self, hostgroup_id, host_list,
                         host_flags=None, async=False):
        """Create a hostgroup containing the given hosts.

        :param hostgroup_id: the name of the new hostgroup
        :param host_list: list of hosts
        :param host_flags: dictionary of optional host flags to apply
        :param async: Flag to indicate if call should be async
        :return: dict, status_code
        """
        new_ig_data = ({"hostId": host_list, "hostGroupId": hostgroup_id})
        if host_flags:
            new_ig_data.update({"hostFlags": host_flags})
        if async:
            new_ig_data.update({"executionOption": ASYNCHRONOUS})
        return self.create_resource(self.array_id, SLOPROVISIONING,
                                    'hostgroup', new_ig_data)

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
        return self.modify_resource(
            self.array_id, SLOPROVISIONING, 'hostgroup', edit_host_data,
            resource_name=hostgroup_id)

    def delete_hostgroup(self, hostgroup_id):
        """Delete a given hostgroup.

        Cannot delete if associated with a masking view
        :param hostgroup_id: name of the hostgroup
        :return: dict, status_code
        """
        return self.delete_resource(self.array_id, SLOPROVISIONING,
                                    'hostgroup', hostgroup_id)

    def get_initiators(self, initiator_id=None, filters=None):
        """Lists initiators on a given array.

        See UniSphere documenation for full list of filters.
        Can filter by initiator_id OR filters.
        :param initiator_id: initiator id, optional
        :param filters: Optional filters - dict
        :return: initiator list
        """
        if initiator_id and filters:
            msg = "Initiator_id and filters are mutually exclusive"
            LOG.error(msg)
            raise exception.InvalidInputException(data=msg)
        return self.get_resource(self.array_id, SLOPROVISIONING, 'initiator',
                                 resource_name=initiator_id, params=filters)

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
        :return: dict, status_code
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
            LOG.error(msg)
            raise exception.InvalidInputException(data=msg)
        return self.modify_resource(
            self.array_id, SLOPROVISIONING, 'initiator', edit_init_data,
            version='', resource_name=initiator_id)

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

    def get_initiator_list(self, params=None):
        """Retrieve initiator list from the array.

        :param params: dict of optional params
        :returns: list of initiators
        """
        init_dict, _ = self.get_resource(
            self.array_id, SLOPROVISIONING, 'initiator', params=params)
        try:
            init_list = init_dict['initiatorId']
        except KeyError:
            init_list = []
        return init_list

    def get_in_use_initiator_list_from_array(self):
        """Get the list of initiators which are in-use from the array.

        Gets the list of initiators from the array which are in
        hosts/ initiator groups.
        :returns: init_list
        """
        params = {'in_a_host': 'true'}
        return self.get_initiator_list(params)

    def get_initiator_group_from_initiator(self, initiator):
        """Given an initiator, get its corresponding initiator group, if any.

        :param initiator: the initiator id
        :returns: found_init_group_name -- string
        """
        found_init_group_name = None
        init_details, _ = self.get_initiators(initiator_id=initiator)
        if init_details:
            found_init_group_name = init_details.get('host')
        else:
            LOG.error("Unable to retrieve initiator details for "
                      "%(init)s.", {'init': initiator})
        return found_init_group_name

    def get_masking_views(self, masking_view_id=None, filters=None):
        """Get a masking view or list of masking views.

        If masking_view_id, return details of a particular masking view.
        Either masking_view_id or filters can be set
        :param masking_view_id: the name of the masking view
        :param filters: dictionary of filters
        :return: dict, status_code
        """
        if masking_view_id and filters:
            LOG.error("masking_view_id and filters are mutually exclusive")
            raise Exception
        return self.get_resource(
            self.array_id, SLOPROVISIONING, 'maskingview',
            resource_name=masking_view_id, params=filters)

    def get_masking_view(self, masking_view_name):
        """Get details of a masking view.

        :param masking_view_name: the masking view name
        :returns: masking view dict
        """
        return self.get_masking_views(masking_view_id=masking_view_name)

    def get_masking_view_list(self, params):
        """Get a list of masking views from the array.

        :param params: optional GET parameters
        :returns: masking view list
        """
        masking_view_list = []
        masking_view_details, sc = self.get_masking_views(filters=params)
        try:
            masking_view_list = masking_view_details['maskingViewId']
        except (KeyError, TypeError):
            pass
        return masking_view_list

    def create_masking_view_existing_components(
            self, port_group_name, masking_view_name,
            storage_group_name, host_name=None,
            host_group_name=None, async=False):
        """Create a new masking view using existing groups.

        Must enter either a host name or a host group name, but
        not both.
        :param port_group_name: name of the port group
        :param masking_view_name: name of the new masking view
        :param storage_group_name: name of the storage group
        :param host_name: name of the host (initiator group)
        :param host_group_name: name of host group
        :param async: flag to indicate if command should be run asynchronously
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
        payload = ({"portGroupSelection": {
                        "useExistingPortGroupParam": {
                            "portGroupId": port_group_name}},
                    "maskingViewId": masking_view_name,
                    "hostOrHostGroupSelection": host_details,
                    "storageGroupSelection": {
                        "useExistingStorageGroupParam": {
                            "storageGroupId": storage_group_name}}})
        if async:
            payload.update({"executionOption": ASYNCHRONOUS})

        return self.create_resource(
            self.array_id, SLOPROVISIONING, 'maskingview', payload)

    def get_masking_views_from_storage_group(self, storagegroup):
        """Return any masking views associated with a storage group.

        :param storagegroup: the storage group name
        :returns: masking view list
        """
        maskingviewlist = []
        storagegroup = self.get_storage_group(storagegroup)
        if storagegroup and storagegroup.get('maskingview'):
            maskingviewlist = storagegroup['maskingview']
        return maskingviewlist

    def get_masking_views_by_host(self, initiatorgroup_name):
        """Given a host (initiator group), retrieve the masking view name.

        Retrieve the list of masking views associated with the
        given initiator group.
        :param initiatorgroup_name: the name of the initiator group
        :returns: list of masking view names
        """
        masking_view_list = []
        ig_details, _ = self.get_hosts(host_id=initiatorgroup_name)
        if ig_details:
            if ig_details.get('maskingview'):
                masking_view_list = ig_details['maskingview']
        else:
            LOG.error("Error retrieving initiator group %(ig_name)s",
                      {'ig_name': initiatorgroup_name})
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
        masking_view_details, sc = self.get_masking_view(maskingview_name)
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
            LOG.error(exception_message)
            raise exception.ResourceNotFoundException(data=exception_message)
        return element

    def get_common_masking_views(self, portgroup_name, ig_name):
        """Get common masking views for a given portgroup and initiator group.

        :param portgroup_name: the port group name
        :param ig_name: the initiator group name
        :returns: masking view list
        """
        params = {'port_group_name': portgroup_name,
                  'host_or_host_group_name': ig_name}
        masking_view_list = self.get_masking_view_list(params)
        if not masking_view_list:
            LOG.info("No common masking views found for %(pg_name)s "
                     "and %(ig_name)s.",
                     {'pg_name': portgroup_name, 'ig_name': ig_name})
        return masking_view_list

    def delete_masking_view(self, array, maskingview_name):
        """Delete a masking view.

        :param array: the array serial number
        :param maskingview_name: the masking view name
        """
        return self.delete_resource(
            array, SLOPROVISIONING, 'maskingview', maskingview_name)

    def modify_masking_view(self, masking_view_id, new_name):
        """Modify an existing masking view.

        Currently, the only supported modification is "rename".
        :param masking_view_id: the current name of the masking view
        :param new_name: the new name of the masking view
        :return: dict, status_code
        """
        mv_payload = {"editMaskingViewActionParam": {
            "renameMaskingViewParam": {"new_masking_view_name": new_name}}}
        return self.modify_resource(
            self.array_id, SLOPROVISIONING, 'maskingview', mv_payload,
            version='', resource_name=masking_view_id)

    def get_host_from_mv(self, masking_view_id):
        """Given a masking view, get the associated host or host group.

        :param masking_view_id: the name of the masking view
        :return: host ID
        """
        return self.get_element_from_masking_view(masking_view_id, host=True)

    def get_sg_from_mv(self, masking_view_id):
        """Given a masking view, get the associated storage group.

        :param masking_view_id: the masking view name
        :return: the name of the storage group
        """
        return self.get_element_from_masking_view(
            self.array_id, masking_view_id, storagegroup=True)

    def get_pg_from_mv(self, masking_view_id):
        """Given a masking view, get the associated port group.

        :param masking_view_id: the masking view name
        :return: the name of the port group
        """
        return self.get_element_from_masking_view(
            masking_view_id, portgroup=True)

    def get_mv_connections(self, mv_name):
        """Get all connection information for a given masking view.

        :param mv_name: the name of the masking view
        :return: dict, status_code
        """
        res_name = "%s/connections" % mv_name
        return self.get_resource(self.array_id, SLOPROVISIONING,
                                 'maskingview', resource_name=res_name)

    def get_ports(self, filters=None):
        """Queries for a list of Symmetrix port keys.

        Note a mixture of Front end, back end and RDF port specific values
        are not allowed. See UniSphere documentation for possible values.
        :param filters: dictionary of filters e.g. {'vnx_attached': 'true'}
        :return: dict, status_code
        """
        return self.get_resource(self.array_id, SLOPROVISIONING, 'port',
                                 params=filters)

    def get_portgroups(self, portgroup_id=None, filters=None):
        """Get portgroup(s) details.

        :param portgroup_id: the name of the portgroup
        :param filters: dictionary of filters
        :return: dict, status_code
        """
        if portgroup_id and filters:
            LOG.error("portgroup_id and filters are mutually exclusive")
            raise Exception
        return self.get_resource(self.array_id, SLOPROVISIONING, 'portgroup',
                                 resource_name=portgroup_id, params=filters)

    def get_director(self, director=None):
        """Queries for details of Symmetrix directors for a symmetrix

        :param director: the director ID e.g. FA-1D - optional
        :return: dict, status_code
        """
        return self.get_resource(self.array_id, SLOPROVISIONING, 'director',
                                 director)

    def get_director_port(self, director, port_no=None, filters=None):
        """Get details of the symmetrix director port.

        Can be filtered by optional parameters, please see documentation.
        :param director: the director ID e.g. FA-1D
        :param port_no: the port number e.g. 1 - optional
        :param filters: optional filters - dict
        :return: dict, status_code
        """
        res_name = "%s/port/%s" % (director, port_no) if port_no else director
        if port_no and filters:
            LOG.error("portNo and filters are mutually exclusive options")
            raise Exception
        return self.get_resource(self.array_id, SLOPROVISIONING, 'director',
                                 resource_name=res_name, params=filters)

    def get_port_identifier(self, director, port_no):
        """Get the identifier (wwn) of the physical port.

        :param director: the ID of the director
        :param port_no: the number of the port
        :return: wwn (FC) or iqn (iscsi), or None
        """
        wwn = None
        port_info, _ = self.get_director_port(director, port_no)
        if port_info:
            try:
                wwn = port_info['symmetrixPort']['identifier']
            except KeyError:
                LOG.error("Cannot retrieve port information")
        return wwn

    def get_ports_from_pg(self, portgroup):
        """Get a list of port identifiers from a port group.

        :param portgroup: the name of the portgroup
        :returns: list of port ids, e.g. ['FA-3D:35', 'FA-4D:32']
        """
        portlist = []
        portgroup_info, _ = self.get_portgroups(portgroup_id=portgroup)
        if portgroup_info:
            port_key = portgroup_info["symmetrixPortKey"]
            for key in port_key:
                port = key['portId']
                portlist.append(port)
        return portlist

    def get_target_wwns_from_pg(self, portgroup):
        """Get the director ports' wwns.

        :param portgroup: portgroup
        :returns: target_wwns -- the list of target wwns for the pg
        """
        target_wwns = []
        port_ids, _ = self.get_ports_from_pg(portgroup)
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
        ip_addresses, iqn = None, None
        dir_id = port_id.split(':')[0]
        port_no = port_id.split(':')[1]
        port_details, _ = self.get_director_port(dir_id, port_no)
        if port_details:
            ip_addresses = port_details['symmetrixPort']['ip_addresses']
            iqn = port_details['symmetrixPort']['identifier']
        return ip_addresses, iqn

    def create_portgroup(self, portgroup_id, director_id, port_id):
        """Create a new portgroup.

        :param portgroup_id: the name of the new port group
        :param director_id: the directoy id
        :param port_id: the port id
        :return: dict, status_code
        """
        payload = ({"portGroupId": portgroup_id,
                    "symmetrixPortKey": [{"directorId": director_id,
                                          "portId": port_id}]})
        return self.create_resource(
            self.array_id, SLOPROVISIONING, 'portgroup', payload)

    def create_multiport_portgroup(self, portgroup_id, ports):
        """Create a new portgroup.

        :param portgroup_id: the name of the new port group
        :param ports: list of port dicts - {"directorId": director_id,
                                            "portId": port_id}
        :return: dict, status_code
        """
        payload = ({"portGroupId": portgroup_id,
                    "symmetrixPortKey": ports})
        return self.create_resource(
            self.array_id, SLOPROVISIONING, 'portgroup', payload)

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
        return self.modify_resource(
            self.array_id, SLOPROVISIONING, 'portgroup', edit_pg_data,
            version='', resource_name=portgroup_id)

    def delete_portgroup(self, portgroup_id):
        """Delete a portgroup.

        :param portgroup_id: the name of the portgroup
        :return: dict, status_code
        """
        return self.delete_resource(self.array_id, SLOPROVISIONING,
                                    'portgroup', portgroup_id)

    def extract_directorId_pg(self, portgroup):
        """Get the symm director information from the port group.

        :param portgroup: the name of the portgroup
        :return: the director information
        """
        info, sc = self.get_portgroups(portgroup_id=portgroup)
        try:
            port_key = info["portGroup"]["symmetrixPortKey"]
            return port_key
        except KeyError:
            LOG.error("Cannot find port key information from given portgroup")

    def get_workload_settings(self, array):
        """Get valid workload options from array.

        :param array: the array serial number
        :returns: workload_setting -- list of workload names
        """
        workload_setting = []
        wl_details, _ = self.get_resource(array, SLOPROVISIONING, 'workloadtype')
        if wl_details:
            workload_setting = wl_details['workloadId']
        return workload_setting

    def get_SLO(self, slo_id=None):
        """Gets a list of available SLO's on a given array, or returns
        details on a specific SLO if one is passed in in the parameters.

        :param slo_id: the service level agreement, optional
        :return: dict, status_code
        """
        return self.get_resource(self.array_id, SLOPROVISIONING, 'slo',
                                 resource_name=slo_id)

    def modify_slo(self, slo_id, new_name):
        """Modify an SLO.

        Currently, the only modification permitted is renaming.
        :param slo_id: the current name of the slo
        :param new_name: the new name for the slo
        :return: dict, status_code
        """
        edit_slo_data = ({"editSloActionParam": {
            "renameSloParam": {"sloId": new_name}}})
        return self.modify_resource(
            self.array_id, SLOPROVISIONING, 'host', edit_slo_data,
            version='', resource_name=slo_id)

    def get_wlp_timestamp(self):
        """Get the latest timestamp from WLP for processing New Workloads.

        :return: dict, status_code
        """
        target_uri = ("/%s/wlp/symmetrix/%s"
                      % (self.U4V_VERSION, self.array_id))
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
        params = {'srp': srp, 'slo': slo, 'workloadtype': workload}
        return self.get_resource(self.array_id, 'wlp',
                                 'headroom', params=params)

    def get_headroom_capacity(self, srp, slo, workload):
        """Get capacity of the different slo/ workload combinations.

        :param srp: the storage resource srp
        :param slo: the service level
        :param workload: the workload
        :returns: remaining_capacity -- string, or None
        """
        try:
            headroom, _ = self.get_headroom(workload, srp, slo)
            remaining_capacity = headroom['headroom'][0]['headroomCapacity']
        except (KeyError, TypeError):
            remaining_capacity = None
        return remaining_capacity

    def get_srp(self, srp=None):
        """Gets a list of available SRP's on a given array, or returns
        details on a specific SRP if one is passed in in the parameters.

        :param srp: the storage resource pool, optional
        :return: dict, status_code
        """
        return self.get_resource(self.array_id, SLOPROVISIONING, 'srp',
                                 resource_name=srp)

    def get_slo_list(self):
        """Retrieve the list of slo's from the array

        :returns: slo_list -- list of service level names
        """
        slo_list = []
        slo_dict, _ = self.get_SLO()
        if slo_dict and slo_dict.get('sloId'):
            slo_list = slo_dict['sloId']
        return slo_list

    def is_compression_capable(self):
        """Check if array is compression capable.

        :returns: bool
        """
        is_compression_capable = False
        target_uri = ("/%s/sloprovisioning/symmetrix?compressionCapable=true"
                      % self.U4V_VERSION)
        message, status_code = self.request(target_uri, GET)
        self.check_status_code_success(
            "Check if compression enabled", status_code, message)
        if message.get('symmetrixId'):
            if self.array_id in message['symmetrixId']:
                is_compression_capable = True
        return is_compression_capable

    def get_sg(self, sg_id=None, filters=None):
        """Gets details of all storage groups on a given array, or returns
        details on a specific sg if one is passed in in the parameters.

        :param sg_id: the storage group name, optional
        :param filters: dictionary of filters e.g.
                       {'child': 'true', 'srp_name': '=SRP_1'}
        :return: dict, status_code
        """
        if sg_id and filters:
            LOG.error("sg_id and filters are mutually exclusive")
            raise Exception()
        return self.get_resource(
            self.array_id, SLOPROVISIONING, 'storagegroup',
            resource_name=sg_id, params=filters)

    def get_storage_group(self, storage_group_name):
        """Given a name, return storage group details.

        :param storage_group_name: the name of the storage group
        :returns: storage group dict or None
        """
        sg_details, sc = self.get_sg(sg_id=storage_group_name)
        return sg_details

    def get_storage_group_list(self, params=None):
        """"Return a list of storage groups.

        :param params: optional filter parameters
        :returns: storage group list
        """
        sg_list = []
        sg_details, _ = self.get_sg(filters=params)
        if sg_details:
            sg_list = sg_details['storageGroupId']
        return sg_list

    def create_non_empty_storagegroup(
            self, srpID, sg_id, slo, workload, num_vols, vol_size,
            capUnit, disable_compression=False, async=False):
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
        :param async: Flag to indicate if this call should be async
        :return: dict, status_code
        """
        return self.create_storage_group(
            srpID, sg_id, slo, workload,
            do_disable_compression=disable_compression,
            num_vols=num_vols, vol_size=vol_size, cap_unit=capUnit,
            async=async)

    def create_empty_sg(self, srp_id, sg_id, slo, workload,
                        disable_compression=False, async=False):
        """Generates a dictionary for json formatting and calls
        the create_sg function to create an empty storage group
        Set the disable_compression flag for
        disabling compression on an All Flash array (where compression
        is on by default).
        :param srp_id: the storage resource pool
        :param sg_id: the name of the new storage group
        :param slo: the service level agreement (e.g. Gold)
        :param workload: the workload (e.g. DSS)
        :param disable_compression: flag for disabling compression (AF only)
        :param async: Flag to indicate if this call should be async
        :return: dict, status_code
        """
        return self.create_storage_group(
            srp_id, sg_id, slo, workload,
            do_disable_compression=disable_compression, async=async)

    def modify_storagegroup(self, sg_id, edit_sg_data):
        """Edits an existing storage group

        :param sg_id: the name of the storage group
        :param edit_sg_data: the payload of the request
        :return: dict, status_code
        """
        return self.modify_resource(
            self.array_id, SLOPROVISIONING, 'storagegroup', edit_sg_data,
            version=None, resource_name=sg_id)

    def add_existing_vol_to_sg(self, sg_id, vol_id, async=False):
        """Expand an existing storage group by adding new volumes.

        :param sg_id: the name of the storage group
        :param vol_id: the device id of the volume - can be list
        :param async: Flag to indicate if the call should be async
        :return: dict, status_code
        """
        if not isinstance(vol_id, list):
            vol_id = [vol_id]
        add_vol_data = {"editStorageGroupActionParam": {
            "expandStorageGroupParam": {
                "addSpecificVolumeParam": {
                    "volumeId": vol_id}}}}
        if async:
            add_vol_data.update({'executionOption': ASYNCHRONOUS})
        if self.U4V_VERSION == '83':
            add_vol_data = {"editStorageGroupActionParam": {
                "addVolumeParam": {"volumeId": vol_id}}}
        return self.modify_storagegroup(sg_id, add_vol_data)

    def add_new_vol_to_storagegroup(self, sg_id, num_vols, vol_size,
                                    capUnit, async=False, vol_name=None):
        """Expand an existing storage group by adding new volumes.

        :param sg_id: the name of the storage group
        :param num_vols: the number of volumes
        :param vol_size: the size of the volumes
        :param capUnit: the capacity unit
        :param async: Flag to indicate if call should be async
        :param vol_name: name to give to the volume, optional
        :return: dict, status_code
        """
        add_vol_info = {
                    "num_of_vols": num_vols,
                    "emulation": "FBA",
                    "volumeAttribute": {
                        "volume_size": vol_size,
                        "capacityUnit": capUnit}}
        if vol_name:
            add_vol_info.update({
                "volumeIdentifier": {
                    "identifier_name": vol_name,
                    "volumeIdentifierChoice": "identifier_name"}})
        expand_sg_data = {"editStorageGroupActionParam": {
            "expandStorageGroupParam": {
                "addVolumeParam": add_vol_info}}}
        if async:
            expand_sg_data.update({"executionOption": ASYNCHRONOUS})
        return self.modify_storagegroup(sg_id, expand_sg_data)

    def remove_vol_from_storagegroup(self, sg_id, vol_id, async=False):
        """Remove a volume from a given storage group

        :param sg_id: the name of the storage group
        :param vol_id: the device id of the volume
        :param async: Flag to indicate if call should be async
        :return: dict, status_code
        """
        if not isinstance(vol_id, list):
            vol_id = [vol_id]
        payload = {"editStorageGroupActionParam": {
            "removeVolumeParam": {"volumeId": vol_id}}}
        if async:
            payload.update({'executionOption': ASYNCHRONOUS})
        return self.modify_storagegroup(sg_id, payload)

    def move_vol_between_storagegroup(self, src_sg_id, tgt_sg_id,
                                      vol_id, async=False):
        """MOve volumes between storage groups.

        :param src_sg_id: the name of the source storage group
        :param tgt_sg_id: the name of the target sg
        :param vol_id: the device id of the volume
        :param async: Flag to indicate if call should be async
        :return: dict, status_code
        """
        if not isinstance(vol_id, list):
            vol_id = [vol_id]
        payload = {"editStorageGroupActionParam": {
            "moveVolumeToStorageGroupParam": {
                "storageGroupId": tgt_sg_id,
                "volumeId": vol_id, "force": 'true'}}}
        if async:
            payload.update({'executionOption': ASYNCHRONOUS})
        return self.modify_storagegroup(src_sg_id, payload)

    def delete_sg(self, sg_id):
        """Delete a given storage group.

        A storage group cannot be deleted if it
        is associated with a masking view
        :param sg_id: the name of the storage group
        :return: dict, status_code
        """
        return self.delete_resource(
            self.array_id, SLOPROVISIONING, 'storagegroup', sg_id)

    def get_mv_from_sg(self, storage_group):
        """Get the associated masking view(s) from a given storage group

        :param storage_group: the name of the storage group
        :return: Masking view list, or None
        """
        response, sc = self.get_sg(storage_group)
        mvlist = response["maskingview"]
        if len(mvlist) > 0:
            return mvlist
        else:
            return None

    def set_hostIO_limit_IOPS(self, storage_group, iops, dynamic_distribution):
        """Set the HOSTIO Limits on an existing storage group.

        :param storage_group: String up to 32 Characters
        :param dynamic_distribution: valid values Always, Never, OnFailure
        :param iops: integer value. Min Value 100, must be specified to
                     nearest 100, e.g.202 is not a valid value
        :return: dict, status_code
        """
        qos_specs = {'maxIOPS': iops,
                     'DistributionType': dynamic_distribution}
        return self.update_storagegroup_qos(storage_group, qos_specs)

    def get_num_vols_in_sg(self, storage_group_name):
        """Get the number of volumes in a storage group.

        :param storage_group_name: the storage group name
        :returns: num_vols -- int
        """
        num_vols = 0
        storagegroup = self.get_storage_group(storage_group_name)
        try:
            num_vols = int(storagegroup['num_of_vols'])
        except (KeyError, TypeError):
            pass
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

    def _create_storagegroup(self, payload):
        """Create a storage group.

        :param payload: the payload -- dict
        :returns: status_code -- int, message -- string, server response
        """
        return self.create_resource(
            self.array_id, SLOPROVISIONING, 'storagegroup', payload)

    def create_storage_group(self, srp_id, sg_id, slo, workload,
                             do_disable_compression=False,
                             num_vols=0, vol_size="0", cap_unit="GB",
                             async=False):
        """Create the volume in the specified storage group.

        :param srp_id: the SRP (String)
        :param sg_id: the group name (String)
        :param slo: the SLO (String)
        :param workload: the workload (String)
        :param do_disable_compression: flag for disabling compression
        :param num_vols: number of volumes to be created
        :param vol_size: the volume size
        :param cap_unit: the capacity unit (MB, GB, TB, CYL)
        :param async: Flag to indicate if call should be async
        :returns: storagegroup_name - string
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

            payload.update({"sloBasedStorageGroupParam": [slo_param]})

        if async:
            payload.update({"executionOption": ASYNCHRONOUS})

        return self._create_storagegroup(payload)

    def modify_storage_group(self, storagegroup, payload):
        """Modify a storage group (PUT operation).

        :param storagegroup: storage group name
        :param payload: the request payload
        :returns: message -- dict, server response, status_code -- int,
        """
        return self.modify_resource(
            self.array_id, SLOPROVISIONING, 'storagegroup',
            payload, resource_name=storagegroup)

    def create_volume_from_sg_return_dev_id(
            self, volume_name, storagegroup_name, vol_size):
        """Create a new volume in the given storage group.

        Create a new volume
        :param volume_name: the volume name (String)
        :param storagegroup_name: the storage group name
        :param vol_size: volume size (String)
        :returns: job, status_code, device_id
        :raises: VolumeBackendAPIException
        """
        job, status_code = self.add_new_vol_to_storagegroup(
            storagegroup_name, 1, vol_size, "GB",
            async=True, vol_name=volume_name)
        LOG.debug("Create Volume: %(volumename)s. Status code: %(sc)lu.",
                  {'volumename': volume_name,
                   'sc': status_code})

        task = self.wait_for_job('Create volume', status_code, job)

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

        return job, status_code, device_id

    def update_storagegroup_qos(self, storage_group_name, qos_specs):
        """Update the storagegroupinstance with qos details.

        If maxIOPS or maxMBPS is in qos_specs, then DistributionType can be
        modified in addition to maxIOPS or/and maxMBPS
        If maxIOPS or maxMBPS is NOT in qos_specs, we check to see if
        either is set in StorageGroup. If so, then DistributionType can be
        modified.
        Example qos specs: {'maxIOPS': '4000', 'maxMBPS': '4000',
                            'DistributionType': 'Dynamic'}
        :param storage_group_name: the storagegroup instance name
        :param qos_specs: the qos specifications
        :returns: bool, True if updated, else False
        """
        message, sc = None, 401
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
            message, sc = (
                self.modify_storage_group(storage_group_name, payload))
        return message, sc

    def move_volume_between_storage_groups(
            self, device_id, source_storagegroup_name,
            target_storagegroup_name, force=False):
        """Move a volume to a different storage group.

        Note: 8.4.0.7 or later
        :param source_storagegroup_name: the originating storage group name
        :param target_storagegroup_name: the destination storage group name
        :param device_id: the device id - can be list
        :param force: force flag (necessary on a detach)
        """
        force_flag = "true" if force else "false"
        if not isinstance(device_id, list):
            device_id = [device_id]
        payload = ({"executionOption": "ASYNCHRONOUS",
                    "editStorageGroupActionParam": {
                        "moveVolumeToStorageGroupParam": {
                            "volumeId": device_id,
                            "storageGroupId": target_storagegroup_name,
                            "force": force_flag}}})
        return self.modify_storage_group(source_storagegroup_name, payload)

    def get_volumes(self, vol_id=None, filters=None):
        """Gets details of volume(s) from array.

        :param vol_id: the volume's device ID
        :param filters: dictionary of filters
        :return: dict, status_code
        """
        if vol_id and filters:
            LOG.error("volID and filters are mutually exclusive.")
            raise Exception()
        return self.get_resource(self.array_id, SLOPROVISIONING, 'volume',
                                 resource_name=vol_id, params=filters)

    def get_vol_effectivewwn_details_84(self, vollist):
        """
        Get volume details for a list of volumes usually
        obtained for get_vols_from_SG
        using 84 endpoint as this gives wwn details
        :param vollist:
        :return: Dictionary
        """
        """Create CSV and set headings"""
        with open(bytes('wwn_data.csv', 'UTF-8'), 'wt') as csvfile:
            eventwriter = csv.writer(csvfile,
                                     delimiter=',',
                                     quotechar='|',
                                     quoting=csv.QUOTE_MINIMAL)

            eventwriter.writerow(['volumeId', 'effective_wwn', 'wwn',
                                  'has_effective_wwn', 'storageGroupId'])
        for volume in vollist:
            voldetails, rc = self.get_volumes(vol_id=volume)
            volumeId = voldetails.get('volumeId')
            effective_wwn = voldetails.get('effective_wwn')
            wwn = voldetails.get('wwn')
            has_effective_wwn = voldetails.get('has_effective_wwn')
            storageGroupId = voldetails.get('storageGroupId')
            with open(bytes('wwn_data.csv', 'UTF-8'), 'a') as csvfile:
                eventwriter = csv.writer(csvfile,
                                         delimiter=',',
                                         quotechar='|',
                                         quoting=csv.QUOTE_MINIMAL)
                eventwriter.writerow([volumeId, effective_wwn, wwn,
                                      has_effective_wwn, storageGroupId])

    def get_deviceId_from_volume(self, vol_identifier):
        """Given the volume identifier (name), return the device ID

        :param vol_identifier: the identifier of the volume
        :return: the device ID of the volume
        """
        return self.find_volume_device_id(vol_identifier)

    def get_vols_from_SG(self, sg_id):
        """Retrieve volume information associated with a particular sg

        :param sg_id: the name of the storage group
        :return: list of device IDs of associated volumes
        """
        params = {"storageGroupId": sg_id}

        volume_list = self.get_list_of_dev_ids(params)
        if not volume_list:
            LOG.debug("Cannot find record for storage group %(storageGrpId)s",
                      {'volumeId': sg_id})
        return volume_list

    def get_SG_from_vols(self, vol_id):
        """Retrieves sg information for a specified volume.

        Note that a FAST managed volume cannot be a
        member of more than one storage group.
        :param vol_id: the device ID of the volume
        :return: list of storage groups, or None
        """
        sg_list = []
        vol = self.get_volume(vol_id)
        if vol and vol.get('storageGroupId'):
            sg_list = vol['storageGroupId']
        num_storage_groups = len(sg_list)
        LOG.debug("There are %(num)d storage groups associated "
                  "with volume %(deviceId)s.",
                  {'num': num_storage_groups, 'deviceId': vol_id})
        return sg_list

    def get_volume(self, device_id):
        """Get a VMAX volume from array.

        :param device_id: the volume device id
        :returns: volume dict
        :raises: ResourceNotFoundException
        """
        volume_dict, _ = self.get_volumes(vol_id=device_id)
        if not volume_dict:
            exception_message = ("Volume %(deviceID)s not found."
                                 % {'deviceID': device_id})
            LOG.error(exception_message)
            raise exception.ResourceNotFoundException(data=exception_message)
        return volume_dict

    def get_list_of_dev_ids(self, params):
        """Get a filtered list of VMAX volumes from array.

        Filter parameters are required as the unfiltered volume list could be
        very large and could affect performance if called often.
        :param params: filter parameters
        :returns: device_ids -- list
        """
        device_ids = []
        volumes, _ = self.get_volumes(filters=params)
        try:
            volume_dict_list = volumes['resultList']['result']
            for vol_dict in volume_dict_list:
                device_id = vol_dict['volumeId']
                device_ids.append(device_id)
        except (KeyError, TypeError):
            pass
        return device_ids

    def _modify_volume(self, device_id, payload):
        """Modify a volume (PUT operation).

        :param device_id: volume device id
        :param payload: the request payload
        """
        return self.modify_resource(self.array_id, SLOPROVISIONING, 'volume',
                                    payload, resource_name=device_id)

    def extend_volume(self, device_id, new_size, async=False):
        """Extend a VMAX volume.

        :param device_id: volume device id
        :param new_size: the new required size for the device
        :param async: flag to indicate if call should be async
        """
        extend_vol_payload = {"editVolumeActionParam": {
            "expandVolumeParam": {
                "volumeAttribute": {
                    "volume_size": new_size,
                    "capacityUnit": "GB"}}}}
        if async:
            extend_vol_payload.update({"executionOption": ASYNCHRONOUS})
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

    def delete_volume(self, device_id):
        """Delete a volume.

        :param device_id: volume device id
        """
        return self.delete_resource(
            self.array_id, SLOPROVISIONING, "volume", device_id)

    def deallocate_volume(self, device_id):
        """Deallocate all tracks on a volume.

        Necessary before deletion.
        :param device_id: the device id
        :return: dict, sc
        """
        payload = {"editVolumeActionParam": {
            "freeVolumeParam": {"free_volume": 'true'}}}
        return self._modify_volume(device_id, payload)

    def find_host_lun_id_for_vol(self, maskingview, device_id):
        """Find the host_lun_id for a volume in a masking view.

        :param maskingview: the masking view name
        :param device_id: the device ID
        :returns: host_lun_id -- int
        """
        host_lun_id = None
        resource_name = ('%(maskingview)s/connections'
                         % {'maskingview': maskingview})
        params = {'volume_id': device_id}
        connection_info, _ = self.get_resource(
            self.array_id, SLOPROVISIONING, 'maskingview',
            resource_name=resource_name, params=params)
        if not connection_info:
            LOG.error('Cannot retrive masking view connection information '
                      'for %(mv)s.', {'mv': maskingview})
        else:
            try:
                host_lun_id = (connection_info['maskingViewConnection']
                               [0]['host_lun_address'])
                host_lun_id = int(host_lun_id, 16)
            except Exception as e:
                LOG.error("Unable to retrieve connection information "
                          "for volume %(vol)s in masking view %(mv)s"
                          "Exception received: %(e)s.",
                          {'vol': device_id, 'mv': maskingview,
                           'e': e})
        return host_lun_id

    def is_volume_in_storagegroup(self, device_id, storagegroup):
        """See if a volume is a member of the given storage group.

        :param device_id: the device id
        :param storagegroup: the storage group name
        :returns: bool
        """
        is_vol_in_sg = False
        sg_list = self.get_SG_from_vols(device_id)
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

        volume_list = self.get_list_of_dev_ids(params)
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
        return vol['volume_identifier']

    def get_size_of_device_on_array(self, device_id):
        """Get the size of the volume from the array.

        :param device_id: the volume device id
        :returns: size --  or None
        """
        cap = None
        try:
            vol = self.get_volume(device_id)
            cap = vol['cap_gb']
        except Exception as e:
            LOG.error("Error retrieving size of volume %(vol)s. "
                      "Exception received was %(e)s.",
                      {'vol': device_id, 'e': e})
        return cap

    def find_low_volume_utilization(self, low_utilization_percentage, csvname):
        """
        Function to find volumes under a specified percentage, may be long
        running as will check all sg on array and all storage group.  Only
        identifies volumes in storage group,  note if volume is in more
        than one sg it may show up more than once.
        :param low_utilization_percentage: low utilization watermark
        percentage,
        e.g. find volumes with utilization less than 10%
        :param csvname: filename for CFV output file
        :return: will create csvfile with name passed
        """
        sg_dict, rc = self.get_sg()
        sg_list = sg_dict.get('storageGroupId')

        with open(bytes(csvname, 'UTF-8'), 'w', newline='') as csvfile:
            eventwriter = csv.writer(csvfile,
                                     delimiter=',',
                                     quotechar='|',
                                     quoting=csv.QUOTE_MINIMAL)

            eventwriter.writerow(["sgname", "volumeid", "identifier",
                                  "capacity", "allocated_Percent"])

            for sg in sg_list:
                vollist = self.get_vols_from_SG(sg)

                for vol in vollist:
                    volume = self.get_volume(vol)
                    if volume[
                        "allocated_percent"] < low_utilization_percentage:
                        allocated = volume["allocated_percent"]
                        try:
                            vol_identifiers = (volume["volume_identifier"])
                        except:
                            vol_identifiers = ("No Identifier")
                    vol_cap = (volume["cap_gb"])
                    eventwriter.writerow(
                        [sg, vol, vol_identifiers, vol_cap, allocated])

    def get_replication_info(self):
        """Return replication information for an array.

        :return: dict, status_code
        """
        target_uri = '/83/replication/symmetrix/%s' % self.array_id
        return self._get_request(target_uri, 'replication info')

    def check_snap_capabilities(self):
        """Check what replication facilities are available

        :return: dict, status_code
        """
        array_capabilities = None
        target_uri = ("/%s/replication/capabilities/symmetrix"
                      % self.U4V_VERSION)
        capabilities, _ = self._get_request(
            target_uri, 'replication capabilities')
        if capabilities:
            symm_list = capabilities['symmetrixCapability']
            for symm in symm_list:
                if symm['symmetrixId'] == self.array_id:
                    array_capabilities = symm
                    break
        return array_capabilities

    def is_snapvx_licensed(self):
        """Check if the snapVx feature is licensed and enabled.

        :returns: True if licensed and enabled; False otherwise.
        """
        snap_capability = False
        capabilities = self.check_snap_capabilities()
        if capabilities:
            snap_capability = capabilities['snapVxCapable']
        else:
            LOG.error("Cannot access replication capabilities "
                      "for array %(array)s", {'array': self.array_id})
        return snap_capability

    def get_storage_group_rep(self, array, storage_group_name):
        """Given a name, return storage group details wrt replication.

        :param array: the array serial number
        :param storage_group_name: the name of the storage group
        :returns: storage group dict or None
        """
        return self.get_resource(
            array, REPLICATION, 'storagegroup',
            resource_name=storage_group_name)

    def create_storagegroup_snap(self, sg_name, snap_name, ttl=None,
                                 hours=None):
        """Create a snapVx snapshot of a storage group.

        :param sg_name: the source group name
        :param snap_name: the name of the snapshot
        :param ttl: ttl in days, if any - int
        :param hours: Boolean, if set will specify TTL value is hours not days
        """
        payload = {"snapshotName": snap_name}
        if ttl:
            payload.update({"timeToLive": ttl})
        if hours and ttl:
            payload.update({"timeInHours": "True"})
        resource_type = ('storagegroup/%(sg_name)s/snapshot'
                         % {'sg_name': sg_name})
        return self.create_resource(
            self.array_id, REPLICATION, resource_type, payload)

    def modify_storagegroup_snap(
            self, source_sg_id, target_sg_id, snap_name, link=False,
            unlink=False, restore=False, new_name=None, gen_num=0,
            async=False):
        """Modify a storage group snapshot.

        Please note that only one parameter can be modiffied at a time.
        :param source_sg_id: the source sg id
        :param target_sg_id: the target sg id (Can be None)
        :param snap_name: the snapshot name
        :param link: Flag to indicate action = Link
        :param unlink: Flag to indicate action = Unlink
        :param restore: Flag to indicate action = Restore
        :param new_name: the new name for the snapshot
        :param gen_num: the generation number
        :param async: flag to indicate if call should be async
        """
        payload = {}
        if link:
            payload = {"link": {"linkStorageGroupName": target_sg_id,
                                "copy": "true"},
                       "action": "Link"}
        elif unlink:
            payload = {"unlink": {"unlinkStorageGroupName": target_sg_id},
                       "action": "Unlink"}

        elif restore:
            payload = {"action": "Restore"}

        elif new_name:
            payload = ({"rename": {"newSnapshotName": new_name},
                        "action": "Rename"})

        if async:
            payload.update({"executionOption": ASYNCHRONOUS})

        resource_name = ('%(sg_name)s/snapshot/%(snap_id)s/generation/'
                         '%(gen_num)d'
                         % {'sg_name': source_sg_id, 'snap_id': snap_name,
                            'gen_num': gen_num})

        return self.modify_resource(
            self.array_id, REPLICATION, 'storagegroup', payload,
            resource_name=resource_name)

    def get_snap_sg(self, sg_id):
        """Get snapshot information on a particular sg.

        :param sg_id: the name of the storage group
        :return: dict, status_code
        """
        return self.get_resource(self.array_id, REPLICATION, 'storagegroup',
                                 resource_name=sg_id)

    def get_snap_sg_generation(self, sg_id, snap_name):
        """Gets a snapshot and its generation count information for an sg.

        The most recent snapshot will have a gen number of 0.
        The oldest snapshot will have a gen number = genCount - 1
        (i.e. if there are 4 generations of particular snapshot,
        the oldest will have a gen num of 3)
        :param sg_id: the name of the storage group
        :param snap_name: the name of the snapshot
        :return: dict, status_code
        """
        res_name = "%s/snapshot/%s" % (sg_id, snap_name)
        return self.get_resource(self.array_id, REPLICATION, 'storagegroup',
                                 resource_name=res_name)

    def create_new_gen_snap(self, sg_id, snap_name):
        """Establish a new generation of a SnapVX snapshot for a source SG

        :param sg_id: the name of the storage group
        :param snap_name: the name of the existing snapshot
        :return: dict, status_code
        """
        resource_type = ("storagegroup/%s/snapshot/%s/generation"
                         % (sg_id, snap_name))
        payload = ({})
        return self.create_resource(
            self.array_id, REPLICATION, resource_type, payload)

    def restore_snapshot(self, sg_id, snap_name, gen_num=0):
        """Restore a storage group to its snapshot

        :param sg_id: the name of the storage group
        :param snap_name: the name of the snapshot
        :param gen_num: the generation number of the snapshot (int)
        :return: dict, status_code
        """
        return self.modify_storagegroup_snap(
            self.array_id, sg_id, None, snap_name,
            restore=True, gen_num=gen_num)

    def rename_gen_snapshot(self, sg_id, snap_name, gen_num, new_name):
        """Rename an existing storage group snapshot

        :param sg_id: the name of the storage group
        :param snap_name: the name of the snapshot
        :param gen_num: the generation number of the snapshot (int)
        :param new_name: the new name of the snapshot
        :return: dict, status_code
        """
        return self.modify_storagegroup_snap(
            self.array_id, sg_id, None, snap_name,
            new_name=new_name, gen_num=gen_num)

    def link_gen_snapshot(self, sg_id, snap_name, gen_num, link_sg_name,
                          async=False):
        """Link a snapshot to another storage group.

        Target storage group will be created if it does not exist.
        :param sg_id: Source storage group name
        :param snap_name: name of the snapshot
        :param gen_num: generation number of a snapshot (int)
        :param link_sg_name:  the target storage group name
        :param async: flag to indicate if call is async
        :return: dict, status_code
        """
        return self.modify_storagegroup_snap(sg_id, link_sg_name, snap_name,
                                             link=True, gen_num=gen_num,
                                             async=async)

    def set_snapshot_id(self, sgname):
        """Parse a list of snaps for storage group and select from menu.

        :return:String returned with the name of the selected snapshot
        """
        snaplist = self.get_snap_sg(sgname)
        print(snaplist)
        i = 0
        for elem in snaplist[0]["snapVXSnapshots"]:
            print(i, " ", elem, "\n")
            i = int(i + 1)
        snapselection = input("Choose the snapshot you want from the "
                              "below list \n")
        snapshot_id = (snaplist[0]["snapVXSnapshots"][int(snapselection)])
        return snapshot_id

    def delete_sg_snapshot(self, sg_id, snap_name, gen_num=0):
        """Delete the snapshot of a storagegroup.

        :param sg_id: the storage group name
        :param snap_name: the name of the snapshot
        :param gen_num: the generation number
        """
        resource_name = ('%(sg_name)s/snapshot/%(snap_id)s/generation/'
                         '%(gen_num)d'
                         % {'sg_name': sg_id, 'snap_id': snap_name,
                            'gen_num': gen_num})
        return self.delete_resource(
            self.array_id, REPLICATION, 'storagegroup', resource_name)

    def is_vol_in_rep_session(self, device_id):
        """Check if a volume is in a replication session.

        :param device_id: the device id
        :returns: snapvx_tgt -- bool, snapvx_src -- bool,
                 rdf_grp -- list or None
        """
        snapvx_src = False
        snapvx_tgt = False
        rdf_grp = None
        volume_details = self.get_volume(device_id)
        if volume_details:
            LOG.debug("Vol details: %(vol)s", {'vol': volume_details})
            if volume_details.get('snapvx_target'):
                snapvx_tgt = volume_details['snapvx_target']
            if volume_details.get('snapvx_source'):
                snapvx_src = volume_details['snapvx_source']
            if volume_details.get('rdfGroupId'):
                rdf_grp = volume_details['rdfGroupId']
        return snapvx_tgt, snapvx_src, rdf_grp

    def get_srdf_num(self, sg_id):
        """Get the SRDF number for a storage group.

        :param sg_id: Storage Group Name of replicated group
        :return:JSON dictionary Message and Status
        {
          "storageGroupName": "REST_TEST_SG",
          "symmetrixId": "0001970xxxxx",
          "rdfgs": [4]
        }
        """
        res_name = "%s/rdf_group" % sg_id
        return self.get_resource(self.array_id, REPLICATION, 'storagegroup',
                                 res_name)

    def get_rdf_group(self, array, rdf_number):
        """Get specific rdf group details.

        :param array: the array serial number
        :param rdf_number: the rdf number
        """
        return self.get_resource(array, REPLICATION, 'rdf_group',
                                 rdf_number)

    def get_rdf_group_list(self, array):
        """Get rdf group list from array.

        :param array: the array serial number
        """
        return self.get_resource(array, REPLICATION, 'rdf_group')

    def get_rdf_group_volume(self, array, rdf_number, device_id):
        """Get specific volume details, from an RDF group.

        :param array: the array serial number
        :param rdf_number: the rdf group number
        :param device_id: the device id
        """
        resource_name = "%(rdf)s/volume/%(dev)s" % {
            'rdf': rdf_number, 'dev': device_id}
        return self.get_resource(array, REPLICATION, 'rdf_group',
                                 resource_name)

    def are_vols_rdf_paired(self, array, remote_array, device_id,
                            target_device, rdf_group):
        """Check if a pair of volumes are RDF paired.

        :param array: the array serial number
        :param remote_array: the remote array serial number
        :param device_id: the device id
        :param target_device: the target device id
        :param rdf_group: the rdf group
        :returns: paired -- bool, state -- string
        """
        paired, local_vol_state, rdf_pair_state = False, '', ''
        volume, _ = self.get_rdf_group_volume(array, rdf_group, device_id)
        if volume:
            remote_volume = volume['remoteVolumeName']
            remote_symm = volume['remoteSymmetrixId']
            if (remote_volume == target_device
                    and remote_array == remote_symm):
                paired = True
                local_vol_state = volume['localVolumeState']
                rdf_pair_state = volume['rdfpairState']
        else:
            LOG.warning("Cannot locate source RDF volume %s", device_id)
        return paired, local_vol_state, rdf_pair_state

    def get_rdf_group_number(self, array, rdf_group_label):
        """Given an rdf_group_label, return the associated group number.

        :param array: the array serial number
        :param rdf_group_label: the group label
        :returns: rdf_group_number
        """
        number = None
        rdf_list, _ = self.get_rdf_group_list(array)
        if rdf_list and rdf_list.get('rdfGroupID'):
            number = [rdf['rdfgNumber'] for rdf in rdf_list['rdfGroupID']
                      if rdf['label'] == rdf_group_label][0]
        if number:
            rdf_group = self.get_rdf_group(array, number)
            if not rdf_group:
                number = None
        return number

    def srdf_protect_sg(self, sg_id, remote_sid, srdfmode, establish=None,
                        async=False, rdfg_number=None):
        """SRDF protect a storage group.

        :param sg_id: Unique string up to 32 Characters
        :param remote_sid: Type Integer 12 digit VMAX ID e.g. 000197000008
        :param srdfmode: String, values can be Active, AdaptiveCopyDisk,
                         Synchronous, Asynchronous
        :param establish: default is none. Bool
        :param async: Flag to indicate if call should be async
                      (NOT to be confused with the SRDF mode)
        :param rdfg_number: the required RDFG number (optional)
        :return: message and status Type JSON
        """
        res_type = "storagegroup/%s/rdf_group" % sg_id
        establish_sg = "True" if establish else "False"
        rdf_payload = {"replicationMode": srdfmode,
                       "remoteSymmId": remote_sid,
                       "remoteStorageGroupName": sg_id}
        if rdfg_number is not None:
            rdf_payload['rdfgNumber'] = rdfg_number
        if establish is not None:
            rdf_payload["establish"] = establish_sg
        if async:
            rdf_payload.update({'executionOption': ASYNCHRONOUS})
        return self.create_resource(
            self.array_id, REPLICATION, res_type, rdf_payload)

    def get_srdf_state(self, sg_id, rdfg=None):
        """Get the current SRDF state.

        :param sg_id: name of storage group
        :param rdfg: rdf number, optional
        :return: dict, status_code
        """
        if not rdfg:
            # Get a list of SRDF groups for storage group
            rdfg_list = self.get_srdf_num(sg_id)[0]["rdfgs"]
            rdfg = rdfg_list[0]
        res_name = "%s/rdf_group/%s" % (sg_id, rdfg)
        return self.get_resource(
            self.array_id, REPLICATION, 'storagegroup', res_name)

    def change_srdf_state(self, sg_id, action, rdfg=None,
                          options=None, async=False):
        """Modify the state of an srdf.

        This may be a long running task depending on the size of the SRDF group,
        can switch to async call if required.
        :param sg_id: name of storage group
        :param action: the rdf action e.g. Suspend, Establish, etc
        :param rdfg: rdf number, optional
        :param options: a dict of possible options - depends on action type
        :param async: flag to indicate if call should be async
        """
        # Get a list of SRDF groups for storage group
        if not rdfg:
            rdfg_list = self.get_srdf_num(sg_id)[0]["rdfgs"]
            if len(rdfg_list) < 2:  # Check to see if RDF is cascaded.
                # Sets the RDFG for the Put call to first value in list if
                # group is not cascasded.
                rdfg = rdfg_list[0]
            else:
                LOG.exception("Group is cascaded, functionality not yet "
                              "added in this python library")
        if rdfg:
            res_name = "%s/rdf_group/%s" % (sg_id, rdfg)
            payload = {"action": action}
            if async:
                payload.update({"executionOption": "ASYNCHRONOUS"})
            if options:
                option_header = action.lower()
                payload.update({option_header: options})
            return self.modify_resource(
                self.array_id, REPLICATION, 'storagegroup',
                payload, resource_name=res_name)
        return None, 401

    def get_fe_director_list(self):
        """Get list of all FE Directors.

        :return: director list
        """
        target_uri = "/performance/FEDirector/keys"
        dir_payload = ({"symmetrixId": self.array_id})

        dir_response = self.rest_client.rest_request(
            target_uri, POST, request_object=dir_payload)
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
            port_response = self.rest_client.rest_request(
                target_uri, POST, request_object=port_payload)
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

        target_uri = '/performance/FEPort/metrics'
        port_perf_payload = ({"startDate": start_date,
                              "endDate": end_date,
                              "symmetrixId": self.array_id,
                              "directorId": dir_id,
                              "portId": port_id,
                              "dataFormat": "Average",
                              "metrics": ["PercentBusy"]})
        return self.rest_client.rest_request(
            target_uri, POST, request_object=port_perf_payload)

    def get_fe_director_metrics(self, start_date, end_date,
                                director, dataformat):
        """Function to get one or more metrics for front end directors.

        :param start_date: Date EPOCH Time in Milliseconds
        :param end_date: Date EPOCH Time in Milliseconds
        :param director:List of FE Directors
        :param dataformat:Average or Maximum
        :param dataformat:
        :return: JSON Payload, and RETURN CODE 200 for success
        """
        target_uri = "/performance/FEDirector/metrics"
        fe_director_param = ({
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
                                             request_object=fe_director_param)

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
        fe_director_param = ({"symmetrixId": self.array_id,
                              "directorId": director_id,
                              "endDate": end_date,
                              "dataFormat": dataformat,
                              "metrics": [metriclist],
                              "portId": port_id,
                              "startDate": start_date})

        return self.rest_client.rest_request(
            target_uri, POST, request_object=fe_director_param)

        ##################################
        # Collect VMAX Array level stats #
        ##################################

    def get_array_metrics(self, start_date, end_date):
        """Get array metrics.

        Get all avaliable performance statistics for specified time
        period return in JSON
        :param start_date: EPOCH Time
        :param end_date: Epoch Time
        :return: array_results_combined
        """
        target_uri = "/performance/Array/metrics"
        array_perf_payload = {
            'symmetrixId': self.array_id,
            'endDate': end_date,
            'dataFormat': 'Average',
            'metrics': [
                'OverallCompressionRatio', 'OverallEfficiencyRatio',
                'PercentVPSaved', 'VPSharedRatio', 'VPCompressionRatio',
                'VPEfficiencyRatio', 'PercentSnapshotSaved',
                'SnapshotSharedRatio', 'SnapshotCompressionRatio',
                'SnapshotEfficiencyRatio', 'CopySlotCount', 'HostIOs',
                'HostReads', 'HostWrites', 'PercentReads', 'PercentWrites',
                'PercentHit', 'HostMBs', 'HostMBReads', 'HostMBWritten',
                'HostMBWritten', 'FEReqs', 'FEReadReqs', 'FEWriteReqs',
                'BEIOs', 'BEReqs', 'BEReadReqs', 'BEWriteReqs',
                'SystemWPEvents', 'DeviceWPEvents', 'WPCount',
                'SystemMaxWPLimit', 'PercentCacheWP', 'AvgFallThruTime',
                'FEHitReqs', 'FEReadHitReqs', 'FEWriteHitReqs',
                'PrefetchedTracks', 'FEReadMissReqs', 'FEWriteMissReqs',
                'ReadResponseTime', 'WriteResponseTime',
                'OptimizedReadMisses', 'OptimizedMBReadMisses',
                'AvgOptimizedReadMissSize', 'QueueDepthUtilization',
                'InfoAlertCount', 'WarningAlertCount', 'CriticalAlertCount',
                'RDFA_WPCount', 'AllocatedCapacity', 'FE_Balance',
                'DA_Balance', 'DX_Balance', 'RDF_Balance', 'Cache_Balance',
                'SATA_Balance', 'FC_Balance', 'EFD_Balance'
            ],
            'startDate': start_date
        }
        array_perf_data = self.rest_client.rest_request(
            target_uri, POST, request_object=array_perf_payload)
        array_results_combined = dict()
        array_results_combined['symmetrixID'] = self.array_id
        array_results_combined['reporting_level'] = "array"
        array_results_combined['perf_data'] = (
            array_perf_data[0]['resultList']['result'])
        return array_results_combined

    def get_storage_group_metrics(self, sg_id, start_date, end_date):
        """Get storage group metrics.

        :param sg_id: the storage group id
        :param start_date: the start date
        :param end_date: the end date
        :return: sg_results_combined
        """
        target_uri = '/performance/StorageGroup/metrics'
        sg_perf_payload = {
            'symmetrixId': self.array_id,
            'endDate': end_date,
            'dataFormat': 'Average',
            'storageGroupId': sg_id,
            'metrics': [
                'CriticalAlertCount', 'InfoAlertCount', 'WarningAlertCount',
                'AllocatedCapacity', 'TotalTracks', 'BEDiskReadResponseTime',
                'BEReadRequestTime', 'BEReadTaskTime', 'AvgIOSize',
                'AvgReadResponseTime6', 'AvgReadResponseTime7',
                'AvgReadSize', 'AvgWritePacedDelay', 'AvgWriteResponseTime6',
                'AvgWriteResponseTime7', 'AvgWriteSize', 'BEMBReads',
                'BEMBTransferred', 'BEMBWritten', 'BEPercentReads',
                'BEPercentWrites', 'BEPrefetchedTrackss', 'BEReadReqs',
                'BEPrefetchedTrackUsed', 'BEWriteReqs', 'CompressedTracks',
                'CompressionRatio', 'BlockSize', 'HostMBs', 'IODensity',
                'HostIOs', 'MaxWPThreshold', 'HostMBReads', 'HostMBWritten',
                'AvgOptimizedReadMissSize', 'OptimizedMBReadMisss',
                'OptimizedReadMisses', 'PercentCompressedTracks',
                'PercentHit', 'PercentMisses', 'PercentRandomIO',
                'PercentRandomReads', 'PercentRandomReadHit', 'PercentRead',
                'PercentRandomReadMiss', 'PercentRandomWrites',
                'PercentRandomWriteHit', 'PercentRandomWriteMiss',
                'PercentReadMiss', 'PercentReadHit', 'PercentSeqIO',
                'PercentSeqRead', 'PercentSeqReadHit', 'PercentSeqReadMiss',
                'PercentSeqWrites', 'PercentSeqWriteHit', 'PercentWrite',
                'PercentVPSpaceSaved', 'PercentWriteHit', 'RandomIOs',
                'PercentSeqWriteMiss', 'PercentWriteMiss', 'BEPrefetchedMBs',
                'HostIOLimitPercentTimeExceeded', 'RandomReadHits',
                'RandomReadMisses', 'RandomReads', 'RandomWriteHits',
                'RandomWriteMisses', 'RandomWrites', 'RdfMBRead',
                'RdfMBWritten', 'RdfReads', 'RdfReadHits', 'RdfResponseTime',
                'RDFRewrites', 'RdfWrites', 'HostReads', 'HostReadHits',
                'HostReadMisses', 'ReadResponseTimeCount1',
                'ReadResponseTimeCount2', 'ReadResponseTimeCount3',
                'ReadResponseTimeCount4', 'ReadResponseTimeCount5',
                'ReadResponseTimeCount6', 'ReadResponseTimeCount7',
                'RDFS_WriteResponseTime', 'ReadMissResponseTime',
                'ResponseTime', 'ReadResponseTime', 'WriteMissResponseTime',
                'WriteResponseTime', 'SeqReadHits', 'SeqReadMisses',
                'SeqReads', 'SeqWriteHits', 'SeqWriteMisses', 'SeqWrites',
                'Skew', 'SRDFA_MBSent', 'SRDFA_WriteReqs', 'SRDFS_MBSent',
                'SRDFS_WriteReqs', 'BEReqs', 'HostHits', 'HostMisses',
                'SeqIOs', 'WPCount', 'HostWrites', 'HostWriteHits',
                'HostWriteMisses', 'WritePacedDelay',
                'WriteResponseTimeCount1', 'WriteResponseTimeCount2',
                'WriteResponseTimeCount3', 'WriteResponseTimeCount4',
                'WriteResponseTimeCount5', 'WriteResponseTimeCount6',
                'WriteResponseTimeCount7'
            ],
            'startDate': start_date
        }
        sg_perf_data = self.rest_client.rest_request(
            target_uri, POST, request_object=sg_perf_payload)
        sg_results_combined = dict()
        sg_results_combined['symmetrixID'] = self.array_id
        sg_results_combined['reporting_level'] = "StorageGroup"
        sg_results_combined['sgname'] = sg_id
        sg_results_combined['perf_data'] = (
            sg_perf_data[0]['resultList']['result'])
        return sg_results_combined

    def get_all_fe_director_metrics(self, start_date, end_date):
        """

        Get a list of all Directors.
        Calculate start and End Dates for Gathering Performance Stats
        Last 1 Hour.
        :param start_date: start date
        :param end_date: end date
        :return:
        """
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
        """Get director performance information.

        Get Director level information and performance metrics for
        specified time frame, hard coded to average numbers.
        :param director_id: Director ID
        :param start_date: start date
        :param end_date: end date
        :return: Combined payload of all Director level information
                 & performance metrics
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
                'AvgTimePerSyscall', 'CompressedMBs', 'CompressedReadMBs',
                'CompressedWriteMBs', 'CompressedReadReqs', 'CompressedReqs',
                'CompressedWriteReqs', 'IOs', 'MBs', 'MBRead', 'MBWritten',
                'PercentBusy', 'PercentBusyLogicalCore_0',
                'PercentBusyLogicalCore_1', 'PercentNonIOBusyLogicalCore_1',
                'PercentNonIOBusyLogicalCore_0', 'PercentNonIOBusy',
                'PrefetchedTracks', 'ReadReqs', 'Reqs', 'SyscallCount',
                'Syscall_RDF_DirCount', 'SyscallRemoteDirCount', 'WriteReqs'
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
                'AvgRDFSWriteResponseTime', 'AvgReadMissResponseTime',
                'AvgWPDiscTime', 'AvgTimePerSyscall', 'DeviceWPEvents',
                'HostMBs', 'HitReqs', 'HostIOs', 'MissReqs',
                'AvgOptimizedReadMissSize', 'OptimizedMBReadMisses',
                'OptimizedReadMisses', 'WriteMissReqs', 'PercentHitReqs',
                'PercentReadReqs', 'PercentReadReqHit', 'PercentWriteReqs',
                'PercentWriteReqHit', 'QueueDepthUtilization', 'ReadMissReqs',
                'HostIOLimitMBs', 'ReadReqs', 'ReadHitReqs', 'Reqs',
                'ReadResponseTime', 'HostIOLimitIOs', 'WriteResponseTime',
                'SlotCollisions', 'SyscallCount', 'Syscall_RDF_DirCounts',
                'SyscallRemoteDirCounts', 'SystemWPEvents', 'TotalReadCount',
                'TotalWriteCount', 'WriteReqs', 'WriteHitReqs', 'PercentBusy',
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
                'AvgIOServiceTime', 'AvgIOSizeReceived', 'AvgIOSizeSent',
                'AvgTimePerSyscall', 'CopyIOs', 'CopyMBs', 'IOs', 'Reqs',
                'MBSentAndReceived', 'MBRead', 'MBWritten', 'PercentBusy',
                'Rewrites', 'AsyncMBSent', 'AsyncWriteReqs', 'SyncMBSent',
                'SyncWrites', 'SyscallCount', 'Syscall_RDF_DirCounts',
                'SyscallRemoteDirCount', 'SyscallTime', 'WriteReqs',
                'TracksSentPerSec', 'TracksReceivedPerSec'
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
                'PercentBusy', 'RandomReadMissMBs', 'RandomReadMisses',
                'RandomWriteMissMBs', 'RandomWriteMisses'
            ],
            'startDate': self.start_date
        }

        # Perform Director level performance REST call dependent on Director type
        if 'DF' in director_id or 'DX' in director_id:
            perf_metrics_payload = self.rest_client.rest_request(
                be_director_uri, POST, request_object=be_director_payload)
            director_type = 'BE'
        elif ('EF' in director_id or 'FA' in director_id
              or 'FE' in director_id or 'SE' in director_id):
            perf_metrics_payload = self.rest_client.rest_request(
                fe_director_uri, POST, request_object=fe_director_payload)
            director_type = 'FE'
        elif 'RF' in director_id or 'RE' in director_id:
            perf_metrics_payload = self.rest_client.rest_request(
                rdf_director_uri, POST, request_object=rdf_director_payload)
            director_type = 'RDF'
        elif 'IM' in director_id:
            perf_metrics_payload = self.rest_client.rest_request(
                im_director_uri, POST, request_object=im_director_payload)
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
        combined_payload['director_id'] = director_id
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
            combined_payload['perf_msg'] = ("No active Director "
                                            "performance data available")

        else:
            # Performance metrics returned...
            combined_payload['perf_data'] = (perf_metrics_payload
                                             [0]['resultList']['result'])

        return combined_payload

    def get_port_group_metrics(self, pg_id, start_date, end_date):
        """Get Port Group Performance Metrics.

        :param pg_id:
        :param start_date:
        :param end_date:
        :return:
        """
        target_uri = '/performance/PortGroup/metrics'
        pg_perf_payload = {
            'symmetrixId': self.array_id,
            'endDate': end_date,
            'dataFormat': 'Average',
            'portGroupId': pg_id,
            'metrics': [
                'Reads', 'Writes', 'IOs', 'MBRead', 'MBWritten', 'MBs',
                'AvgIOSize', 'PercentBusy'],
            'startDate': start_date
        }
        pg_perf_data = self.rest_client.rest_request(
            target_uri, POST, request_object=pg_perf_payload)
        pg_results_combined = dict()
        pg_results_combined['symmetrixID'] = self.array_id
        pg_results_combined['reporting_level'] = "PortGroup"
        pg_results_combined['pgname'] = pg_id
        pg_results_combined['perf_data'] = (
            pg_perf_data[0]['resultList']['result'])
        return pg_results_combined

    def get_host_metrics(self, host, start_date, end_date):
        """Get host metrics.

        Get all avaliable host performance statiscics for specified
        time period return in JSON.
        :param host: the host name
        :param start_date: EPOCH Time
        :param end_date: Epoch Time
        :return: Formatted results
        """
        target_uri = "/performance/Host/metrics"
        host_perf_payload = {
            'symmetrixId': self.array_id,
            'endDate': end_date,
            'hostId': host,
            'dataFormat': 'Average',
            'metrics': ['HostIOs', 'HostMBReads', 'HostMBWrites', 'Reads',
                        'ResponseTime', 'ReadResponseTime', 'Writes',
                        'WriteResponseTime', 'SyscallCount', 'MBs'],
            'startDate': start_date
        }
        host_perf_data = self.rest_client.rest_request(
            target_uri, POST, request_object=host_perf_payload)
        host_results = dict()
        host_results['symmetrixID'] = self.array_id
        host_results['reporting_level'] = "Host"
        host_results['HostID'] = host
        host_results['perf_data'] = host_perf_data[0]['resultList']['result']
        return host_results

    def get_perf_threshold_categories(self):
        """Get performance threshold categories.

        Written for Unisphere 84, if you are on ealier, append /83 to the
        endpoint.
        :return: category_list
        """
        target_uri = "/performance/threshold/categories"
        categories = self.rest_client.rest_request(target_uri, GET)
        category_list = categories[0]["endpoint"]
        return category_list

    def get_perf_category_threshold_settings(self, category):
        """Get performance threshold category settings.

        Will accept valid category (categories listed from
        get_threshold_categories).
        Written for Unisphere 84, if earlier version append
        /83/ to start of uri
        :param category:
        :return: dict, sc
        """
        target_uri = "/performance/threshold/list/%s" % category
        return self.rest_client.rest_request(target_uri, GET)


    def set_perf_threshold_and_alert(self, category, metric, firstthreshold,
                                 secondthreshold, notify):
        """
        Function to set performance alerts, suggested use with CSV file to
        get parameter settings from user template.
        Default is to check for 3 out of 5 samples before returning alert,
        users may want to modify as potentially 3 of 5 could mean could
        take 25 minutes for an alert to be seen as samples are at 5 minute
        intervals.
        :param category:
        :param metric:
        :param firstthreshold:
        :param secondthreshold:
        :param notify: Notify user with Alert Boolean
        :return:
        """
        payload=({"secondThresholdSamples": 5,"firstThreshold": firstthreshold,
              "firstThresholdSamples": 5,"metric": metric, "alert": notify,
              "firstThresholdOccurrrences": 3,
              "firstThresholdSeverity": "WARNING",
              "secondThresholdSeverity": "CRITICAL",
              "secondThreshold": secondthreshold,
              "secondThresholdOccurrrences": 3

              })
        target_uri = "/performance/threshold/update/%s" % category

        return self.rest_client.rest_request(target_uri,PUT,
                                             request_object=payload)

    def generate_threshold_settings_csv(self,outputcsvname):
        """
        Creates a CSV file with the following headers format containing current
        alert configuration for the given unisphere instance
        category,metric,firstthreshold,secondthreshold,notify,kpi
        array,HostReads,100000,300000,true,true
        array,HostWrites,100000,300000,true,false
        :param outputcsvname: filename for CSV to be generated
        :return:
        """
        category_list = self.get_perf_threshold_categories()
        with open(bytes(outputcsvname, 'UTF-8'), 'w',newline='') as csvfile:
            eventwriter = csv.writer(csvfile,
                                     delimiter=',',
                                     quotechar='|',
                                     quoting=csv.QUOTE_MINIMAL)

            eventwriter.writerow(["category","metric","firstthreshold",
                                  "secondthreshold","notify", "kpi"])
            for category in category_list:
                metric_setting = \
                self.get_perf_category_threshold_settings(category)[0][
                    'performanceThreshold']
                for metric in metric_setting:
                        eventwriter.writerow([category, metric.get('metric'),
                          metric.get('firstThreshold'), metric.get(
                                'secondThreshold'),metric.get('alertError'),
                                              metric.get('kpi')])


    def set_perfthresholds_csv(self,csvfilename):
        """
        reads CSV file, and sets perforamnce threshold metrics, should be
        used with generate_threshold_settings_csv to produce CSV file that
        can be edited and uploaded.

        :param csvfilename:
        :return:
        Reads a CSV file with the following headers format
        category,metric,firstthreshold,secondthreshold,notify,kpi
        array,HostReads,100000,300000,true,true
        array,HostWrites,100000,300000,true,false
        cur
        """
        data = self.read_csv_values(csvfilename)
        firstthreshold_list = data.get("firstthreshold")
        secondthreshold_list = data.get("secondthreshold")
        notify_list = data.get("notify")
        categrory_list = data.get("category")
        metric_list = data.get("metric")
        kpimetric_list = data.get("kpi")

        for c, m, f, s, n, k in zip(categrory_list, metric_list,
                                 firstthreshold_list,
                                 secondthreshold_list, notify_list,
                                    kpimetric_list):
            #if k :
            #unhash line above if you only want to update KPI values,
            # doing this will reduce runtime of set_perfthresholds_csv
            #you can restrict futher by filtering on category values e.g.
            # if c ="Array" or "RDFS": to restrict to update certain array
            # categories
            self.set_perf_threshold_and_alert(c, m, f, s, n)

