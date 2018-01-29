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

from PyU4V.utils import config_handler
from PyU4V.utils import constants
from PyU4V.utils import exception

logger = logging.getLogger(__name__)
LOG, CFG = config_handler.set_logger_and_config(logger)

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
    def __init__(self, request, interval, retries, u4v_version):
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
        job_url = "/{}/system/job/{}".format(self.U4V_VERSION, job_id)
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
                    'Error {operation}. The status code received '
                    'is {sc} and the message is {message}.'.format(
                        operation=operation, sc=status_code, message=message))
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
                    "Error {operation}. Status code: {sc}. "
                    "Error: {error}. Status: {status}.".format(
                        operation=operation, sc=rc,
                        error=six.text_type(result),
                        status=status))
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
        target_uri = ('/{category}/symmetrix/'
                      '{array}/{resource_type}'.format(
                       version=version, category=category, array=array,
                       resource_type=resource_type))
        if resource_name:
            target_uri += '/{resource_name}'.format(
                resource_name=resource_name)
        if version:
            target_uri = ('/{version}{target}'.format(
                version=version, target=target_uri))
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
        operation = 'get {}'.format(resource_type)
        self.check_status_code_success(operation, sc, message)
        return message

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
        return self.get_request(target_uri, resource_type, params)

    def create_resource(self, array, category, resource_type, payload,
                        version=None):
        """Create a resource.

        :param array: the array serial number
        :param category: the category
        :param resource_type: the resource type
        :param payload: the payload
        :param version: the U4V version
        :returns: message -- string, server response
        """
        target_uri = self._build_uri(array, category, resource_type,
                                     version)
        message, status_code = self.request(target_uri, POST,
                                            request_object=payload)
        operation = 'Create {} resource'.format(resource_type)
        self.check_status_code_success(
            operation, status_code, message)
        return message

    def modify_resource(self, array, category, resource_type, payload,
                        version=None, resource_name=None):
        """Modify a resource.

        :param array: the array serial number
        :param category: the category
        :param resource_type: the resource type
        :param payload: the payload
        :param version: the uv4 version
        :param resource_name: the resource name
        :returns: message -- string (server response)
        """
        if version is None:
            version = self.U4V_VERSION
        target_uri = self._build_uri(array, category, resource_type,
                                     resource_name, version)
        message, status_code = self.request(target_uri, PUT,
                                            request_object=payload)
        operation = 'modify {} resource'.format(resource_type)
        self.check_status_code_success(operation, status_code, message)
        return message

    def delete_resource(
            self, array, category, resource_type, resource_name,
            payload=None, params=None):
        """Delete a resource.

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
        operation = 'delete {} resource'.format(resource_type)
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
        """Returns a list of arrays.

        :param filters: optional dict of filters
        :return: dict
        """
        target_uri = "/{}/system/symmetrix".format(self.U4V_VERSION)
        response = self.get_request(target_uri, 'symmetrix', params=filters)
        if response and response.get('symmetrixId'):
            return response['symmetrixId']
        return []

    def get_v3_or_newer_array_list(self, filters=None):
        """Returns a list of V3 or newer arrays in the environment.

        :param filters: optional dict of filters
        :return: list of array ids
        """
        target_uri = "/{}/sloprovisioning/symmetrix".format(self.U4V_VERSION)
        response = self.get_request(target_uri, 'symmetrix', params=filters)
        if response and response.get('symmetrixId'):
            return response['symmetrixId']
        return []

    def get_array(self, array_id):
        """Return details on specific array.

        :return: server response
        """
        target_uri = "/{}/system/symmetrix/{}".format(
            self.U4V_VERSION, array_id)
        return self.get_request(target_uri, 'symmetrix')

    def get_iterator_page_list(self, iterator_id, start, end):
        """Get a page of results from an iterator instance.

        :param iterator_id: the id of the iterator
        :param start: the start number
        :param end: the end number
        :return: dict
        """
        target_uri = 'common/Iterator/{}/page'.format(iterator_id)
        filters = {'from': start, 'to': end}
        return self.get_request(target_uri, 'iterator', params=filters)

    def get_wlp_timestamp(self, array_id):
        """Get the latest timestamp from WLP for processing New Workloads.

        :return: dict
        """
        target_uri = ("/{}/wlp/symmetrix/{}".format(
            self.U4V_VERSION, array_id))
        return self.get_request(target_uri, 'wlp')

    def get_headroom(self, array_id, workload, srp="SRP_1", slo="Diamond"):
        """Get the Remaining Headroom Capacity.

        Get the headroom capacity for a given srp/ slo/ workload combination.
        Exapmle output:
        {'headroom': [{'workloadType': 'OLTP',
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
        params = {'srp': srp, 'slo': slo, 'workloadtype': workload}
        return self.get_resource(array_id, 'wlp', 'headroom', params=params)
