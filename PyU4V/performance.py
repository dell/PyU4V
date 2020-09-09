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
"""performance.py."""

import copy
import logging
import re
import time

from PyU4V import common
from PyU4V.utils import constants
from PyU4V.utils import decorators
from PyU4V.utils import exception
from PyU4V.utils import file_handler
from PyU4V.utils import performance_category_map
from PyU4V.utils import performance_constants as pc

LOG = logging.getLogger(__name__)
CATEGORY_MAP = performance_category_map.performance_data


class PerformanceFunctions(object):
    """PerformanceFunctions."""

    def __init__(self, array_id, rest_client):
        """__init__."""
        self.common = common.CommonFunctions(rest_client)
        self.post_request = self.common.create_resource
        self.get_request = self.common.get_resource
        self.put_request = self.common.modify_resource
        self.array_id = array_id
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

    def is_array_performance_registered(self, array_id=None):
        """Check if an array is registered for diagnostic performance data.

        This will return False is an array is registered for real-time data but
        not for diagnostic performance data.

        :param array_id: array id -- str
        :returns: bool
        """
        array_id = self.array_id if not array_id else array_id
        registration_details = dict()
        response = self.get_request(
            category=pc.PERFORMANCE, resource_level=pc.ARRAY,
            resource_type=pc.REG_DETAILS, resource_type_id=array_id)
        if response.get(pc.REG_DETAILS_INFO):
            registration_details = response.get(pc.REG_DETAILS_INFO)[0]
        return registration_details.get(pc.REG_DIAGNOSTIC, False) if (
            registration_details) else False

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
            request_body[pc.SYMM_ID] = array_id
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

        cat = CATEGORY_MAP.get(category.upper())
        if cat:
            request = self.get_request if pc.ARRAY in cat[pc.CATEGORY] else (
                self.post_request)
            return request(
                category=pc.PERFORMANCE, resource_level=cat[pc.CATEGORY],
                resource_type=pc.KEYS, payload=request_body)
        else:
            raise exception.InvalidInputException(
                'Key list extraction failed due to invalid category "{cat}", '
                'please correct the category name before trying '
                'again.'.format(cat=category))

    @staticmethod
    def get_performance_categories_list():
        """Get the list of supported performance categories.

        :returns: categories -- list
        """
        categories = list()
        for cat in CATEGORY_MAP:
            category_info = CATEGORY_MAP.get(cat)
            categories.append(category_info[pc.CATEGORY])
        return categories

    @staticmethod
    def validate_category(category):
        """Check that a supplied category is valid.

        :raises: InvalidInputException
        """
        if category.upper() not in CATEGORY_MAP:
            raise exception.InvalidInputException(
                'Invalid category "{cat}" supplied, please correct the '
                'supplied category and try again.'.format(cat=category))

    @staticmethod
    def get_performance_metrics_list(category, kpi_only=False):
        """For a given category, return the list of valid metrics.

        :param category: performance category -- str
        :param kpi_only: if only KPI metrics should be returned -- bool
        :returns: metrics -- list
        """
        if CATEGORY_MAP.get(category.upper()):
            user_cat = CATEGORY_MAP.get(category.upper())
            kpi_list = user_cat[pc.METRICS_KPI] if kpi_only else (
                user_cat[pc.METRICS_ALL])
            return kpi_list
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

        # 2. Format Time input - request body input need to retrieve object
        # specific timestamps
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

        start_time, end_time = self.format_time_input(
            array_id=array_id, category=category, director_id=director_id,
            key_tgt_id=object_id, start_time=start_time, end_time=end_time)

        # 3. Check recency
        if recency:
            recency = recency if isinstance(recency, int) else self.recency

            if not self.is_timestamp_current(int(end_time), minutes=recency):
                raise exception.VolumeBackendAPIException(
                    'Timestamp failed recency check of {rec} '
                    'minutes.'.format(rec=recency))

        # 4. Format Metrics
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

        # 5. Set data format
        if data_format.upper() not in [pc.AVERAGE.upper(), pc.MAXIMUM.upper()]:
            raise exception.InvalidInputException(
                'Invalid data format "{f}" specified, please use one of '
                'Average or Maximum'.format(f=data_format))

        if pc.MAXIMUM.upper() in data_format.upper():
            data_format = pc.MAXIMUM
        else:
            data_format = pc.AVERAGE

        # Add asset IDs to the return dict before additional key/values added
        if request_body:
            for k, v in request_body.items():
                key = self.common.convert_to_snake_case(k)
                performance_details[key] = v

        # 6. Set request body
        request_body[pc.START_DATE] = start_time
        request_body[pc.END_DATE] = end_time
        request_body[pc.SYMM_ID] = str(array_id)
        request_body[pc.DATA_FORMAT] = str(data_format)
        request_body[pc.METRICS] = metrics_list

        # 7. Post Request
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

    @decorators.refactoring_notice(
        'PyU4V.performance', 'PyU4V.performance.get_threshold_categories',
        9.1, 9.3)
    def get_perf_threshold_categories(self):
        """Get a list of performance threshold categories.

        This call is being refactored in favour of
        performance.get_threshold_categories().

        :returns: performance threshold categories -- list
        """
        return self.get_threshold_categories()

    def get_threshold_categories(self):
        """Get a list of performance threshold categories.

        :returns: performance threshold categories -- list
        """
        categories = self.get_request(
            category=pc.PERFORMANCE, resource_level=pc.THRESHOLD,
            resource_type=pc.CATEGORIES)
        return categories.get(pc.THRESH_CAT, list()) if categories else list()

    @decorators.refactoring_notice(
        'PyU4V.performance',
        'PyU4V.performance.get_category_threshold_settings', 9.1, 9.3)
    def get_perf_category_threshold_settings(self, category):
        """Get performance threshold category settings.

        This call is being refactored in favour of
        performance.get_threshold_category_settings().

        :param category: category id -- str
        :returns: category settings --  dict
        """
        return self.get_threshold_category_settings(category)

    def get_threshold_category_settings(self, category):
        """Get performance threshold category settings.

        :param category: category id -- str
        :returns: category settings --  dict
        """
        return self.get_request(
            category=pc.PERFORMANCE, resource_level=pc.THRESHOLD,
            resource_type=pc.LIST, resource_type_id=category)

    @decorators.refactoring_notice(
        'PyU4V.performance', 'PyU4V.performance.update_threshold', 9.1, 9.3)
    def set_perf_threshold_and_alert(
            self, category, metric, firstthreshold, secondthreshold, notify):
        """Set performance thresholds and alerts.

        This call is being refactored in favour of
        performance.update_threshold_settings().

        Function to set performance alerts, suggested use with CSV file to
        get parameter settings from user template. Set to check for 3 out of 5
        samples before returning alert, if users need more control use
        performance.update_threshold_settings().

        :param category: category id -- str
        :param metric: performance metric -- str
        :param firstthreshold: first threshold -- int
        :param secondthreshold: second threshold -- int
        :param notify: notify user with alert -- bool
        :returns: operation success details -- dict
        """
        return self.update_threshold_settings(
            category=category, metric=metric, alert=notify,
            first_threshold=str(firstthreshold),
            second_threshold=str(secondthreshold),
            first_threshold_occurrences=3, first_threshold_samples=5,
            first_threshold_severity=pc.WARN_LVL,
            second_threshold_occurrences=3, second_threshold_samples=5,
            second_threshold_severity=pc.CRIT_LVL)

    def update_threshold_settings(
            self, category, metric, first_threshold, second_threshold,
            alert=True, first_threshold_occurrences=3,
            first_threshold_samples=5,
            first_threshold_severity=pc.WARN_LVL,
            second_threshold_occurrences=3, second_threshold_samples=5,
            second_threshold_severity=pc.CRIT_LVL):
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
        :returns: operation success details -- dict
        """
        payload = dict()
        payload[pc.METRIC] = metric
        payload[pc.ALERT] = alert
        payload[pc.FIRST_THRESH] = str(first_threshold)
        payload[pc.FIRST_THRESH_OCC] = str(first_threshold_occurrences)
        payload[pc.FIRST_THRESH_SAMP] = str(first_threshold_samples)
        payload[pc.FIRST_THRESH_SEV] = first_threshold_severity
        payload[pc.SEC_THRESH] = str(second_threshold)
        payload[pc.SEC_THRESH_OCC] = str(second_threshold_occurrences)
        payload[pc.SEC_THRESH_SAMP] = str(second_threshold_samples)
        payload[pc.SEC_THRESH_SEV] = second_threshold_severity

        return self.put_request(
            category=pc.PERFORMANCE, resource_level=pc.THRESHOLD,
            resource_type=pc.UPDATE, resource_type_id=category,
            payload=payload)

    def generate_threshold_settings_csv(self, output_csv_path):
        """Generate a csv file with threshold settings.

        Creates a CSV file with current alert configuration for the given
        unisphere instance category, metric, first_threshold, second_threshold,
        alert_user, kpi.

        :param output_csv_path: filename for CSV to be generated -- str
        """
        category_list = self.get_threshold_categories()
        data_for_csv = list()
        data_for_csv.append([pc.CATEGORY, pc.METRIC, pc.FIRST_THRESH,
                             pc.SEC_THRESH, pc.ALERT_ERR, pc.KPI])
        for category in category_list:
            metric_setting = self.get_threshold_category_settings(category)
            threshold_settings = metric_setting.get(pc.PERF_THRESH)
            for threshold in threshold_settings:
                data_for_csv.append([
                    category, threshold.get(pc.METRIC),
                    int(threshold.get(pc.FIRST_THRESH)),
                    int(threshold.get(pc.SEC_THRESH)),
                    threshold.get(pc.ALERT_ERR), threshold.get(pc.KPI)])
        file_handler.write_to_csv_file(output_csv_path, data_for_csv)

    @decorators.refactoring_notice(
        'PyU4V.performance', 'PyU4V.performance.update_threshold', 9.1, 9.3)
    def set_perfthresholds_csv(self, csvfilename):
        """Set performance thresholds using a CSV file.

        This call is being refactored in favour of
        performance.set_thresholds_from_csv().

        :param csvfilename: the path to the csv file
        """
        self.set_thresholds_from_csv(csvfilename)

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
            self.update_threshold_settings(
                category=category_list[i], metric=metric_list[i],
                alert=notify_list[i], first_threshold=f_threshold_list[i],
                second_threshold=s_threshold_list[i])

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

    def get_core_keys(self, array_id=None):
        """List cores for the given array.

        :param array_id: array id -- str
        :returns: core info with first and last available dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(category=pc.CORE,
                                                 array_id=array_id)
        return key_list.get(pc.CORE_INFO, list()) if key_list else list()

    def get_core_stats(
            self, core_id, metrics, array_id=None, data_format=pc.AVERAGE,
            start_time=None, end_time=None, recency=None):
        """List time range performance data for given core.

        :param core_id: core id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.CORE_ID: core_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.CORE, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_database_keys(self, array_id=None):
        """List databases for the given array.

        :param array_id: array id -- str
        :returns: database info with first and last available dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(category=pc.DB,
                                                 array_id=array_id)
        return key_list.get(pc.DB_INFO, list()) if key_list else list()

    def get_database_stats(
            self, database_id, metrics, array_id=None, data_format=pc.AVERAGE,
            start_time=None, end_time=None, recency=None):
        """List time range performance data for given database.

        :param database_id: database id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.DB_ID: database_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.DB, metrics=metrics,
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

    def get_disk_keys(self, array_id=None):
        """List disks for the given array.

        :param array_id: array id -- str
        :returns: disk info with first and last available dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(category=pc.DISK,
                                                 array_id=array_id)
        return key_list.get(pc.DISK_INFO, list()) if key_list else list()

    def get_disk_stats(
            self, disk_id, metrics, array_id=None, data_format=pc.AVERAGE,
            start_time=None, end_time=None, recency=None):
        """List time range performance data for given disk.

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
            array_id=array_id, category=pc.DISK, metrics=metrics,
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

    def get_disk_technology_pool_keys(self, array_id=None):
        """List disk technology pools for the given array.

        :param array_id: array id -- str
        :returns: disk technology pool info with first and last available
                  dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(category=pc.DISK_TECH_POOL,
                                                 array_id=array_id)
        return key_list.get(
            pc.DISK_TECH_POOL_INFO, list()) if key_list else list()

    def get_disk_technology_pool_stats(
            self, disk_tech_id, metrics, array_id=None,
            data_format=pc.AVERAGE, start_time=None, end_time=None,
            recency=None):
        """List time range performance data for given disk technology.

        :param disk_tech_id: disk technology id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.DISK_TECH: disk_tech_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.DISK_TECH_POOL, metrics=metrics,
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

    def get_external_director_keys(self, array_id=None):
        """List external directors for the given array.

        :param array_id: array id -- str
        :returns: external directors with first and last available
                  dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(category=pc.EXT_DIR,
                                                 array_id=array_id)
        return key_list.get(pc.EXT_DIR_INFO, list()) if key_list else list()

    def get_external_director_stats(
            self, director_id, metrics, array_id=None,
            data_format=pc.AVERAGE, start_time=None, end_time=None,
            recency=None):
        """List time range performance data for given external director.

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
            array_id=array_id, category=pc.EXT_DIR, metrics=metrics,
            data_format=data_format, request_body=request_body,
            start_time=start_time, end_time=end_time, recency=recency)

    def get_external_disk_keys(self, array_id=None):
        """List external disks for the given array.

        :param array_id: array id -- str
        :returns: external disks with first and last available dates -- list
        """
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

    def get_external_disk_group_keys(self, array_id=None):
        """List external disk groups for the given array.

        :param array_id: array id -- str
        :returns: external disk groups with first and last available
                  dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(category=pc.EXT_DISK_GRP,
                                                 array_id=array_id)
        return key_list.get(
            pc.EXT_DISK_GRP_INFO, list()) if key_list else list()

    def get_external_disk_group_stats(
            self, disk_group_id, metrics, array_id=None,
            data_format=pc.AVERAGE, start_time=None, end_time=None,
            recency=None):
        """List time range performance data for given external disk group.

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
            array_id=array_id, category=pc.EXT_DISK_GRP, metrics=metrics,
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

    def get_initiator_by_port_keys(
            self, array_id=None, start_time=None, end_time=None):
        """List active initiators by port for the given array by time range

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
            category=pc.INIT_BY_PORT, array_id=array_id,
            start_time=start_time, end_time=end_time)
        return key_list.get(
            pc.INIT_BY_PORT_INFO, list()) if key_list else list()

    def get_initiator_by_port_stats(
            self, initiator_by_port_id, metrics, array_id=None,
            data_format=pc.AVERAGE, start_time=None, end_time=None,
            recency=None):
        """List time range performance data for given initiator.

        Performance details will only be returned if the initiator was active
        during the specified time range. If no time range is provided, start
        and end times from array level are used.

        :param initiator_by_port_id: initiator by port id -- str
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
        request_body = {pc.INIT_BY_PORT_ID: initiator_by_port_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.INIT_BY_PORT, metrics=metrics,
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

    def get_iscsi_target_keys(self, array_id=None):
        """List iSCSI targets for the given array.

        :param array_id: array_id: array id -- str
        :returns: iSCSI interfaces info with first and last available
                  dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        key_list = self.get_performance_key_list(category=pc.ISCSI_TGT,
                                                 array_id=array_id)
        return key_list.get(pc.ISCSI_TGT_INFO, list()) if key_list else list()

    def get_iscsi_target_stats(
            self, iscsi_target_id, metrics, array_id=None,
            data_format=pc.AVERAGE, start_time=None, end_time=None,
            recency=None):
        """List time range performance data for given iSCSI target.

        :param iscsi_target_id: iSCSI target id -- str
        :param metrics: performance metrics to retrieve -- str or list
        :param array_id: array id -- str
        :param data_format: response data format 'Average' or 'Maximum' -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :param recency: check recency of timestamp in minutes -- int
        :returns: performance metrics -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {pc.ISCSI_TGT_ID_METRICS: iscsi_target_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.ISCSI_TGT, metrics=metrics,
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

    def get_storage_group_by_pool_keys(self, storage_group_id, array_id=None,
                                       start_time=None, end_time=None):
        """List storage groups by thin pool for the given array by time range.

        Only active pools from within the specified time range are returned. If
        no time range is provided, start and end times from array level are
        used.

        :param storage_group_id: storage group id -- str
        :param array_id: array id -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :returns: pool info with first and last available dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        start_time, end_time = self.format_time_input(
            category=pc.ARRAY, array_id=array_id, start_time=start_time,
            end_time=end_time)
        key_list = self.get_performance_key_list(
            category=pc.SG_BY_POOL, array_id=array_id,
            storage_group_id=storage_group_id,
            start_time=start_time, end_time=end_time)
        return key_list.get(pc.POOL_INFO, list()) if key_list else list()

    def get_storage_group_by_pool_stats(
            self, storage_group_id, pool_id, metrics, array_id=None,
            data_format=pc.AVERAGE, start_time=None, end_time=None,
            recency=None):
        """List time range performance data for given storage group by pool.

        Performance details will only be returned if the storage was active
        during the specified time range. If no time range is provided, start
        and end times from array level are used.

        :param storage_group_id: storage group id -- str
        :param pool_id: pool id -- str
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
        request_body = {pc.SG_ID: storage_group_id, pc.POOL_ID: pool_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.SG_BY_POOL,
            metrics=metrics, data_format=data_format,
            request_body=request_body, start_time=start_time,
            end_time=end_time, recency=recency)

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

    def get_storage_resource_by_pool_keys(
            self, storage_container_id, storage_resource_id, array_id=None,
            start_time=None, end_time=None):
        """List storage resource by pool for the given array by time range.

        Only active pools from within the specified time range are returned. If
        no time range is provided, start and end times from array level are
        used.

        :param storage_container_id: storage container id -- str
        :param storage_resource_id: storage resource id -- str
        :param array_id: array id -- str
        :param start_time: timestamp in milliseconds since epoch -- str
        :param end_time: timestamp in milliseconds since epoch -- str
        :returns: pool info with first and last available dates -- list
        """
        array_id = self.array_id if not array_id else array_id
        start_time, end_time = self.format_time_input(
            category=pc.ARRAY, array_id=array_id, start_time=start_time,
            end_time=end_time)
        key_list = self.get_performance_key_list(
            category=pc.STORAGE_RES_BY_POOL, array_id=array_id,
            storage_container_id=storage_container_id,
            storage_resource_id=storage_resource_id, start_time=start_time,
            end_time=end_time)
        return key_list.get(pc.POOL_INFO, list()) if key_list else list()

    def get_storage_resource_by_pool_stats(
            self, storage_container_id, storage_resource_id,
            metrics, array_id=None, data_format=pc.AVERAGE,
            start_time=None, end_time=None, recency=None):
        """List time range performance data for given storage resource.

        Performance details will only be returned if the pool was active
        during the specified time range. If no time range is provided, start
        and end times from array level are used.

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
        start_time, end_time = self.format_time_input(
            category=pc.ARRAY, array_id=array_id, start_time=start_time,
            end_time=end_time)
        request_body = {pc.STORAGE_CONT_ID: storage_container_id,
                        pc.STORAGE_RES_ID: storage_resource_id}
        return self.get_performance_stats(
            array_id=array_id, category=pc.STORAGE_RES_BY_POOL,
            metrics=metrics,
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

    @decorators.refactoring_notice(
        'PyU4V.performance', 'PyU4V.performance.get_frontend_director_keys',
        9.1, 9.3)
    def get_fe_director_list(self):
        """Get list of all FE Directors.

        :returns: all FE directors -- list
        """
        dir_list = list()
        response = self.get_frontend_director_keys(array_id=self.array_id)
        for director in response:
            dir_list.append(director.get(pc.DIR_ID))
        return dir_list

    @decorators.refactoring_notice(
        'PyU4V.performance', 'PyU4V.performance.get_frontend_port_keys',
        9.1, 9.3)
    def get_fe_port_list(self):
        """Get a list of all front end ports in the array.

        :returns: all FE directors and ports -- list
        """
        port_list = list()
        dir_list = self.get_fe_director_list()
        for director in dir_list:
            director_ports = dict()
            response = self.get_frontend_port_keys(
                array_id=self.array_id, director_id=director)
            for port in response:
                director_ports[port.get(pc.PORT_ID)] = director
            port_list.append(director_ports)
        return port_list

    @decorators.deprecation_notice('PyU4V.performance', 9.1, 9.3)
    def get_fe_port_util_last4hrs(self, dir_id, port_id):
        """Get FE port percent busy stats for last 4 hours.

        :param dir_id: director id -- str
        :param port_id: port id -- str
        :returns: port details -- dict
        """
        start_time, end_time = self.get_timestamp_by_hour(hours_difference=4)
        return self.get_frontend_port_stats(
            array_id=self.array_id, director_id=dir_id, port_id=port_id,
            metrics='PercentBusy', start_time=start_time, end_time=end_time)

    @decorators.refactoring_notice(
        'PyU4V.performance', 'PyU4V.performance.get_frontend_director_stats',
        9.1, 9.3)
    def get_fe_director_metrics(self, start_date, end_date,
                                director, dataformat=pc.AVERAGE):
        """Get one or more metrics for front end directors.

        :param start_date: timestamp in milliseconds since epoch -- str
        :param end_date: timestamp in milliseconds since epoch -- str
        :param director: FE director -- str
        :param dataformat: pc.AVERAGE, 'Maximum' -- str
        :returns: performance data -- dict
        """
        return self.get_frontend_director_stats(
            array_id=self.array_id, director_id=director, metrics=pc.KPI,
            start_time=start_date, end_time=end_date, data_format=dataformat)

    @decorators.refactoring_notice(
        'PyU4V.performance', 'PyU4V.performance.get_frontend_port_stats',
        9.1, 9.3)
    def get_fe_port_metrics(self, start_date, end_date, director_id,
                            port_id, dataformat, metriclist):
        """Get one or more metrics for front end director ports.

        :param start_date: timestamp in milliseconds since epoch -- str
        :param end_date: timestamp in milliseconds since epoch -- str
        :param director_id: director id -- str
        :param port_id: port id -- str
        :param dataformat: 'Average', 'Maximum' -- str
        :param metriclist: performance metrics -- list
        :returns: performance data -- dict
        """
        return self.get_frontend_port_stats(
            array_id=self.array_id, director_id=director_id, port_id=port_id,
            metrics=metriclist, data_format=dataformat, start_time=start_date,
            end_time=end_date)

    @decorators.refactoring_notice(
        'PyU4V.performance', 'PyU4V.performance.get_array_stats', 9.1, 9.3)
    def get_array_metrics(self, start_date, end_date, array_id=None):
        """Get array performance information.

        :param start_date: timestamp in milliseconds since epoch -- str
        :param end_date: timestamp in milliseconds since epoch -- str
        :param array_id: array id -- str
        :returns: performance details -- dict
        """
        array_id = self.array_id if not array_id else array_id
        return self.get_array_stats(
            array_id=array_id, start_time=start_date, end_time=end_date,
            metrics=pc.KPI)

    @decorators.refactoring_notice(
        'PyU4V.performance', 'PyU4V.performance.get_storage_group_stats',
        9.1, 9.3)
    def get_storage_group_metrics(self, sg_id, start_date, end_date):
        """Get storage group performance information.

        :param sg_id: storage group id -- str
        :param start_date: timestamp in milliseconds since epoch -- str
        :param end_date: timestamp in milliseconds since epoch -- str
        :returns: performance details -- dict
        """
        return self.get_storage_group_stats(
            array_id=self.array_id, storage_group_id=sg_id, metrics=pc.KPI,
            start_time=start_date, end_time=end_date)

    @decorators.deprecation_notice('PyU4V.performance', 9.1, 9.3)
    def get_all_fe_director_metrics(self, start_date, end_date):
        """Get performance information of all front end directors.

        :param start_date: EPOCH Time in Milliseconds -- str
        :param end_date: EPOCH Time in Milliseconds -- str
        :returns: sg performance details -- dict
        """
        dir_list = self.get_fe_director_list()
        all_directors = list()
        for fe_director in dir_list:
            all_directors.append(self.get_frontend_director_stats(
                array_id=self.array_id, director_id=fe_director,
                metrics=pc.KPI, start_time=start_date, end_time=end_date))
        return all_directors

    @decorators.deprecation_notice('PyU4V.performance', 9.1, 9.3)
    def get_director_info(self, director_id, start_date, end_date):
        """Get director performance information.

        :param director_id: director id -- str
        :param start_date: timestamp in milliseconds since epoch -- str
        :param end_date: timestamp in milliseconds since epoch -- str
        :returns: performance details -- dict
        """
        director_type = ''
        perf_metrics_payload = dict()
        if any(x in director_id for x in pc.BE_DIR_TAGS):
            perf_metrics_payload = self.get_backend_director_stats(
                array_id=self.array_id, director_id=director_id,
                metrics=pc.KPI, start_time=start_date, end_time=end_date)
            director_type = 'BE'

        elif any(x in director_id for x in pc.FE_DIR_TAGS):
            perf_metrics_payload = self.get_frontend_director_stats(
                array_id=self.array_id, director_id=director_id,
                metrics=pc.KPI, start_time=start_date, end_time=end_date)
            director_type = 'FE'

        elif any(x in director_id for x in pc.RDF_DIR_TAGS):
            perf_metrics_payload = self.get_rdf_director_stats(
                array_id=self.array_id, director_id=director_id,
                metrics=pc.KPI, start_time=start_date, end_time=end_date)
            director_type = 'RDF'

        elif any(x in director_id for x in pc.IM_DIR_TAGS):
            perf_metrics_payload = self.get_im_director_stats(
                array_id=self.array_id, director_id=director_id,
                metrics=pc.KPI, start_time=start_date, end_time=end_date)
            director_type = 'IM'

        elif any(x in director_id for x in pc.EDS_DIR_TAGS):
            perf_metrics_payload = self.get_eds_director_stats(
                array_id=self.array_id, director_id=director_id,
                metrics=pc.KPI, start_time=start_date, end_time=end_date)
            director_type = 'EDS'

        # Get director info level data...
        director_info = self.get_request(
            category=constants.SYSTEM,
            resource_level=constants.SYMMETRIX,
            resource_level_id=self.array_id,
            resource_type=constants.DIRECTOR, resource_type_id=director_id)

        for k, v in director_info.items():
            key = self.common.convert_to_snake_case(k)
            perf_metrics_payload[key] = v

        perf_metrics_payload['director_type'] = director_type

        return perf_metrics_payload

    @decorators.refactoring_notice(
        'PyU4V.performance', 'PyU4V.performance.get_port_group_stats',
        9.1, 9.3)
    def get_port_group_metrics(self, pg_id, start_date, end_date):
        """Get Port Group performance information.

        :param pg_id: port group id -- str
        :param start_date: timestamp in milliseconds since epoch -- str
        :param end_date: timestamp in milliseconds since epoch -- str
        :returns: port group performance details -- dict
        """
        return self.get_port_group_stats(
            array_id=self.array_id, port_group_id=pg_id, metrics=pc.KPI,
            start_time=start_date, end_time=end_date)

    @decorators.refactoring_notice(
        'PyU4V.performance', 'PyU4V.performance.get_host_stats', 9.1, 9.3)
    def get_host_metrics(self, host, start_date, end_date):
        """Get host performance information.

        :param host: host name -- str
        :param start_date: timestamp in milliseconds since epoch -- str
        :param end_date: timestamp in milliseconds since epoch -- str
        :returns: port group performance details -- dict
        """
        return self.get_host_stats(
            host_id=host, metrics=pc.KPI, array_id=self.array_id,
            start_time=start_date, end_time=end_date)
