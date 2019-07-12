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
"""common.py."""

import csv
import logging
import time

from PyU4V.utils import constants
from PyU4V.utils import exception

import six

LOG = logging.getLogger(__name__)

# HTTP constants
GET = constants.GET
POST = constants.POST
PUT = constants.PUT
DELETE = constants.DELETE

# U4V constants
STATUS_200 = constants.STATUS_200
STATUS_201 = constants.STATUS_201
STATUS_202 = constants.STATUS_202
STATUS_204 = constants.STATUS_204
STATUS_401 = constants.STATUS_401
STATUS_404 = constants.STATUS_404
# Job constants
INCOMPLETE_LIST = constants.INCOMPLETE_LIST
CREATED = constants.CREATED
SUCCEEDED = constants.SUCCEEDED


class CommonFunctions(object):
    """CommonFunctions."""

    def __init__(self, request, interval, retries, u4v_version):
        """__init__."""
        self.request = request
        self.interval = interval
        self.retries = retries
        self.U4V_VERSION = u4v_version

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

    def get_job_by_id(self, job_id):
        """Get details of a specific job.

        :param job_id: the job id
        """
        job_url = "/%s/system/job/%s" % (self.U4V_VERSION, job_id)
        return self.get_request(job_url, 'job')

    def _is_job_finished(self, job_id):
        """Check if the job is finished.

        :param job_id: the id of the job
        :returns: complete -- bool, result -- string,
                  rc -- int, status -- string, task -- list of dicts
        """
        complete, rc, status, result, task = False, 0, None, None, None
        job = self.get_job_by_id(job_id)
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
                "Error %(operation)s. The status code "
                "received is %(sc)s and the message is "
                "%(message)s." %
                ({'operation': operation,
                  'sc': status_code,
                  'message': message}))
            if status_code == STATUS_404:
                raise exception.ResourceNotFoundException(
                    data=exception_message)
            if status_code == STATUS_401:
                raise exception.UnauthorizedRequestException()
            else:
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
                    "Error %(operation)s. Status code: %(sc)s. "
                    "Error: %(error)s. Status: %(status)s." %
                    ({'operation': operation,
                      'sc': rc,
                      'error': six.text_type(result),
                      'status': status}))
                raise exception.VolumeBackendAPIException(
                    data=exception_message)
        return task

    def _build_uri(self, *args, **kwargs):
        """Build the target URI.

        :param args: optional arguments passed in to form URI
        :param kwargs: optional key word arguments passed in to form URI
        :returns: target URI -- string
        """
        target_uri = ''
        version = None

        # Version control logic
        if kwargs.get('version') and not kwargs.get('no_version'):
            version = kwargs['version']
        elif kwargs.get('version') and kwargs.get('no_version'):
            version = kwargs['version']
        elif not kwargs.get('version') and not kwargs.get('no_version'):
            LOG.debug("Version has been specified along with no_version "
                      "flag, ignoring no_version flag and using version "
                      "%(version)s.",
                      {'version': version})
            version = self.U4V_VERSION
        elif kwargs['no_version'] and not kwargs.get('version'):
            pass

        # Old method - has arguments passed which define URI
        if args:
            if version:
                target_uri += "/%(version)s" % {'version': version}

            array_id = args[0]
            category = args[1]
            resource_type = args[2]
            resource_name = kwargs.get('resource_name')

            target_uri += "/%(cat)s/symmetrix/%(array_id)s/%(res_type)s" % (
                {'cat': category,
                 'array_id': array_id,
                 'res_type': resource_type})

            if resource_name:
                target_uri += "/%(resource_name)s" % (
                    {'resource_name': kwargs.get('resource_name')})

        # New method - new method is to have only keyword arguments passed
        if not args and kwargs:
            if kwargs.get('category') in ['performance', 'common']:
                version = None
            if version:
                target_uri += "/%s" % version

            target_uri += "/%(category)s/%(resource_level)s" % (
                {'category': kwargs.get('category'),
                 'resource_level': kwargs.get('resource_level')})

            if kwargs.get('resource_level_id'):
                target_uri += "/%s" % kwargs.get('resource_level_id')

            if kwargs.get('resource_type'):
                target_uri += "/%s" % kwargs.get('resource_type')
                if kwargs.get('resource_type_id'):
                    target_uri += "/%s" % kwargs.get('resource_type_id')

            if kwargs.get('resource'):
                target_uri += "/%s" % kwargs.get('resource')
                if kwargs.get('resource_id'):
                    target_uri += "/%s" % kwargs.get('resource_id')

            if kwargs.get('object_type'):
                target_uri += "/%s" % kwargs.get('object_type')
                if kwargs.get('object_type_id'):
                    target_uri += "/%s" % kwargs.get('object_type_id')

        return target_uri

    def get_request(self, target_uri, resource_type, params=None):
        """Send a GET request to the array.

        :param target_uri: the target uri
        :param resource_type: the resource type, e.g. maskingview
        :param params: optional dict of filter params
        :returns: resource_object -- dict or None
        :raises: ResourceNotFoundException
        """
        message, sc = self.request(target_uri, GET, params=params)
        operation = "get %s" % resource_type
        self.check_status_code_success(operation, sc, message)
        return message

    def get_resource(self, *args, **kwargs):
        """Get resource details from the array.

        The args passed in are
        positional and should be passed in using the order they are listed in
        below.

        Traditional Method:
        :param args:
            param0 array_id: the array serial number
            param1 category: the resource category e.g. sloprovisioning
            param2 resource_type: the resource type e.g. maskingview
        :param kwargs:
            param version: optional version of Unisphere
            param resource_name: optional name of a specific resource
            param params: optional dict of filter params

        New Method:
        :param kwargs:
            param version: the version of Unisphere
            param no_version: (boolean) if the URI required no version
            param category: the resource category e.g. sloprovisioning, system
            param resource_level: the resource level e.g. storagegroup, alert
            param resource_level_id: the resource level ID
            param resource_type: the name of a specific resource
            param resource_type_id: the name of a specific resource
            param resource: the name of a specific resource
            param resource_id: the name of a specific resource
            param object_type: the name of a specific resource
            param object_type_id: the name of a specific resource
            param params: query parameters

        :returns: resource object -- dict
        """
        target_uri = self._build_uri(*args, **kwargs)

        if args:
            resource_type = args[2]
        elif not args and kwargs:
            resource_type = kwargs.get('resource_level')
        else:
            resource_type = None

        return self.get_request(
            target_uri, resource_type, kwargs.get('params'))

    def create_resource(self, *args, **kwargs):
        """Create a resource.

        The args passed in are positional and should be
        passed in using the order they are listed in below.

        Traditional Method:
        :param args:
            param0 array_id: the array serial number
            param1 category: the resource category e.g. sloprovisioning
            param2 resource_type: the resource type e.g. maskingview
        :param kwargs:
            param version: optional version of Unisphere
            param resource_name: optional name of a specific resource
            param payload: optional payload dict

        New Method:
        :param kwargs:
            param version: the version of Unisphere
            param no_version: (boolean) if the URI required no version
            param category: the resource category e.g. sloprovisioning, system
            param resource_level: the resource level e.g. storagegroup, alert
            param resource_level_id: the resource level ID
            param resource_type: the name of a specific resource
            param resource_type_id: the name of a specific resource
            param resource: the name of a specific resource
            param resource_id: the name of a specific resource
            param object_type: the name of a specific resource
            param object_type_id: the name of a specific resource
            param payload: optional payload dict

        :returns: message -- string, server response
        """
        target_uri = self._build_uri(*args, **kwargs)

        message, status_code = self.request(
            target_uri, POST, request_object=kwargs.get('payload'))

        if args:
            resource_type = args[2]
        elif not args and kwargs:
            resource_type = kwargs.get('resource_level')
        else:
            resource_type = None

        operation = "Create %s resource" % resource_type

        self.check_status_code_success(
            operation, status_code, message)
        return message

    def modify_resource(self, *args, **kwargs):
        """Modify a resource.

        The args passed in are positional and should be
        passed in using the order they are listed in below.

        Traditional Method:
        :param args:
            param0 array_id: the array serial number
            param1 category: the resource category e.g. sloprovisioning
            param2 resource_type: the resource type e.g. maskingview
        :param kwargs:
            param version: optional version of Unisphere
            param resource_name: optional name of a specific resource
            param payload: optional payload dict

        New Method:
        :param kwargs:
            param version: the version of Unisphere
            param no_version: (boolean) if the URI required no version
            param category: the resource category e.g. sloprovisioning, system
            param resource_level: the resource level e.g. storagegroup, alert
            param resource_level_id: the resource level ID
            param resource_type: the name of a specific resource
            param resource_type_id: the name of a specific resource
            param resource: the name of a specific resource
            param resource_id: the name of a specific resource
            param object_type: the name of a specific resource
            param object_type_id: the name of a specific resource
            param payload: optional payload dict

        :returns: message -- string (server response)
        """
        target_uri = self._build_uri(*args, **kwargs)

        message, status_code = self.request(
            target_uri, PUT, request_object=kwargs.get('payload'))

        if args:
            resource_type = args[2]
        elif not args and kwargs:
            resource_type = kwargs.get('resource_level')
        else:
            resource_type = None

        operation = "Modify %s resource" % resource_type

        self.check_status_code_success(operation, status_code, message)
        return message

    def delete_resource(self, *args, **kwargs):
        """Delete a resource.

        The args passed in are positional and should be
        passed in using the order they are listed in below.

        Traditional Method:
        :param args:
            param0 array_id: the array serial number
            param1 category: the resource category e.g. sloprovisioning
            param2 resource_type: the resource type e.g. maskingview
        :param kwargs:
            param version: optional version of Unisphere
            param resource_name: optional name of a specific resource
            param payload: optional payload dict

        New Method:
        :param kwargs:
            param version: the version of Unisphere
            param no_version: (boolean) if the URI required no version
            param category: the resource category e.g. sloprovisioning, system
            param resource_level: the resource level e.g. storagegroup, alert
            param resource_level_id: the resource level ID
            param resource_type: the name of a specific resource
            param resource_type_id: the name of a specific resource
            param resource: the name of a specific resource
            param resource_id: the name of a specific resource
            param object_type: the name of a specific resource
            param object_type_id: the name of a specific resource
            param payload: optional payload dict
        """
        target_uri = self._build_uri(*args, **kwargs)

        message, status_code = self.request(
            target_uri, DELETE, request_object=kwargs.get('payload'),
            params=kwargs.get('payload'))

        if args:
            resource_type = args[2]
        elif not args and kwargs:
            resource_type = kwargs.get('resource_level')
        else:
            resource_type = None

        operation = "Delete %s resource" % resource_type

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
        """Read any csv file with headers.

        You can extract the multiple lists from the headers in the CSV file.
        In your own script, call this function and assign to data variable,
        then extract the lists to the variables. Example:
        data=ru.read_csv_values(mycsv.csv)
        sgnamelist = data['sgname']
        policylist = data['policy']

        :param file_name: path to CSV file
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

    def get_uni_version(self):
        """Get the unisphere version from the server.

        :return: version and major_version(e.g. ("V8.4.0.16", "84"))
        """
        version, major_version = None, None
        target_uri = "/%s/system/version" % self.U4V_VERSION
        response = self.get_request(target_uri, 'version')
        if response and response.get('version'):
            version = response['version']
            version_list = version.split('.')
            major_version = version_list[0][1] + version_list[1]
        return version, major_version

    def get_array_list(self, filters=None):
        """Return a list of arrays.

        :param filters: optional dict of filters
        :return: dict
        """
        print(self.U4V_VERSION)
        target_uri = "/%s/system/symmetrix" % self.U4V_VERSION
        response = self.get_request(target_uri, 'symmetrix', params=filters)
        if response and response.get('symmetrixId'):
            return response['symmetrixId']
        return []

    def get_v3_or_newer_array_list(self, filters=None):
        """Return a list of V3 or newer arrays in the environment.

        :param filters: optional dict of filters
        :return: list of array ids
        """
        target_uri = "/%s/sloprovisioning/symmetrix" % self.U4V_VERSION
        response = self.get_request(target_uri, 'symmetrix', params=filters)
        if response and response.get('symmetrixId'):
            return response['symmetrixId']
        return []

    def get_array(self, array_id):
        """Return details on specific array.

        :return: server response
        """
        target_uri = "/%s/system/symmetrix/%s" % (
            self.U4V_VERSION, array_id)
        return self.get_request(target_uri, 'symmetrix')

    def get_iterator_page_list(self, iterator_id, start, end):
        """Get a page of results from an iterator instance.

        :param iterator_id: the id of the iterator
        :param start: the start number
        :param end: the end number
        :return: list of results
        """
        page_list = []
        target_uri = "/common/Iterator/%s/page" % iterator_id
        filters = {'from': start, 'to': end}
        response = self.get_request(target_uri, 'iterator', params=filters)
        if response and response.get('result'):
            page_list = response['result']
        return page_list

    def get_wlp_information(self, array_id):
        """Get the latest timestamp from WLP for processing New Workloads.

        Ezample return:
        {"processingDetails": {
        "lastProcessedSpaTimestamp": 1517408700000,
        "nextUpdate": 1038},
        "spaRegistered": True}

        :return: dict
        """
        wlp_details = None
        target_uri = ("/%s/wlp/symmetrix/%s" % (
            self.U4V_VERSION, array_id))
        response = self.get_request(target_uri, 'wlp')
        if response and response.get('symmetrixDetails'):
            wlp_details = response['symmetrixDetails']
        return wlp_details

    def get_headroom(self, array_id, workload, srp="SRP_1", slo="Diamond"):
        """Get the Remaining Headroom Capacity.

        Get the headroom capacity for a given srp/ slo/ workload combination.
        Example output:
        [{'workloadType': 'OLTP',
        'headroomCapacity': 29076.34, 'processingDetails':
        {'lastProcessedSpaTimestamp': 1485302100000,
        'nextUpdate': 1670}, 'sloName': 'Diamond',
        'srp': 'SRP_1', 'emulation': 'FBA'}]})

        :param array_id: the array serial number
        :param workload: the workload type (DSS, OLTP, DSS_REP, OLTP_REP)
        :param srp: the storage resource pool. Default SRP_1.
        :param slo: the service level. Default Diamond.
        :return: dict
        """
        headroom = []
        params = {'srp': srp, 'slo': slo, 'workloadtype': workload}
        response = self.get_resource(array_id, 'wlp', 'headroom',
                                     params=params)
        if response and response.get('headroom'):
            headroom = response['headroom']
        return headroom
