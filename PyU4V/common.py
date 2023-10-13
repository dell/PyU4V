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
"""common.py."""

import json
import logging
import math
import re
import six
import socket
import time

from PyU4V.utils import constants
from PyU4V.utils import exception

LOG = logging.getLogger(__name__)

# HTTP constants
GET = constants.GET
POST = constants.POST
PUT = constants.PUT
DELETE = constants.DELETE

# Status code constants
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

# Resource constants
SYSTEM = constants.SYSTEM
JOB = constants.JOB
VERSION = constants.VERSION
SYMMETRIX = constants.SYMMETRIX
SLOPROVISIONING = constants.SLOPROVISIONING
COMMON = constants.COMMON
ITERATOR = constants.ITERATOR
PAGE = constants.PAGE
WLP = constants.WLP
HEADROOM = constants.HEADROOM


class CommonFunctions(object):
    """CommonFunctions."""

    def __init__(self, rest_client):
        """__init__."""
        self.rest_client = rest_client
        self.request = self.rest_client.rest_request
        self.interval = self.rest_client.interval
        self.retries = self.rest_client.retries
        self.UNI_VERSION = constants.UNISPHERE_VERSION

    def wait_for_job_complete(self, job):
        """Given the job wait for it to complete.

        :param job: job details -- dict
        :returns: response code, result, status, task details -- int, str, str,
                  list
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
            """Called at an interval until the job is finished."""
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
                    else:
                        kwargs['status'], kwargs['task'] = status, task
            except Exception as error:
                exception_message = 'Issue encountered waiting for job.'
                LOG.exception(exception_message)
                raise exception.VolumeBackendAPIException(
                    data=exception_message) from error

            return kwargs

        job_id = job['jobId']
        kwargs = {'retries': 0, 'wait_for_job_called': False,
                  'rc': 0, 'result': None}

        while not kwargs['wait_for_job_called']:
            time.sleep(self.interval)
            kwargs = _wait_for_job_complete()
            if kwargs['retries'] > self.retries:
                LOG.error('_wait_for_job_complete failed after {cnt} '
                          'tries.'.format(cnt=kwargs['retries']))
                kwargs['rc'], kwargs['result'] = -1, kwargs['result']
                break

        LOG.debug('Return code is: {rc}. Result is {res}.'.format(
            rc=kwargs['rc'], res=kwargs['result']))
        return (kwargs['rc'], kwargs['result'],
                kwargs['status'], kwargs['task'])

    def get_job_by_id(self, job_id):
        """Get details of a specific job.

        :param job_id: job id -- str
        :returns: job details -- dict
        """
        return self.get_resource(category=SYSTEM, resource_level=JOB,
                                 resource_level_id=job_id)

    def _is_job_finished(self, job_id):
        """Check if the job is finished.

        :param job_id: job id -- str
        :returns: job complete, result, response code, status, task
                  details -- bool, str, int, str, list
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

        :param operation: operation being performed -- str
        :param status_code: status code -- int
        :param message: server response -- str
        :raises: VolumeBackendAPIException
        """
        if status_code not in [STATUS_200, STATUS_201,
                               STATUS_202, STATUS_204]:
            exception_message = (
                'Error {op}. The status code received is {sc} and the message '
                'is {msg}.'.format(op=operation, sc=status_code, msg=message))
            if status_code == STATUS_404:
                raise exception.ResourceNotFoundException(
                    data=exception_message)
            if status_code == STATUS_401:
                raise exception.UnauthorizedRequestException()

            raise exception.VolumeBackendAPIException(
                data=exception_message)

    def wait_for_job(self, operation, status_code, job):
        """Check if call is async, wait for it to complete.

        :param operation: operation being performed -- str
        :param status_code: status code -- int
        :param job: job id -- str
        :returns: task details -- list
        :raises: VolumeBackendAPIException
        """
        task = None
        if status_code == STATUS_202:
            rc, result, status, task = self.wait_for_job_complete(job)
            if rc != 0:
                exception_message = (
                    'Error {op}. Status code: {sc}. Error: {err}. '
                    'Status: {st}.'.format(
                        op=operation, sc=rc, err=six.text_type(result),
                        st=status))
                LOG.error(exception_message)
                raise exception.VolumeBackendAPIException(
                    data=exception_message)
        return task

    def build_target_uri(self, **kwargs):
        """Build the target URI.

        This function calls into _build_uri() for access outside this class.

        :key version: Unisphere version -- int
        :key no_version: if versionless uri -- bool
        :key category: resource category e.g. sloprovisioning -- str
        :key resource_level: resource level e.g. storagegroup -- str
        :key resource_level_id: resource level id -- str
        :key resource_type: optional name of resource -- str
        :key resource_type_id: optional name of resource -- str
        :key resource: optional name of resource -- str
        :key resource_id: optional name of resource -- str
        :key object_type: optional name of resource -- str
        :key object_type_id: optional name of resource -- str
        :returns: target URI -- str
        """
        return self._build_uri(**kwargs)

    def _build_uri(self, **kwargs):
        """Build the target URI.

        :key version: Unisphere version -- int
        :key no_version: if versionless uri -- bool
        :key category: resource category e.g. sloprovisioning -- str
        :key resource_level: resource level e.g. storagegroup -- str
        :key resource_level_id: resource level id -- str
        :key resource_type: optional name of resource -- str
        :key resource_type_id: optional name of resource -- str
        :key resource: optional name of resource -- str
        :key resource_id: optional name of resource -- str
        :key object_type: optional name of resource -- str
        :key object_type_id: optional name of resource -- str
        :returns: target URI -- str
        """
        target_uri, version = str(), None

        if kwargs.get('category') not in ['performance', 'common']:
            version = self._build_uri_get_version(kwargs.get('version'),
                                                  kwargs.get('no_version'))
        if version:
            target_uri += '/{version}'.format(version=version)

        target_uri += '/{category}'.format(
            category=kwargs.get('category'))

        if kwargs.get('resource_level'):
            target_uri += '/{resource_level}'.format(
                resource_level=kwargs.get('resource_level'))

        if kwargs.get('resource_level_id'):
            target_uri += '/{resource_level_id}'.format(
                resource_level_id=kwargs.get('resource_level_id'))

        if kwargs.get('resource_type'):
            target_uri += '/{resource_type}'.format(
                resource_type=kwargs.get('resource_type'))
            if kwargs.get('resource_type_id'):
                target_uri += '/{resource_type_id}'.format(
                    resource_type_id=kwargs.get('resource_type_id'))

        if kwargs.get('resource'):
            target_uri += '/{resource}'.format(
                resource=kwargs.get('resource'))
            if kwargs.get('resource_id'):
                target_uri += '/{resource_id}'.format(
                    resource_id=kwargs.get('resource_id'))

        if kwargs.get('object_type'):
            target_uri += '/{object_type}'.format(
                object_type=kwargs.get('object_type'))
            if kwargs.get('object_type_id'):
                target_uri += '/{object_type_id}'.format(
                    object_type_id=kwargs.get('object_type_id'))

        return target_uri

    def _build_uri_get_version(self, version=None, no_version=False):
        """Get the Unisphere version for the target URI.

        :param version: version to use from kwargs -- str
        :param no_version: if URI should be versionless -- bool
        :returns: version -- str
        """
        if not version and no_version:
            version = None
        elif not version and not no_version:
            version = self.UNI_VERSION
        elif version and no_version:
            LOG.debug(
                'Version has been specified along with no_version flag, '
                'ignoring no_version flag and using version {ver}'.format(
                    ver=version))
        return version

    def get_request(self, target_uri, resource_type, params=None):
        """Send a GET request to the array.

        :param target_uri: target uri -- str
        :param resource_type: the resource type, e.g. maskingview -- str
        :param params: optional filter params -- dict
        :returns: resource_object -- dict
        :raises: ResourceNotFoundException
        """
        message, sc = self.request(target_uri, GET, params=params)
        operation = 'GET {resource_type}'.format(resource_type=resource_type)
        self.check_status_code_success(operation, sc, message)
        return message

    def get_resource(self, *args, **kwargs):
        """Get resource details from the array.

        :key version: Unisphere version -- int
        :key no_version: if versionless uri -- bool
        :key category: resource category e.g. sloprovisioning -- str
        :key resource_level: resource level e.g. storagegroup -- str
        :key resource_level_id: resource level id -- str
        :key resource_type: optional name of resource -- str
        :key resource_type_id: optional name of resource -- str
        :key resource: optional name of resource -- str
        :key resource_id: optional name of resource -- str
        :key object_type: optional name of resource -- str
        :key object_type_id: optional name of resource -- str
        :key params: query parameters -- dict
        :returns: resource object -- dict
        """
        target_uri = self._build_uri(**kwargs)
        resource_type = None
        if args:
            resource_type = args[2]
        elif not args and kwargs:
            resource_type = kwargs.get('resource_level')
        return self.get_request(
            target_uri, resource_type, kwargs.get('params'))

    def create_resource(self, *args, **kwargs):
        """Create a resource.

        :key version: Unisphere version -- int
        :key no_version: if versionless uri -- bool
        :key category: resource category e.g. sloprovisioning -- str
        :key resource_level: resource level e.g. storagegroup -- str
        :key resource_level_id: resource level id -- str
        :key resource_type: optional name of resource -- str
        :key resource_type_id: optional name of resource -- str
        :key resource: optional name of resource -- str
        :key resource_id: optional name of resource -- str
        :key object_type: optional name of resource -- str
        :key object_type_id: optional name of resource -- str
        :key payload: query parameters -- dict
        :returns: resource object -- dict
        """
        target_uri = self._build_uri(**kwargs)
        if kwargs.get('target_uri'):
            target_uri = (kwargs.get('target_uri'))
        message, status_code = self.request(
            target_uri, POST, request_object=kwargs.get('payload'))
        resource_type = None
        if args:
            resource_type = args[2]
        elif not args and kwargs:
            resource_type = kwargs.get('resource_level')
        operation = ('POST {resource_type} resource'.format(
            resource_type=resource_type))
        self.check_status_code_success(operation, status_code, message)
        return message

    def modify_resource(self, *args, **kwargs):
        """Modify a resource.

        :key version: Unisphere version -- int
        :key no_version: if versionless uri -- bool
        :key category: resource category e.g. sloprovisioning -- str
        :key resource_level: resource level e.g. storagegroup -- str
        :key resource_level_id: resource level id -- str
        :key resource_type: optional name of resource -- str
        :key resource_type_id: optional name of resource -- str
        :key resource: optional name of resource -- str
        :key resource_id: optional name of resource -- str
        :key object_type: optional name of resource -- str
        :key object_type_id: optional name of resource -- str
        :key payload: query parameters
        :returns: resource object -- dict
        """
        target_uri = self._build_uri(**kwargs)
        if kwargs.get('target_uri'):
            target_uri = (kwargs.get('target_uri'))
        message, status_code = self.request(
            target_uri, PUT, request_object=kwargs.get('payload'))
        resource_type = None
        if args:
            resource_type = args[2]
        elif not args and kwargs:
            resource_type = kwargs.get('resource_level')
        operation = ('PUT {resource_type} resource'.format(
            resource_type=resource_type))
        self.check_status_code_success(operation, status_code, message)
        return message

    def delete_resource(self, *args, **kwargs):
        """Delete a resource.

        :key version: Unisphere version -- int
        :key no_version: if versionless uri -- bool
        :key category: resource category e.g. sloprovisioning -- str
        :key resource_level: resource level e.g. storagegroup -- str
        :key resource_level_id: resource level id -- str
        :key resource_type: optional name of resource -- str
        :key resource_type_id: optional name of resource -- str
        :key resource: optional name of resource -- str
        :key resource_id: optional name of resource -- str
        :key object_type: optional name of resource -- str
        :key object_type_id: optional name of resource -- str
        :key payload: query parameters
        """
        target_uri = self._build_uri(**kwargs)
        if kwargs.get('target_uri'):
            target_uri = (kwargs.get('target_uri'))
        message, status_code = self.request(
            target_uri, DELETE, request_object=kwargs.get('payload'),
            params=kwargs.get('params'))
        resource_type = None
        if args:
            resource_type = args[2]
        elif not args and kwargs:
            resource_type = kwargs.get('resource_level')
        operation = ('DELETE {resource_type} resource'.format(
            resource_type=resource_type))
        self.check_status_code_success(operation, status_code, message)

    def download_file(self, **kwargs):
        """Download a file.

        :key version: Unisphere version -- int
        :key no_version: if versionless uri -- bool
        :key category: resource category e.g. sloprovisioning -- str
        :key resource_level: resource level e.g. storagegroup -- str
        :key resource_level_id: resource level id -- str
        :key resource_type: optional name of resource -- str
        :key resource_type_id: optional name of resource -- str
        :key resource: optional name of resource -- str
        :key resource_id: optional name of resource -- str
        :key object_type: optional name of resource -- str
        :key object_type_id: optional name of resource -- str
        :key payload: query parameters -- dict
        :returns: file info including binary data -- dict
        :raises: ValueError
        """
        target_uri = self._build_uri(**kwargs)
        if kwargs.get('target_uri'):
            target_uri = (kwargs.get('target_uri'))
        response, status_code = self.rest_client.file_transfer_request(
            method=POST, download=True, uri=target_uri,
            timeout=kwargs.get('timeout'), r_obj=kwargs.get('payload'))
        try:
            message = response.raw.reason
            operation = ('download {resource_type} resource'.format(
                resource_type=kwargs.get('resource_level')))
            self.check_status_code_success(operation, status_code, message)
        except ValueError:
            LOG.error(
                'There request to download from {uri} has failed and no '
                'message has been returned from Unisphere. Please check '
                'Unisphere REST logs for further details.'.format(
                    uri=target_uri))
        return response

    def upload_file(self, **kwargs):
        """Upload a file.

        :key version: Unisphere version -- int
        :key no_version: if versionless uri -- bool
        :key category: resource category e.g. sloprovisioning -- str
        :key resource_level: resource level e.g. storagegroup -- str
        :key resource_level_id: resource level id -- str
        :key resource_type: optional name of resource -- str
        :key resource_type_id: optional name of resource -- str
        :key resource: optional name of resource -- str
        :key resource_id: optional name of resource -- str
        :key object_type: optional name of resource -- str
        :key object_type_id: optional name of resource -- str
        :key form_data: multipart form data -- dict
        :returns: response success details -- dict
        """
        response_content = dict()
        target_uri = self._build_uri(**kwargs)
        if kwargs.get('target_uri'):
            target_uri = (kwargs.get('target_uri'))
        response, status_code = self.rest_client.file_transfer_request(
            method=POST, upload=True, uri=target_uri,
            form_data=kwargs.get('form_data'))
        try:
            response_content = json.loads(response.text)
            msg = response_content.get('message')
            operation = ('upload {resource_type} resource'.format(
                resource_type=kwargs.get('resource_level')))
            self.check_status_code_success(operation, status_code, msg)
            # Workaround until failed responses do not return 200
            if not response_content.get('success', False):
                LOG.error(msg)
                raise exception.VolumeBackendAPIException(msg)
            LOG.info('The settings upload request was successful.')
        except ValueError:
            LOG.error(
                'There request to upload to {uri} has failed and no '
                'message has been returned from Unisphere. Please check '
                'Unisphere REST logs for further details.'.format(
                    uri=target_uri))
        return response_content

    def get_uni_version(self):
        """Get the unisphere version from the server.

        :returns: version and major_version e.g. "V10.0.0.0", "100" -- str, str
        """
        version, major_version = None, None
        response = self.get_resource(category=VERSION, no_version=True)
        if response and response.get('version'):
            version = response['version']
            version_list = version.split('.')
            major_version = version_list[0][1:] + version_list[1]
        return version, major_version

    def get_uni_version_info(self):
        """Get the unisphere version from the server.

        :returns: {'version': 'T10.1.0.468', 'api_version': '101',
                  'supported_api_versions': ['101', '100', '92']} -- dict
        """
        response = self.get_resource(category=VERSION, no_version=True)

        return response

    def get_array_list(self, filters=None):
        """Return a list of arrays.

        :param filters: optional filters -- dict
        :returns: arrays ids -- list
        """
        response = self.get_resource(
            category=SYSTEM, resource_level=SYMMETRIX, params=filters)
        return response.get('symmetrixId', list()) if response else list()

    def get_v3_or_newer_array_list(self, filters=None):
        """Return a list of V3 or newer arrays in the environment.

        :param filters: optional filters -- dict
        :returns: arrays ids -- list
        """
        response = self.get_resource(
            category=SLOPROVISIONING, resource_level=SYMMETRIX, params=filters)
        return response.get('symmetrixId', list()) if response else list()

    def get_array(self, array_id):
        """Get array details.

        :param array_id: array id -- str
        :returns: array details -- dict
        """
        return self.get_resource(category=SYSTEM, resource_level=SYMMETRIX,
                                 resource_level_id=array_id)

    def get_iterator_page_list(self, iterator_id, start, end):
        """Get a page of results from an iterator instance.

        :param iterator_id: iterator id -- str
        :param start: the start number -- int
        :param end: the end number -- int
        :returns: iterator page results -- dict
        """
        response = self.get_resource(
            no_version=True, category=COMMON, resource_level=ITERATOR,
            resource_level_id=iterator_id, resource_type=PAGE,
            params={'from': start, 'to': end})
        return response.get('result', list()) if response else list()

    def get_iterator_results(self, rest_response):
        """Get all results from all pages of an iterator if count > 1000.

        :param rest_response: response JSON from REST API -- dict
        :returns: all results -- dict
        """
        full_response = list()
        full_response += rest_response['resultList']['result']

        if rest_response.get('count') and int(rest_response.get('count')) > 0:
            count = rest_response.get('count')
            max_page_size = rest_response.get('maxPageSize')
            if int(count) > int(max_page_size):
                total_iterations = int(math.ceil(count / float(max_page_size)))
                iterator_id = rest_response.get('id')
                # We skip to second page as we already have the first page in
                # the input param rest_response
                for x in range(1, total_iterations):
                    start = x * max_page_size + 1
                    end = (x + 1) * max_page_size
                    if end > count:
                        end = count
                    full_response += self.get_iterator_page_list(iterator_id,
                                                                 start, end)
        return full_response

    @staticmethod
    def check_ipv4(ipv4):
        """Check if a given string is a valid ipv6 address

        :param ipv4: ipv4 address -- str
        :returns: string is valid ipv4 address -- bool
        """
        try:
            socket.inet_pton(socket.AF_INET, ipv4)
            return True
        except socket.error:
            return False

    @staticmethod
    def check_ipv6(ipv6):
        """Check if a given string is a valid ipv6 address

        :param ipv6: ipv6 address -- str
        :returns: string is valid ipv6 address -- bool
        """
        try:
            socket.inet_pton(socket.AF_INET6, ipv6)
            return True
        except socket.error:
            return False

    @staticmethod
    def convert_to_snake_case(camel_case_string):
        """Convert a string from camel case to snake case.

        :param camel_case_string: string for formatting -- str
        :returns: snake case variant -- str
        """
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_case_string)
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        return s2.replace('__', '_')

    @staticmethod
    def check_timestamp(in_timestamp):
        """Check that the timestamp is in the correct format

        :param in_timestamp: timestamp e.g. 2020-11-24 15:00 -- str
        """

        pattern = (r'^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1]) '
                   r'(2[0-3]|[01][0-9]):[0-5][0-9]$')
        return re.match(pattern, in_timestamp)

    @staticmethod
    def check_epoch_timestamp(in_epoch_timestamp):
        """Check that the timestamp is in the correct format

        :param in_epoch_timestamp: timestamp e.g. 1554332400 -- str
        """

        pattern1 = r'^[0-9]{10}$'
        pattern2 = r'^[0-9]{13}$'
        return re.match(pattern1, in_epoch_timestamp) or re.match(
            pattern2, in_epoch_timestamp)

    def is_array_v4(self, array_id):
        """Check to see if array is a v4

        :param array_id: the array serial number
        :returns: bool
        """

        is_v4 = False
        array_details = self.get_array(array_id)

        if array_details:
            ucode_version = array_details.get(
                'ucode') or array_details.get('microcode')
            if ucode_version:
                major_version = ucode_version.split('.')[0]
                if major_version >= constants.UCODE_6079:
                    is_v4 = True

        return is_v4
