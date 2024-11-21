# Copyright (c) 2021 Dell Inc. or its subsidiaries.
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
"""performance.py."""

import copy
import logging
import re
import socket
import time
from PyU4V import common
from PyU4V import real_time
from PyU4V.utils import exception
from PyU4V.utils import file_handler
from PyU4V.utils import performance_constants as pc


LOG = logging.getLogger(__name__)


class PerformanceFunctions(object):
    """PerformanceFunctions."""

    def __init__(self, array_id, rest_client):
        """__init__."""
        self.common = common.CommonFunctions(rest_client)
        self.real_time = real_time.RealTimeFunctions(array_id, rest_client)
        self.post_request = self.common.create_resource
        self.get_request = self.common.get_resource
        self.put_request = self.common.modify_resource
        self.array_id = array_id
        self.is_v4 = self.common.is_array_v4(self.array_id)
        self.timestamp = None
        self.recency = 7

    def set_array_id(self, array_id):
        """Set the array id.

        :param array_id: array id -- str
        """
        self.array_id = array_id

    def set_timestamp(self, timestamp):
        """Set the performance timestamp.

        :param timestamp: the performance timestamp -- str
        """
        self.timestamp = timestamp

    def set_recency(self, minutes):
        """Set the recency value in minutes.

        :param minutes: recency minutes -- int
        """
        self.recency = minutes

    def is_array_diagnostic_performance_registered(self, array_id=None):
        """Check if an array is registered for diagnostic performance data.

        :param array_id: array id -- str
        :returns: is diagnostic registered -- bool
        """
        array_id = self.array_id if not array_id else array_id
        response = self.get_request(
            category=pc.PERFORMANCE, resource_level=pc.ARRAY,
            resource_type=pc.REG, resource_type_id=array_id)
        return response.get('isRegistered', False) if response else False

    def is_array_real_time_performance_registered(self, array_id=None):
        """Check if an array is registered for real-time performance data.

        :param array_id: array id -- str
        :returns: is real-time registered -- bool
        """
        array_id = self.array_id if not array_id else array_id
        try:
            response = self.get_array_registration_details(array_id)
            return response.get('realtime', False) if response else False
        except exception.VolumeBackendAPIException as e:
            LOG.error(e)
            return False

    def get_array_registration_details(self, array_id=None):
        """Get array performance registration details.

        This call will return information about both diagnostic and real-time
        performance registration along with the diagnostic collection interval
        in minutes.

        :param array_id: array id -- str
        :returns: array performance registration details -- dict
        """
        array_id = self.array_id if not array_id else array_id
        response = self.get_request(
            category=pc.PERFORMANCE, resource_level=pc.ARRAY,
            resource_type=pc.REG_DETAILS, resource_type_id=array_id)
        reg_details = response.get(pc.REG_DETAILS_INFO)
        return reg_details[0] if len(reg_details) > 0 else dict()

    def enable_diagnostic_data_collection(self, array_id=None):
        """Register an array for diagnostic performance data gathering.

        :param array_id: array id -- str
        :raises: VolumeBackendAPIException
        """
        array_id = self.array_id if not array_id else array_id

        if not self.is_array_diagnostic_performance_registered(array_id):
            response = self.post_request(
                category=pc.PERFORMANCE, resource_level=pc.ARRAY,
                resource_type=pc.REGISTER, payload={pc.SYMM_ID: array_id,
                                                    pc.REG_DIAGNOSTIC: True,
                                                    pc.REAL_TIME: False})

            response_message = response.get('message', list())
            if response_message:
                msg = response_message[0]
                if 'Successfully' in msg:
                    LOG.info(msg)
                else:
                    LOG.error(msg)
                    raise exception.VolumeBackendAPIException(message=msg)
            else:
                msg = ('There has been an issue registering array {arr} for '
                       'diagnostic performance data. It was not possible '
                       'to retrieve a message from the REST API detailing the '
                       'error, please check Unisphere Logs.')
                LOG.error(msg)
                raise exception.VolumeBackendAPIException(message=msg)
        else:
            LOG.info('Array {arr} is already registered for diagnostic '
                     'performance data.'.format(arr=array_id))

    def disable_diagnostic_data_collection(self, array_id=None):
        """Disable an array from diagnostic performance data gathering.

        Note: Disabling diagnostic performance data gathering will also
        disable real-time data gathering.

        :param array_id: array id -- str
        :raises: VolumeBackendAPIException
        """
        array_id = self.array_id if not array_id else array_id

        if self.is_array_diagnostic_performance_registered(array_id):
            LOG.warning('Disabling diagnostic performance data collection '
                        'will also disable real-time data collection, if '
                        'enabled.')
            response = self.post_request(
                category=pc.PERFORMANCE, resource_level=pc.ARRAY,
                resource_type=pc.REGISTER, payload={pc.SYMM_ID: array_id,
                                                    pc.REG_DIAGNOSTIC: False,
                                                    pc.REAL_TIME: False})

            response_message = response.get('message', list())
            if response_message:
                msg = response_message[0]
                if 'Successfully' in msg:
                    LOG.info(msg)
                else:
                    LOG.error(msg)
                    raise exception.VolumeBackendAPIException(message=msg)
            else:
                msg = ('There has been an issue disabled array {arr} '
                       'diagnostic performance data. It was not possible '
                       'to retrieve a message from the REST API detailing the '
                       'error, please check Unisphere Logs.')
                LOG.error(msg)
                raise exception.VolumeBackendAPIException(message=msg)
        else:
            LOG.info('Array {arr} is already disabled for diagnostic '
                     'performance data.'.format(arr=array_id))

    def enable_real_time_data_collection(
            self, array_id=None, storage_group_list=None, file=False):
        """Register an array for real-time performance data gathering.

        Note: Real-time performance data is not supported for arrays
        running HyperMax OS.

        :param array_id: array id -- str
        :param storage_group_list: comma separated list of storage groups
                                   to be registered for real time stats
                                   collection e.g. 'sg1, sg2' -- str
        :param file: register file collection for performance --bool
        :raises: VolumeBackendAPIException
        """
        array_id = self.array_id if not array_id else array_id

        payload = {'symmetrixId': array_id,
                   'diagnostic': True,
                   'realtime': True,
                   'file': False}

        if storage_group_list:
            payload.update({'selectedSGs': storage_group_list})

        response = self.post_request(
            category=pc.PERFORMANCE, resource_level=pc.ARRAY,
            resource_type=pc.REGISTER, payload=payload)

        return response

    def disable_real_time_data_collection(self, array_id=None):
        """Disable an array from real-time performance data gathering.

        :param array_id: array_id -- str
        :raises: VolumeBackendAPIException
        """
        array_id = self.array_id if not array_id else array_id

        if self.is_array_real_time_performance_registered(array_id):
            # Retain the existing diagnostic performance setting
            diag_reg = self.is_array_diagnostic_performance_registered(
                array_id)

            response = self.post_request(
                category=pc.PERFORMANCE, resource_level=pc.ARRAY,
                resource_type=pc.REGISTER, payload={
                    pc.SYMM_ID: array_id, pc.REG_DIAGNOSTIC: diag_reg,
                    pc.REAL_TIME: False})

            response_message = response.get('message', list())
            if response_message:
                msg = response_message[0]
                if 'Successfully' in msg:
                    LOG.info(msg)
                else:
                    LOG.error(msg)
                    raise exception.VolumeBackendAPIException(message=msg)
            else:
                msg = ('There has been an issue disabling array {arr} '
                       'real-time performance data. It was not possible '
                       'to retrieve a message from the REST API detailing the '
                       'error, please check Unisphere Logs.')
                LOG.error(msg)
                raise exception.VolumeBackendAPIException(message=msg)
        else:
            LOG.info('Array {arr} is already disabled for real-time '
                     'performance data.'.format(arr=array_id))

    def backup_performance_database(
            self, array_id=None, filename=str(), last_day_of_diagnostic=False,
            named_real_time_traces=False):
        """Backup an array performance database.

        Backup of a performance database is a recommended practice. The backup
        performance database option is available for one or more storage
        systems, regardless of their registration status.

        By default, only Trending & Planning (Historical) data is backed up.
        The performance databases backups should be stored in a safe location.
        Performance database backups can be restored. For more information on
        restoring backups please see Unisphere for PowerMax official
        documentation, for now only performing backups is supported via REST.

        Note: Underscores will be stripped from any filename provided, this is
        due to Unisphere restricting the length of the filename string when
        underscores are provided.

        The backup filename format will be as follows when viewed in Unisphere:

            {array_id}_{date}{time}_{TZ}_{filename}_SPABackup.dat

        :param array_id: array id -- str
        :param filename: performance backup file name -- str
        :param last_day_of_diagnostic: Last day of Diagnostics, this option is
                                       not recommended for recurring
                                       backups -- bool
        :param named_real_time_traces: Named Real Time Traces, this option is
                                       not recommended for recurring
                                       backups -- bool
        :raises: exception.VolumeBackendAPIException
        """
        array_id = self.array_id if not array_id else array_id
        filename.strip('_')
        if not filename:
            filename = '{prefix}-{host}'.format(prefix=pc.FILENAME_PREFIX,
                                                host=socket.gethostname())
        try:
            response = self.post_request(
                category=pc.PERFORMANCE, resource_level=pc.ARRAY,
                resource_type=pc.BACKUP, payload={
                    pc.SYMM_ID: array_id, pc.FILENAME: filename,
                    pc.NAMED_RT_TRACES: last_day_of_diagnostic,
                    pc.LAST_DAY_DIAG: named_real_time_traces})
            LOG.info(response.get('message')[0])
        except exception.VolumeBackendAPIException as e:
            LOG.error(e)
            raise exception.VolumeBackendAPIException(e)

    def get_last_available_timestamp(self, array_id=None):
        """Get the last recorded performance timestamp.

        :param array_id: array_id: array id -- str
        :returns: timestamp -- int
        :raises: ResourceNotFoundException
        """
        array_id = self.array_id if not array_id else array_id
        timestamp = None

        response = self.get_request(
            category=pc.PERFORMANCE, resource_level=pc.ARRAY,
            resource_type=pc.KEYS)
        if response:
            for key in response.get(pc.ARRAY_INFO):
                if key and key.get(pc.SYMM_ID) == array_id:
                    timestamp = key[pc.LA_DATE]
            if not timestamp:
                msg = ('Array {arr} could not be found in list of performance '
                       'keys.'.format(arr=array_id))
                LOG.info(msg)
                raise exception.ResourceNotFoundException(data=msg)

        return timestamp

    def is_timestamp_current(self, timestamp, minutes=None):
        """Check if the timestamp is less than a user specified set of minutes.

        If no minutes value is provided, self.recency is used. Seven minutes
        is recommended to provide a small amount of time for the STP daemon to
        record the next set of metrics in five minute intervals.

        :param timestamp: timestamp in milliseconds since epoch -- int
        :param minutes: timestamp recency in minutes -- int
        :returns: if timestamp is less than recency value -- bool
        """
        r = minutes if isinstance(minutes, int) else self.recency
        return (int(time.time()) * 1000) - timestamp < r * pc.ONE_MINUTE

    @staticmethod
    def get_timestamp_by_hour(
            start_time=None, end_time=None, hours_difference=None):
        """Get timestamp difference in hours from supplied time.

        If start time is provided but not end time, the time difference will be
        after the start time.

        If end time is provided but not start time, the time difference will be
        before the end time.

        If neither start or end time are provided, or both are incorrectly
        provided, the time difference is from the current time.

        :param start_time: timestamp in milliseconds since epoch -- int
        :param end_time: timestamp in milliseconds since epoch -- int
        :param hours_difference: difference in hours -- int
        :returns: timestamp in milliseconds since epoch -- str
        """
        time_difference = pc.ONE_HOUR * hours_difference
        if start_time and not end_time:
            end_time = start_time + time_difference
        elif end_time and not start_time:
            start_time = end_time - time_difference
        else:
            end_time = int(round(time.time() * 1000))
            start_time = end_time - time_difference
        return start_time, end_time

    def _get_rb_key(self, category):
        """Get the required request body key for array/symmetrix ID.

        In Unisphere 10.0 V4 arrays with new categories use arrayId instead
        of symmetrixId, this call determines if the new key should be used
        or the old one.

        :param category: the target performance category -- str
        :returns: the request body key -- str
        """
        key = pc.SYMM_ID
        if category and category in pc.NEW_CATEGORIES:
            key = pc.SYSTEM_ID

        return key

    def _run_v4_filesystem_request(self, category, request_body, keys=False,
                                   metrics=False):
        """Perform request to get keys or stats for file.

        Filsystem endpoints are nested under /performance/file so do not follow
        traditional layout of performance endpoints. This function makes the
        changes required to get at the file endpoints.

        :param category: performance category -- str
        :param keys: if endpoint is for keys -- bool
        :param metrics: if endpoint is for metrics -- bool
        :returns: response -- dict
        :raises: exception.InvalidInputException
        """
        if keys == metrics:
            raise exception.InvalidInputException(
                'You must specify set one of keys or metrics to True for '
                '_run_v4_filesystem_request().')

        rt = None
        if 'FileSystem' in category:
            rt = pc.FILESYSTEM
        elif 'Interface' in category:
            rt = pc.INTERFACE
        elif 'Node' in category:
            rt = pc.NODE
        elif 'Server' in category:
            rt = pc.SERVER

        return self.post_request(
            category=pc.PERFORMANCE, resource_level=pc.FILE,
            resource_type=rt, object_type=pc.KEYS if keys else pc.METRICS,
            payload=request_body)

    def get_performance_key_list(
            self, category, array_id=None, director_id=None,
            storage_group_id=None, storage_container_id=None,
            storage_resource_id=None, start_time=None, end_time=None):
        """Get performance key list for a given performance category.

        :param category: performance category -- str
        :param array_id: array id -- str
        :param director_id: director id -- str
        :param storage_group_id: storage group id -- str
        :param storage_container_id:  storage container id -- str
        :param storage_resource_id: storage resource id -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :returns: category performance keys -- list
        :raises: InvalidInputException
        """
        request_body = dict()
        if array_id:
            request_body[self._get_rb_key(category)] = array_id
        if director_id:
            request_body[pc.DIR_ID] = director_id
        if storage_group_id:
            request_body[pc.SG_ID] = storage_group_id
        if storage_container_id:
            request_body[pc.STORAGE_CONT_ID] = storage_container_id
        if storage_resource_id:
            request_body[pc.STORAGE_RES_ID] = storage_resource_id
        if start_time or end_time:
            request_body[pc.START_DATE] = start_time
            request_body[pc.END_DATE] = end_time

        category_list = self.get_performance_categories_list(array_id)
        if category in category_list:
            if 'SDNAS' in category:
                response = self._run_v4_filesystem_request(
                    category, request_body, keys=True)
            else:
                request = self.get_request if pc.ARRAY in category else (
                    self.post_request)
                response = request(
                    category=pc.PERFORMANCE, resource_level=category,
                    resource_type=pc.KEYS, payload=request_body)

            if response:
                return response
            else:
                raise exception.ResourceNotFoundException(
                    'There are no provisioned assets for performance category '
                    '"{cat}".'.format(cat=category))

        else:
            raise exception.InvalidInputException(
                'Key list extraction failed due to invalid category "{cat}", '
                'please correct the category name before trying '
                'again.'.format(cat=category))

    def get_performance_categories_list(self, array_id=None):
        """Get the list of supported performance categories.

        :param array_id: array id -- str
        :returns: categories -- list
        """
        array_id = self.array_id if not array_id else array_id
        response = self.get_request(
            category=pc.PERFORMANCE, resource_level=pc.ARRAY,
            resource_type=pc.HELP, resource_type_id=array_id,
            resource=pc.CATEGORIES)

        return response.get('categoryName', list()) if response else list()

    def validate_category(self, category, array_id=None):
        """Check that a supplied category is valid.

        :param category: performance category -- str
        :param array_id: array id -- str
        :raises: InvalidInputException
        """
        array_id = self.array_id if not array_id else array_id
        category_list = self.get_performance_categories_list(array_id)
        if category not in category_list:
            raise exception.InvalidInputException(
                'Invalid category "{cat}" supplied, please correct the '
                'supplied category and try again.'.format(cat=category))

    def get_performance_metrics_list(self, category, kpi_only=False,
                                     array_id=None):
        """For a given category, return the list of valid metrics.

        :param category: performance category -- str
        :param kpi_only: if only KPI metrics should be returned -- bool
        :param array_id: array id -- str
        :returns: metrics -- list
        """
        array_id = self.array_id if not array_id else array_id
        category_list = self.get_performance_categories_list(array_id)
        if category in category_list:
            mode = 'Kpi' if kpi_only else 'All'
            response = self.get_request(
                category=pc.PERFORMANCE, resource_level=pc.ARRAY,
                resource_type=pc.HELP, resource_type_id=array_id,
                resource=category, object_type=pc.METRICS,
                object_type_id=mode)
            return response.get('metricName', list()) if response else list()
        else:
            raise exception.InvalidInputException(
                'There was an issue retrieving the metrics for user '
                'specified category "{cat}", please ensure this category is a '
                'valid Unisphere REST API performance category before trying '
                'again.'.format(cat=category))

    @staticmethod
    def format_metrics(metrics):
        """Format metrics input for inclusion in REST request.

        Take metric parameters and format them correctly to be used in
        REST request body. Valid input types are string and list.

        :param metrics:  metric(s) -- str or list
        :returns: metrics -- list
        :raises: InvalidInputException
        """
        if isinstance(metrics, str):
            input_list = [metrics]
        elif isinstance(metrics, list):
            input_list = metrics
        else:
            msg = ('Unknown input parameter type, please pass in a '
                   '<string> or <list> input type.')
            LOG.error(msg)
            raise exception.InvalidInputException(msg)
        return input_list

    def extract_timestamp_keys(
            self, array_id=None, category=None, director_id=None,
            key_tgt_id=None):
        """Retrieve the timestamp keys for a given performance asset.

        Note: If a director key timestamp is required, set this as the
        key_tgt_id, the input parameter director_id is only required for port
        key extraction.

        :param array_id: array id -- str
        :param category: performance category -- str
        :param director_id: director id -- str
        :param key_tgt_id: object id for the timestamp required -- str
        :returns: timestamp in milliseconds since epoch -- str
        """
        array_id = self.array_id if not array_id else array_id
        self.validate_category(category)
        response = self.get_performance_key_list(
            category=category, array_id=array_id, director_id=director_id)
        key_regex = re.compile(r'\A[\w]*(Info)$')
        start = None
        end = None
        for key in response.keys():
            match = key_regex.search(key)
            if match:
                time_keys = response.get(match.group())
                for p_keys in time_keys:
                    for k, v in p_keys.items():
                        tgt_id = array_id if not key_tgt_id else key_tgt_id
                        if isinstance(v, str) and tgt_id in v:
                            start = p_keys.get(pc.FA_DATE)
                            end = p_keys.get(pc.LA_DATE)
        return start, end

    def format_time_input(
            self, array_id=None, category=None, director_id=None,
            key_tgt_id=None, start_time=None, end_time=None):
        """Format time range for use in the request object.

        Use cases are:
        1. If start is set but not end, set end to most recent timestamp
        2. If end is set but not start, set start time to first available
        3. If neither are set, use most recent timestamp
        4. If both are set, skip if conditions and check input is valid

        Note: If a director key timestamp is required, set this as the
        key_tgt_id, the input parameter director_id is only required for port
        key extraction.  A category is only required when timestamp extraction
        is required.

        :param array_id: array id -- str
        :param category: performance category -- str
        :param director_id: director id (for port key extraction only) -- str
        :param key_tgt_id: object id for the timestamp required -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :returns: start time, end time (tuple) -- str, str
        :raises: InvalidInputException
        """
        array_id = self.array_id if not array_id else array_id
        err_msg = None
        # 1. Start is set but not the end, set end time
        if start_time and not end_time:
            end_time = self.get_last_available_timestamp(array_id)
            if not end_time:
                err_msg = (
                    'Last available timestamp could not be extracted from '
                    'Unisphere, please array check performance registration.')

        # 2. End is set but not the start, set start time as first available
        elif end_time and not start_time:
            self.validate_category(category)
            start_time, __ = self.extract_timestamp_keys(
                array_id=array_id, category=category, director_id=director_id,
                key_tgt_id=key_tgt_id)
            if not start_time:
                err_msg = (
                    'First available timestamp could not be extracted from '
                    'Unisphere, please array check performance registration.')

        # 3. Neither are set, set both to the most recent timestamp
        elif not start_time and not end_time:
            self.validate_category(category)
            __, end_time = self.extract_timestamp_keys(
                array_id=array_id, category=category, director_id=director_id,
                key_tgt_id=key_tgt_id)
            start_time = end_time
            if not start_time and not end_time:
                err_msg = (
                    'Timestamps could not be extracted from Unisphere, please '
                    'array check performance registration.')

        if err_msg:
            LOG.error(err_msg)
            raise exception.VolumeBackendAPIException(err_msg)

        # 4. Check time values are valid
        if len(str(start_time)) != 13 and len(str(end_time)) != 13:
            raise exception.InvalidInputException(
                'Invalid time input, time must be in milliseconds since epoch')
        if int(start_time) > int(end_time):
            raise exception.InvalidInputException(
                'The end_time cannot be before start_time')

        return str(start_time), str(end_time)

    def get_performance_stats(
            self, category, metrics, data_format=pc.AVERAGE, array_id=None,
            request_body=None, start_time=None, end_time=None, recency=None):
        """Retrieve the performance statistics for a given category and object.

        :param category: category id -- str
        :param array_id: array id -- str
        :param metrics: performance metrics, options are individual metrics,
                        a list of metrics, 'KPI' for KPI metrics only, and
                        'ALL' for all metrics -- str/list
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param request_body: request params and object IDs -- dict
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        :raises: VolumeBackendAPIException, InvalidInputException
        """
        array_id = self.array_id if not array_id else array_id
        director_id, object_id = None, None
        metrics_list, performance_details = list(), dict()
        if not request_body:
            request_body = dict()

        # 1. Validate category
        self.validate_category(category)

        # 2. Extract required IDs from request body
        if request_body:
            req_body_copy = copy.deepcopy(request_body)
            # Dir/Port Scenario
            if len(req_body_copy) > 1:
                if req_body_copy.get(pc.DIR_ID):
                    director_id = req_body_copy.get(pc.DIR_ID)
                    del req_body_copy[pc.DIR_ID]
            if req_body_copy:
                if req_body_copy.get(pc.DISK_TECH):
                    object_id = req_body_copy.get(pc.DISK_TECH)
                else:
                    key_regex = re.compile(r'\A[\w]*(Id)$')
                    for key in req_body_copy.keys():
                        match = key_regex.search(key)
                        if match:
                            object_id = req_body_copy.get(match.group())

        # 3. Format Time input - request body input need to retrieve object
        # specific timestamps
        start_time, end_time = self.format_time_input(
            array_id=array_id, category=category, director_id=director_id,
            key_tgt_id=object_id, start_time=start_time, end_time=end_time)

        # 4. Check recency
        if recency:
            recency = recency if isinstance(recency, int) else self.recency

            if not self.is_timestamp_current(int(end_time), minutes=recency):
                raise exception.VolumeBackendAPIException(
                    'Timestamp failed recency check of {rec} '
                    'minutes.'.format(rec=recency))

        # 5. Format Metrics
        if isinstance(metrics, list):
            metrics_list = metrics
        elif isinstance(metrics, str):
            if metrics.upper() == pc.KPI.upper():
                metrics_list = self.get_performance_metrics_list(
                    category=category, kpi_only=True)
            elif metrics.upper() == pc.ALL.upper():
                metrics_list = self.get_performance_metrics_list(
                    category=category)
            else:
                metrics_list = self.format_metrics(metrics)

        # 6. Set data format
        if data_format.upper() not in [pc.AVERAGE.upper(), pc.MAXIMUM.upper()]:
            raise exception.InvalidInputException(
                'Invalid data format "{f}" specified, please use one of '
                'Average or Maximum'.format(f=data_format))

        if pc.MAXIMUM.upper() in data_format.upper():
            data_format = pc.MAXIMUM
        else:
            data_format = pc.AVERAGE

        # 7. Add asset IDs to the return dict before additional key/values
        # added
        if request_body:
            for k, v in request_body.items():
                key = self.common.convert_to_snake_case(k)
                performance_details[key] = v

        # 6. Set request body
        request_body[pc.START_DATE] = start_time
        request_body[pc.END_DATE] = end_time
        request_body[self._get_rb_key(category)] = str(array_id)
        request_body[pc.DATA_FORMAT] = str(data_format)
        request_body[pc.METRICS] = metrics_list

        # 7. Post Request
        if 'SDNAS' in category:
            perf_response = self._run_v4_filesystem_request(
                category, request_body, metrics=True)
        else:
            perf_response = self.post_request(
                category=pc.PERFORMANCE, resource_level=category,
                resource_type=pc.METRICS, payload=request_body)

        # 8 Format results response
        performance_details.update(
            {'result': self.common.get_iterator_results(perf_response),
             'array_id': str(array_id),
             'start_date': start_time,
             'end_date': end_time,
             'timestamp': end_time,
             'reporting_level': self.common.convert_to_snake_case(category)})

        return performance_details

    def get_days_to_full(self, array_id=None, array_to_full=False,
                         srp_to_full=False, thin_pool_to_full=False):
        """Get days to full information.

        Requires at least 10 Days of Performance data, available categories
        are 'Array', 'SRP', and 'ThinPool'.

        :param array_id: array id -- str
        :param array_to_full: get array days to full info -- bool
        :param srp_to_full: get storage resource pool days to full info -- bool
        :param thin_pool_to_full: get thin pool days to full info -- bool
        :returns: days to full information -- list
        """
        array_id = self.array_id if not array_id else array_id

        category = None
        if array_to_full:
            category = pc.ARRAY
        elif srp_to_full:
            category = pc.SRP
        elif thin_pool_to_full:
            category = pc.THIN_POOL
        if not category:
            raise exception.InvalidInputException(
                'You must specify a days to full category from "Array", '
                '"SRP", or "Thin Pool" by setting the respective input param '
                'to True in perf.get_days_to_full().')

        request_body = {pc.SYMM_ID: array_id, pc.CATEGORY: category}
        response = self.post_request(
            category=pc.PERFORMANCE, resource_level=pc.DAYS_TO_FULL,
            payload=request_body)
        return response.get(
            pc.DAYS_TO_FULL_RESULT, list()) if response else list()

    def get_threshold_categories(self, array_id=None):
        """Get a list of performance threshold categories.

        :param array_id: array serial number -- str
        :returns: performance threshold categories -- list
        """
        array_id = array_id if array_id else self.array_id
        categories = self.get_request(
            category=pc.PERFORMANCE, resource_level=pc.THRESHOLD,
            resource_type=array_id, resource=pc.CATEGORIES)
        return categories.get(pc.THRESH_CAT, list()) if categories else list()

    def get_threshold_category_settings(self, category, array_id=None):
        """Get performance threshold category settings.

        :param category: category id -- str
        :param array_id: array serial number -- str
        :returns: category settings --  dict
        """
        array_id = array_id if array_id else self.array_id
        return self.get_request(
            category=pc.PERFORMANCE, resource_level=pc.THRESHOLD,
            resource_type=pc.LIST, resource_type_id=array_id,
            resource=category)

    def update_threshold_settings(
            self, category, metric, first_threshold, second_threshold,
            alert=True, first_threshold_occurrences=3,
            first_threshold_samples=5,
            first_threshold_severity=pc.WARN_LVL,
            second_threshold_occurrences=3, second_threshold_samples=5,
            second_threshold_severity=pc.CRIT_LVL,
            include_realtime_trace=False):
        """Edit an existing global threshold across all arrays.

        :param category: category id -- str
        :param metric: performance metric -- str
        :param first_threshold: first threshold value -- int
        :param second_threshold: second threshold value -- int
        :param alert: alert on/off -- bool
        :param first_threshold_occurrences: error occurrences -- int
        :param first_threshold_samples: error samples -- int
        :param first_threshold_severity: error severity, valid values are
                                         'INFORMATION', 'WARNING', and
                                         'CRITICAL' -- str
        :param second_threshold_occurrences: error occurrences -- int
        :param second_threshold_samples: error samples -- int
        :param second_threshold_severity: error severity, valid values are
                                          'INFORMATION', 'WARNING', and
                                          'CRITICAL' -- str
        :param include_realtime_trace: if threshold is breached in addition
                                       to alert a performance
        :returns: operation success details -- dict
        """
        payload = {
            "metric": metric,
            "firstThreshold": str(first_threshold),
            "secondThreshold": str(second_threshold),
            "alert": alert,
            "firstThresholdOccurrrences": str(first_threshold_occurrences),
            "firstThresholdSamples": str(first_threshold_samples),
            "firstThresholdSeverity": str(first_threshold_severity),
            "secondThresholdOccurrrences": str(second_threshold_occurrences),
            "secondThresholdSamples": str(second_threshold_samples),
            "secondThresholdSeverity": str(second_threshold_severity),
            "includeRealTimeTraceOnCritical": include_realtime_trace
        }

        return self.put_request(
            category=pc.PERFORMANCE, resource_level=pc.THRESHOLD,
            resource_type=pc.UPDATE, resource_type_id=category,
            payload=payload)

    def generate_threshold_settings_csv(self, output_csv_path, category=None):
        """Generate a csv file with threshold settings.

        Creates a CSV file with current alert configuration for the given
        unisphere instance category, metric, first_threshold, second_threshold,
        alert_user, kpi.

        :param output_csv_path: filename for CSV to be generated -- str
        :param category: threshold specific category -- str
        """
        category_list = (
            self.get_threshold_categories() if not category else [category])
        data_for_csv = list()
        data_for_csv.append([pc.CATEGORY, pc.METRIC, pc.FIRST_THRESH,
                             pc.SEC_THRESH, pc.ALERT_ERR, pc.KPI])
        for category in category_list:
            metric_setting = self.get_threshold_category_settings(category)
            threshold_settings = metric_setting.get(pc.PERF_THRESH)
            print(threshold_settings)
            for threshold in threshold_settings:
                data_for_csv.append([
                    category, threshold.get(pc.METRIC),
                    int(threshold.get(pc.FIRST_THRESH)),
                    int(threshold.get(pc.SEC_THRESH)),
                    threshold.get(pc.ALERT_ERR), threshold.get(pc.KPI)])
        file_handler.write_to_csv_file(output_csv_path, data_for_csv)

    def set_thresholds_from_csv(self, csv_file_path, kpi_only=True):
        """Set performance thresholds using a CSV file.

        Reads CSV file and sets performance threshold metrics on the values
        contained within. The following headers are required:
        category, metric, firstthreshold, secondthreshold, notify, kpi

        It is advisable to generate the CSV file from the function
        performance.generate_threshold_settings_csv() and edit those values
        within that you would like to change.

        :param csv_file_path: path to CSV file -- str
        :param kpi_only: set only KPI thresholds -- bool
        """
        def _str_to_bool(str_in):
            return str_in == 'True'

        data = file_handler.read_csv_values(csv_file_path)

        category_list = data.get(pc.CATEGORY)
        metric_list = data.get(pc.METRIC)
        notify_list = data.get(pc.ALERT_ERR)
        f_threshold_list = data.get(pc.FIRST_THRESH)
        s_threshold_list = data.get(pc.SEC_THRESH)
        is_kpi = data.get(pc.KPI)

        for i in range(0, len(metric_list)):
            if not _str_to_bool(is_kpi[i]) and kpi_only:
                continue
            if int(f_threshold_list[i]) >= int(s_threshold_list[i]):
                LOG.warning(
                    'Not setting performance metric {m} threshold, second '
                    'threshold value {f} must be greater than first threshold '
                    'value {s}.'.format(
                        m=metric_list[i], f=f_threshold_list[i],
                        s=s_threshold_list[i]))
                continue
            self.update_threshold_settings(
                category=category_list[i], metric=metric_list[i],
                alert=notify_list[i], first_threshold=f_threshold_list[i],
                second_threshold=s_threshold_list[i],
                include_realtime_trace=False)

    def get_array_keys(self):
        """List Arrays registered for performance data collection.

        :returns: Arrays with first and last available dates -- list
        """
        key_list = self.get_performance_key_list(category=pc.ARRAY)
        return key_list.get(pc.ARRAY_INFO, list()) if key_list else list()

    def get_array_stats(
            self, metrics, array_id=None, data_format=pc.AVERAGE,
            start_time=None, end_time=None, recency=None):
        """List performance data for specified array for giving time range.

        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        return self.get_performance_stats(
            array_id=array_id, category=pc.ARRAY, metrics=metrics,
            data_format=data_format, start_time=start_time, end_time=end_time,
            recency=recency)

    def get_backend_director_keys(self, array_id=None):
        """List BE directors for the given array.

        :param array_id: array id -- str
        :returns: BE directors with first and last available dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(category=pc.BE_DIR,
                                                 array_id=array_id)
        return key_list.get(pc.BE_DIR_INFO, list()) if key_list else list()

    def get_backend_director_stats(
            self, director_id, metrics, array_id=None, data_format=pc.AVERAGE,
            start_time=None, end_time=None, recency=None):
        """List time range performance data for given BE director.

        :param director_id: director id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.DIR_ID: director_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.BE_DIR, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_backend_emulation_keys(self, array_id=None):
        """List BE emulations for the given array.

        :param array_id: array id -- str
        :returns: BE emulation info with first and last available dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(category=pc.BE_EMU,
                                                 array_id=array_id)
        return key_list.get(pc.BE_EMU_INFO, list()) if key_list else list()

    def get_backend_emulation_stats(
            self, emulation_id, metrics, array_id=None, data_format=pc.AVERAGE,
            start_time=None, end_time=None, recency=None):
        """List time range performance data for given BE emulation.

        :param emulation_id: emulation id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.BE_EMU_ID: emulation_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.BE_EMU, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_backend_port_keys(self, director_id, array_id=None):
        """List BE ports for the given array.

        :param director_id: array id -- str
        :param array_id: director id -- str
        :returns: BE port info with first and last available dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(
            category=pc.BE_PORT, array_id=array_id, director_id=director_id)
        return key_list.get(pc.BE_PORT_INFO, list()) if key_list else list()

    def get_backend_port_stats(
            self, director_id, port_id, metrics, array_id=None,
            data_format=pc.AVERAGE, start_time=None, end_time=None,
            recency=None):
        """List time range performance data for given BE port.

        :param director_id: director id -- str
        :param port_id: port id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.DIR_ID: director_id, pc.PORT_ID: str(port_id)}
        return self.get_performance_stats(
            array_id=array_id, category=pc.BE_PORT, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_board_keys(self, array_id=None):
        """List boards for the given array.

        :param array_id: array id -- str
        :returns: board info with first and last available dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(category=pc.BOARD,
                                                 array_id=array_id)
        return key_list.get(pc.BOARD_INFO, list()) if key_list else list()

    def get_board_stats(
            self, board_id, metrics, array_id=None,
            data_format=pc.AVERAGE, start_time=None, end_time=None,
            recency=None):
        """List time range performance data for given board.

        :param board_id: board id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.BOARD_ID: board_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.BOARD, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_cache_partition_keys(self, array_id=None):
        """List cache partitions for the given array.

        :param array_id: array id -- str
        :returns: cache partition info with first and last available
                  dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(category=pc.CACHE_PART,
                                                 array_id=array_id)
        return key_list.get(
            pc.CACHE_PART_INFO, list()) if key_list else list()

    def get_cache_partition_perf_stats(
            self, cache_partition_id, metrics, array_id=None,
            data_format=pc.AVERAGE, start_time=None, end_time=None,
            recency=None):
        """List time range performance data for given cache partition.

        :param cache_partition_id: cache partition id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.CACHE_PART_ID: cache_partition_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.CACHE_PART, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_device_group_keys(self, array_id=None):
        """List device groups for the given array.

        :param array_id: array id -- str
        :returns: device group info with first and last available dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(category=pc.DEV_GRP,
                                                 array_id=array_id)
        return key_list.get(pc.DEV_GRP_INFO, list()) if key_list else list()

    def get_device_group_stats(
            self, device_group_id, metrics, array_id=None,
            data_format=pc.AVERAGE, start_time=None, end_time=None,
            recency=None):
        """List time range performance data for given device group.

        :param device_group_id: device group id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.DEV_GRP_ID: device_group_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.DEV_GRP, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_disk_group_keys(self, array_id=None):
        """List disk groups for the given array.

        :param array_id: array id -- str
        :returns: disk info with first and last available dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(category=pc.DISK_GRP,
                                                 array_id=array_id)
        return key_list.get(pc.DISK_GRP_INFO, list()) if key_list else list()

    def get_disk_group_stats(
            self, disk_group_id, metrics, array_id=None,
            data_format=pc.AVERAGE,
            start_time=None, end_time=None, recency=None):
        """List time range performance data for given disk group.

        :param disk_group_id: disk group id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.DISK_GRP_ID: disk_group_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.DISK_GRP, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_eds_director_keys(self, array_id=None):
        """List EDS directors for the given array.

        :param array_id: array id -- str
        :returns: EDS director info with first and last available dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(category=pc.EDS_DIR,
                                                 array_id=array_id)
        return key_list.get(pc.EDS_DIR_INFO, list()) if key_list else list()

    def get_eds_director_stats(
            self, director_id, metrics, array_id=None,
            data_format=pc.AVERAGE, start_time=None, end_time=None,
            recency=None):
        """List time range performance data for given EDS director.

        :param director_id: director id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.DIR_ID: director_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.EDS_DIR, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_eds_emulation_keys(self, array_id=None):
        """List EDS emulations for the given array.

        :param array_id: array id -- str
        :returns: EDS emulation info with first and last available
                  dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(category=pc.EDS_EMU,
                                                 array_id=array_id)
        return key_list.get(pc.EDS_EMU_INFO, list()) if key_list else list()

    def get_eds_emulation_stats(
            self, emulation_id, metrics, array_id=None,
            data_format=pc.AVERAGE, start_time=None, end_time=None,
            recency=None):
        """List time range performance data for given EDS emulation.

        :param emulation_id: emulation id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.EDS_EMU_ID: emulation_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.EDS_EMU, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_em_director_keys(self, array_id=None):
        """List EM directors for the given array.

        :param array_id: array id -- str
        :returns: EDS director info with first and last available dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(category=pc.EM_DIR,
                                                 array_id=array_id)
        return key_list.get(pc.EM_DIR_INFO, list()) if key_list else list()

    def get_em_director_stats(
            self, director_id, metrics, array_id=None,
            data_format=pc.AVERAGE, start_time=None, end_time=None,
            recency=None):
        """List time range performance data for given EM director.

        :param director_id: director id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.DIR_ID: director_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.EM_DIR, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_external_disk_keys(self, array_id=None):
        """List external disks for the given array.

        :param array_id: array id -- str
        :returns: external disks with first and last available dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(category=pc.EXT_DISK,
                                                 array_id=array_id)
        return key_list.get(pc.EXT_DISK_INFO, list()) if key_list else list()

    def get_external_disk_stats(
            self, disk_id, metrics, array_id=None, data_format=pc.AVERAGE,
            start_time=None, end_time=None, recency=None):
        """List time range performance data for given external disk.

        :param disk_id: disk id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.DISK_ID: disk_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.EXT_DISK, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_frontend_director_keys(self, array_id=None):
        """List FE directors for the given array.

        :param array_id: array id -- str
        :returns: FE directors with first and last available dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(category=pc.FE_DIR,
                                                 array_id=array_id)
        return key_list.get(pc.FE_DIR_INFO, list()) if key_list else list()

    def get_frontend_director_stats(
            self, director_id, metrics, array_id=None, data_format=pc.AVERAGE,
            start_time=None, end_time=None, recency=None):
        """List time range performance data for given FE director.

        :param director_id: director id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.DIR_ID: director_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.FE_DIR, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_frontend_emulation_keys(self, array_id=None):
        """List FE emulations for the given array.

        :param array_id: array id -- str
        :returns: BE emulation info with first and last available dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(category=pc.FE_EMU,
                                                 array_id=array_id)
        return key_list.get(pc.FE_EMU_INFO, list()) if key_list else list()

    def get_frontend_emulation_stats(
            self, emulation_id, metrics, array_id=None, data_format=pc.AVERAGE,
            start_time=None, end_time=None, recency=None):
        """List time range performance data for given FE emulation.

        :param emulation_id: emulation id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.FE_EMU_ID: emulation_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.FE_EMU, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_frontend_port_keys(self, director_id, array_id=None):
        """List FE ports for the given array.

        :param director_id: array id -- str
        :param array_id: director id -- str
        :returns: FE port info with first and last available dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(
            category=pc.FE_PORT, array_id=array_id, director_id=director_id)
        return key_list.get(pc.FE_PORT_INFO, list()) if key_list else list()

    def get_frontend_port_stats(
            self, director_id, port_id, metrics, array_id=None,
            data_format=pc.AVERAGE, start_time=None, end_time=None,
            recency=None):
        """List time range performance data for given FE port.

        :param director_id: director id -- str
        :param port_id: port id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.DIR_ID: director_id, pc.PORT_ID: port_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.FE_PORT, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_ficon_emulation_keys(self, array_id=None):
        """List FICON emulations for the given array.

        :param array_id: array id -- str
        :returns: FICON emulation info with first and last available
                  dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(
            category=pc.FICON_EMU, array_id=array_id)
        return key_list.get(pc.FICON_EMU_INFO, list()) if key_list else list()

    def get_ficon_emulation_stats(
            self, ficon_emulation_id, metrics, array_id=None,
            data_format=pc.AVERAGE, start_time=None, end_time=None,
            recency=None):
        """List time range performance data for given FICON emulation.

        :param ficon_emulation_id: FICON emulation id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.FICON_EMU_ID: ficon_emulation_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.FICON_EMU, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_ficon_emulation_thread_keys(self, array_id=None):
        """List FICON emulation threads for the given array.

        :param array_id: array id -- str
        :returns: FICON emulation thread info with first and last available
                  dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(
            category=pc.FICON_EMU_THR, array_id=array_id)
        return key_list.get(
            pc.FICON_EMU_THR_INFO, list()) if key_list else list()

    def get_ficon_emulation_thread_stats(
            self, ficon_emulation_thread_id, metrics, array_id=None,
            data_format=pc.AVERAGE, start_time=None, end_time=None,
            recency=None):
        """List time range performance data for given FICON emulation thread.

        :param ficon_emulation_thread_id: FICON emulation thread id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.FICON_EMU_THR_ID: ficon_emulation_thread_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.FICON_EMU_THR,
            metrics=metrics, data_format=data_format,
            request_body=request_body, start_time=start_time,
            end_time=end_time, recency=recency)

    def get_ficon_port_thread_keys(self, array_id=None):
        """List FICON port threads for the given array.

        :param array_id: array id -- str
        :returns: FICON port info with first and last available dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(
            category=pc.FICON_PORT_THR, array_id=array_id)
        return key_list.get(
            pc.FICON_PORT_THR_INFO, list()) if key_list else list()

    def get_ficon_port_thread_stats(
            self, ficon_port_thread_id, metrics, array_id=None,
            data_format=pc.AVERAGE, start_time=None, end_time=None,
            recency=None):
        """List time range performance data for given FICON port thread.

        :param ficon_port_thread_id: FICON port thread id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.FICON_PORT_THR_ID: ficon_port_thread_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.FICON_PORT_THR, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_host_keys(self, array_id=None, start_time=None, end_time=None):
        """List active hosts for the given array by time range.

        Only active hosts from within the specified time range are returned. If
        no time range is provided, start and end times from array level are
        used.

        :param array_id: array id -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :returns: host info with first and last available dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        start_time, end_time = self.format_time_input(
            category=pc.ARRAY, array_id=array_id, start_time=start_time,
            end_time=end_time)
        key_list = self.get_performance_key_list(
            category=pc.HOST, array_id=array_id, start_time=start_time,
            end_time=end_time)
        return key_list.get(pc.HOST_INFO, list()) if key_list else list()

    def get_host_stats(
            self, host_id, metrics, array_id=None, data_format=pc.AVERAGE,
            start_time=None, end_time=None, recency=None):
        """List time range performance data for given host.

        Performance details will only be returned if the host was active during
        the specified time range. If no time range is provided, start and end
        times from array level are used.

        :param host_id: host id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        start_time, end_time = self.format_time_input(
            category=pc.ARRAY, array_id=array_id, start_time=start_time,
            end_time=end_time)
        request_body = {pc.HOST_ID: host_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.HOST, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_im_director_keys(self, array_id=None):
        """List IM directors for the given array.

        :param array_id: array id -- str
        :returns: IM directors with first and last available dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(category=pc.IM_DIR,
                                                 array_id=array_id)
        return key_list.get(pc.IM_DIR_INFO, list()) if key_list else list()

    def get_im_director_stats(
            self, director_id, metrics, array_id=None, data_format=pc.AVERAGE,
            start_time=None, end_time=None, recency=None):
        """List time range performance data for given IM director.

        :param director_id: director id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.DIR_ID: director_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.IM_DIR, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_im_emulation_keys(self, array_id=None):
        """List IM emulations for the given array.

        :param array_id: array id -- str
        :returns: IM emulation info with first and last available dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(category=pc.IM_EMU,
                                                 array_id=array_id)
        return key_list.get(pc.IM_EMU_INFO, list()) if key_list else list()

    def get_im_emulation_stats(
            self, emulation_id, metrics, array_id=None, data_format=pc.AVERAGE,
            start_time=None, end_time=None, recency=None):
        """List time range performance data for given IM emulation.

        :param emulation_id: emulation id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.IM_EMU_ID: emulation_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.IM_EMU, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_initiator_perf_keys(self, array_id=None, start_time=None,
                                end_time=None):
        """List active initiators for the given array by time range

        Only active initiators from within the specified time range are
        returned. If no time range is provided, start and end times from array
        level are used.

        :param array_id: array id -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :returns: host info with first and last available dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        start_time, end_time = self.format_time_input(
            category=pc.ARRAY, array_id=array_id, start_time=start_time,
            end_time=end_time)
        key_list = self.get_performance_key_list(
            category=pc.INIT, array_id=array_id, start_time=start_time,
            end_time=end_time)
        return key_list.get(pc.INIT_INFO, list()) if key_list else list()

    def get_initiator_stats(
            self, initiator_id, metrics, array_id=None, data_format=pc.AVERAGE,
            start_time=None, end_time=None, recency=None):
        """List time range performance data for given initiator.

        Performance details will only be returned if the initiator was active
        during the specified time range. If no time range is provided, start
        and end times from array level are used.

        :param initiator_id: initiator id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        start_time, end_time = self.format_time_input(
            category=pc.ARRAY, array_id=array_id, start_time=start_time,
            end_time=end_time)
        request_body = {pc.INIT_ID: initiator_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.INIT, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_ip_interface_keys(self, array_id=None):
        """List IP interfaces for the given array.

        :param array_id: array id -- str
        :returns: IP interface info with first and last available dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(category=pc.IP_INT,
                                                 array_id=array_id)
        return key_list.get(
            pc.ISCSI_CLIENT_INFO, list()) if key_list else list()

    def get_ip_interface_stats(
            self, ip_interface_id, metrics, array_id=None,
            data_format=pc.AVERAGE, start_time=None, end_time=None,
            recency=None):
        """List time range performance data for given IP interface.

        :param ip_interface_id: IP interface id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.IP_INT_ID: ip_interface_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.IP_INT, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_endpoint_keys(self, array_id=None):
        """List endpoints for the given array.

        :param array_id: array_id: array id -- str
        :returns: Endpoint info with first and last available
                  dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(category=pc.ENDPOINT,
                                                 array_id=array_id)
        return key_list.get(pc.ENDPOINT_INFO, list()) if key_list else list()

    def get_endpoint_stats(
            self, endpoint_id, metrics, array_id=None,
            data_format=pc.AVERAGE, start_time=None, end_time=None,
            recency=None):
        """List time range performance data for given iSCSI target.

        :param endpoint_id: iSCSI target id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.ENDPOINT_ID_METRICS: endpoint_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.ENDPOINT, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_masking_view_keys(self, array_id=None):
        """List masking views for the given array.

        :param array_id: array id -- str
        :returns: masking view info with first and last available dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(category=pc.MV,
                                                 array_id=array_id)
        return key_list.get(pc.MV_INFO, list()) if key_list else list()

    def get_masking_view_stats(
            self, masking_view_id, metrics, array_id=None,
            data_format=pc.AVERAGE, start_time=None, end_time=None,
            recency=None):
        """List time range performance data for given masking view.

        :param masking_view_id: masking view id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.MV_ID: masking_view_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.MV, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_port_group_keys(self, array_id=None):
        """List port group for the given array.

        :param array_id: array_id: array id -- str
        :returns: port group info with first and last available
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(category=pc.PG,
                                                 array_id=array_id)
        return key_list.get(pc.PG_INFO, list()) if key_list else list()

    def get_port_group_stats(
            self, port_group_id, metrics, array_id=None,
            data_format=pc.AVERAGE, start_time=None, end_time=None,
            recency=None):
        """List time range performance data for given port group.

        :param port_group_id: port group id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.PG_ID: port_group_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.PG, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_rdfa_keys(self, array_id=None):
        """List RDFA groups for the given array.

        :param array_id: array_id: array id -- str
        :returns: RDFA info with first and last available dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(category=pc.RDFA,
                                                 array_id=array_id)
        return key_list.get(pc.RDFA_INFO, list()) if key_list else list()

    def get_rdfa_stats(
            self, rdfa_group_id, metrics, array_id=None,
            data_format=pc.AVERAGE, start_time=None, end_time=None,
            recency=None):
        """List time range performance data for given RDFA group.

        :param rdfa_group_id: RDFA group id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.RA_GRP_INFO: rdfa_group_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.RDFA, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_rdfs_keys(self, array_id=None):
        """List RDFS groups for the given array.

        :param array_id: array_id: array id -- str
        :returns: RDFS info with first and last available dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(category=pc.RDFS,
                                                 array_id=array_id)
        return key_list.get(pc.RDFS_INFO, list()) if key_list else list()

    def get_rdfs_stats(
            self, rdfs_group_id, metrics, array_id=None,
            data_format=pc.AVERAGE, start_time=None, end_time=None,
            recency=None):
        """List time range performance data for given RDFS group.

        :param rdfs_group_id: RDFS group id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.RA_GRP_ID: rdfs_group_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.RDFS, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_rdf_director_keys(self, array_id=None):
        """List RDF directors for the given array.

        :param array_id: array id -- str
        :returns: RDF directors with first and last available dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(category=pc.RDF_DIR,
                                                 array_id=array_id)
        return key_list.get(pc.RDF_DIR_INFO, list()) if key_list else list()

    def get_rdf_director_stats(
            self, director_id, metrics, array_id=None,
            data_format=pc.AVERAGE, start_time=None, end_time=None,
            recency=None):
        """List time range performance data for given RDF director.

        :param director_id: director id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.DIR_ID: director_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.RDF_DIR, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_rdf_emulation_keys(self, array_id=None):
        """List RDF emulations for the given array.

        :param array_id: array id -- str
        :returns: RDF emulation info with first and last available
                  dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(category=pc.RDF_EMU,
                                                 array_id=array_id)
        return key_list.get(pc.RDF_EMU_INFO, list()) if key_list else list()

    def get_rdf_emulation_stats(
            self, emulation_id, metrics, array_id=None,
            data_format=pc.AVERAGE, start_time=None, end_time=None,
            recency=None):
        """List time range performance data for given RDF emulation.

        :param emulation_id: emulation id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.RDF_EMU_ID: emulation_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.RDF_EMU, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_rdf_port_keys(self, director_id, array_id=None):
        """List RDF ports for the given array.

        :param director_id: array id -- str
        :param array_id: director id -- str
        :returns: RDF port info with first and last available dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(
            category=pc.RDF_PORT, array_id=array_id,
            director_id=director_id)
        return key_list.get(pc.RDF_PORT_INFO, list()) if key_list else list()

    def get_rdf_port_stats(
            self, director_id, port_id, metrics, array_id=None,
            data_format=pc.AVERAGE, start_time=None, end_time=None,
            recency=None):
        """List time range performance data for given RDF port.

        :param director_id: director id -- str
        :param port_id: port id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.DIR_ID: director_id, pc.PORT_ID: port_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.RDF_PORT, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_sdnas_filesystem_keys(self, array_id=None):
        """List SDNAS Filesystems for the given array.

        :param array_id: array id -- str
        :returns: SDNAS Filesystem info with first and last available
                  dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(
            category=pc.SDNAS_FS, array_id=array_id)
        return key_list.get(
            pc.SDNAS_FS_INFO, list()) if key_list else list()

    def get_sdnas_filesystem_stats(
            self, sdnas_filesystem_id, metrics, array_id=None,
            data_format=pc.AVERAGE, start_time=None, end_time=None,
            recency=None):
        """List time range performance data for given SDNAS Filesystem.

        :param sdnas_filesystem_id: SDNAS Filesystem id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.SDNAS_FS_ID: sdnas_filesystem_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.SDNAS_FS, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_sdnas_interface_keys(self, array_id=None):
        """List SDNAS Interfaces for the given array.

        :param array_id: array id -- str
        :returns: SDNAS Interface info with first and last available
                  dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(
            category=pc.SDNAS_INTERFACE, array_id=array_id)
        return key_list.get(
            pc.SDNAS_INTERFACE_INFO, list()) if key_list else list()

    def get_sdnas_interface_stats(
            self, sdnas_interface_id, metrics, array_id=None,
            data_format=pc.AVERAGE, start_time=None, end_time=None,
            recency=None):
        """List time range performance data for given SDNAS Interface.

        :param sdnas_interface_id: SDNAS Interface id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.SDNAS_INTERFACE_ID: sdnas_interface_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.SDNAS_INTERFACE, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_sdnas_node_keys(self, array_id=None):
        """List SDNAS Nodes for the given array.

        :param array_id: array id -- str
        :returns: SDNAS Interface info with first and last available
                  dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(
            category=pc.SDNAS_NODE, array_id=array_id)
        return key_list.get(
            pc.SDNAS_NODE_INFO, list()) if key_list else list()

    def get_sdnas_node_stats(
            self, sdnas_node_id, metrics, array_id=None,
            data_format=pc.AVERAGE, start_time=None, end_time=None,
            recency=None):
        """List time range performance data for given SDNAS Node.

        :param sdnas_node_id: SDNAS Node id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.SDNAS_NODE_ID: sdnas_node_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.SDNAS_NODE, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_sdnas_server_keys(self, array_id=None):
        """List SDNAS Servers for the given array.

        :param array_id: array id -- str
        :returns: SDNAS Interface info with first and last available
                  dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(
            category=pc.SDNAS_SERVER, array_id=array_id)
        return key_list.get(
            pc.SDNAS_SERVER_INFO, list()) if key_list else list()

    def get_sdnas_server_stats(
            self, sdnas_server_id, metrics, array_id=None,
            data_format=pc.AVERAGE, start_time=None, end_time=None,
            recency=None):
        """List time range performance data for given SDNAS Server.

        :param sdnas_server_id: SDNAS Server id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.SDNAS_SERVER_ID: sdnas_server_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.SDNAS_SERVER, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_storage_container_keys(self, array_id=None):
        """List storage containers for the given array.

        :param array_id: array id -- str
        :returns: storage container info with first and last available
                  dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(
            category=pc.STORAGE_CONT, array_id=array_id)
        return key_list.get(
            pc.STORAGE_CONT_INFO, list()) if key_list else list()

    def get_storage_container_stats(
            self, storage_container_id, metrics, array_id=None,
            data_format=pc.AVERAGE, start_time=None, end_time=None,
            recency=None):
        """List time range performance data for given storage container.

        :param storage_container_id: storage container id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.STORAGE_CONT_ID: storage_container_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.STORAGE_CONT, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_storage_group_keys(self, array_id=None):
        """List storage groups for the given array.

        :param array_id: array id -- str
        :returns: storage container info with first and last available
                  dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(
            category=pc.SG, array_id=array_id)
        return key_list.get(pc.SG_INFO, list()) if key_list else list()

    def get_storage_group_stats(
            self, storage_group_id, metrics, array_id=None,
            data_format=pc.AVERAGE, start_time=None, end_time=None,
            recency=None):
        """List time range performance data for given storage group.

        :param storage_group_id: storage group id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.SG_ID: storage_group_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.SG, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_storage_resource_pool_keys(self, array_id=None):
        """List storage resource pools for the given array.

        :param array_id: array id -- str
        :returns: storage resource pool info with first and last available
                  dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(
            category=pc.SRP, array_id=array_id)
        return key_list.get(pc.SRP_INFO, list()) if key_list else list()

    def get_storage_resource_pool_stats(
            self, srp_id, metrics, array_id=None, data_format=pc.AVERAGE,
            start_time=None, end_time=None, recency=None):
        """List time range performance data for given storage resource pools.

        :param srp_id: storage resource pool id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.SRP_ID: srp_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.SRP, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_storage_resource_keys(self, array_id=None):
        """List storage resources for the given array.

        :param array_id: array id -- str
        :returns: storage resource info with first and last available
                  dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(
            category=pc.STORAGE_RES, array_id=array_id)
        return key_list.get(
            pc.STORAGE_RES_INFO, list()) if key_list else list()

    def get_storage_resource_stats(
            self, storage_container_id, storage_resource_id, metrics,
            array_id=None, data_format=pc.AVERAGE,
            start_time=None, end_time=None, recency=None):
        """List time range performance data for given storage resource.

        :param storage_container_id: storage container id -- str
        :param storage_resource_id: storage resource id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.STORAGE_CONT_ID: storage_container_id,
                        pc.STORAGE_RES_ID: storage_resource_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.STORAGE_RES, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_thin_pool_keys(self, array_id=None):
        """List thin pools for the given array.

        :param array_id: array id -- str
        :returns: thin pools with first and last available dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(
            category=pc.THIN_POOL, array_id=array_id)
        return key_list.get(pc.POOL_INFO, list()) if key_list else list()

    def get_thin_pool_stats(
            self, thin_pool_id, metrics, array_id=None, data_format=pc.AVERAGE,
            start_time=None, end_time=None, recency=None):
        """List time range performance data for given thin pool.

        :param thin_pool_id: thin pool id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.POOL_ID: thin_pool_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.THIN_POOL, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_volume_stats(
            self, array_id=None, volume_range_start=None,
            volume_range_end=None, storage_group_list=None,
            metrics=None, start_time=None, end_time=None, recency=None,
            data_format=None):
        """List Performance data for volume level statistics.

        Note: This function can gather statistics for up to 10,000 volumes
        or 100 Storage groups per call, time range can not exceed 1 hour/60
        minutes.  If Maximum values are required you will need to ensure the
        array is registered for both realtime and diagnostic data and
        storage groups are registered for realtime data collection using
        function enable_real_time_data_collection().

        :param volume_range_start: 5 digit device id of first device in range
                                   -- str
        :param volume_range_end: 5 digit device id of last device in range
                                   -- str
        :param storage_group_list: list of up to 100 storage groups
                                   -- str or list
        :param metrics: performance metrics to retrieve, if not specified
               all available metrics will return by default-- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        if not metrics:

            metrics = (self.get_performance_metrics_list(
                category=pc.VOLUME, kpi_only=False))
        if volume_range_start and volume_range_end:
            request_body = {
                "systemId": array_id,
                "volumeStartRange": volume_range_start,
                "volumeEndRange": volume_range_end,

            }
        else:
            if type(storage_group_list) is list:
                storage_group_list = ",".join(storage_group_list)
            request_body = {
                "systemId": array_id,
                "commaSeparatedStorageGroupList": storage_group_list}

        return self.get_performance_stats(
            category=pc.VOLUME, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_zhyperlink_port_keys(self, array_id=None):
        """List zHyperLink Ports for the given array.

        :param array_id: array id -- str
        :returns: thin pools with first and last available dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(
            category=pc.ZHYPER_LINK_PORT, array_id=array_id)
        return key_list.get(
            pc.ZHYPER_LINK_PORT_INFO, list()) if key_list else list()

    def get_zhyperlink_port_stats(
            self, zhyperlink_port_id, metrics, array_id=None,
            data_format=pc.AVERAGE, start_time=None, end_time=None,
            recency=None):
        """List time range performance data for given zHyperLink Port.

        :param zhyperlink_port_id: zHyperLink Port id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.PORT_ID: zhyperlink_port_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.ZHYPER_LINK_PORT, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)
