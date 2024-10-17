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
"""real_time.py."""

import logging
import time

from PyU4V import common
from PyU4V.utils import exception
from PyU4V.utils import performance_constants as pc

LOG = logging.getLogger(__name__)


class RealTimeFunctions(object):
    """PerformanceFunctions."""

    def __init__(self, array_id, rest_client):
        """__init__."""
        self.common = common.CommonFunctions(rest_client)
        self.post_request = self.common.create_resource
        self.get_request = self.common.get_resource
        self.array_id = array_id
        self.recency = 0

    def set_array_id(self, array_id):
        """Set the array id.

        :param array_id: array id -- str
        """
        self.array_id = array_id

    def set_recency(self, minutes):
        """Set the recency value in minutes.

        :param minutes: recency minutes -- int
        """
        self.recency = int(minutes)

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

    def get_categories(self, array_id=None):
        """Get a list of real-time supported performance categories.

        :param array_id: array serial number -- str
        :returns: categories -- list
        """
        array_id = array_id if array_id else self.array_id
        response = self.get_request(
            no_version=True, category=pc.PERFORMANCE,
            resource_level=pc.REAL_TIME, resource_type=pc.HELP,
            resoruce=array_id, object_type=pc.CATEGORIES)
        return response.get(pc.CATEGORY_NAME, list()) if response else list()

    def get_category_metrics(self, category, array_id=None):
        """Get metrics available for a real-time performance category.

        :param category: real-time performance category -- str
        :param array_id: array serial number -- str
        :returns: metrics -- list
        """
        array_id = array_id if array_id else self.array_id
        response = self.get_request(
            no_version=True, category=pc.PERFORMANCE,
            resource_level=pc.REAL_TIME, resource_type=pc.HELP,
            resource_type_id=array_id, resource=category,
            object_type=pc.METRICS)
        return response.get(pc.METRIC_NAME, list()) if response else list()

    def get_timestamps(self, array_id=None):
        """Get real-time performance timestamps for array(s).

        :param array_id: array serial number -- str
        :returns: array timestamp info -- list
        """
        response = self.get_request(
            no_version=True, category=pc.PERFORMANCE,
            resource_level=pc.REAL_TIME, resource_type=pc.HELP,
            resource=pc.TIMES)
        timestamps = response.get(
            pc.ARRAY_INFO, list()) if response else list()

        if array_id and timestamps:
            for array_info in timestamps:
                if array_info.get(pc.SYMM_ID) == array_id:
                    return [array_info]

        return timestamps

    def get_category_keys(self, category, array_id=None):
        """Get category keys valid for real-time metrics collection.

        :param category: real-time performance category -- str
        :param array_id: array serial number -- str
        :returns: category keys -- list
        """
        array_id = self.array_id if not array_id else array_id
        request_params = {pc.SYMM_ID: array_id, pc.CATEGORY: category}
        try:
            response = self.post_request(
                no_version=True, category=pc.PERFORMANCE,
                resource_level=pc.REAL_TIME, resource_type=pc.KEYS,
                payload=request_params)
        except Exception as e:
            logging.error(f"Error in get_category_keys: {e}")
            return list()
        return response.get(pc.KEYS, list()) if response else list()

    def _validate_real_time_input(
            self, start_date, end_date, category, metrics, instance_id):
        """Validate user input for real-time metrics collection.

        :param start_date: timestamp in milliseconds since epoch -- int
        :param end_date: timestamp in milliseconds since epoch -- int
        :param category: category id -- str
        :param metrics: performance metrics -- list
        :param instance_id: instance id -- str
        :raises: VolumeBackendAPIException, InvalidInputException
        """
        delta, msg = end_date - start_date, None

        # Category validation
        if category not in self.get_categories():
            # Allow for no 's' at the end of StorageGroups, StorageGroup is
            # still valid but not returned in category list
            if category != pc.SG:
                msg = (
                    'Real-time performance category "{user_cat}" is not '
                    'one of {uni_cat}.'.format(
                        user_cat=category, uni_cat=self.get_categories()))

        # Metrics validation
        elif metrics != [pc.All_CAP] and not (
                all(metric in self.get_category_metrics(
                    category) for metric in metrics)):
            msg = (
                'The supplied real-time metrics {user_met} are not '
                'valid. Valid options are "All", and one or more of '
                '{uni_met}'.format(
                    user_met=metrics,
                    uni_met=self.get_category_metrics(category)))

        # Required input validation
        elif category != pc.ARRAY and not instance_id:
            msg = ('For real-time performance data other than from the '
                   '"Array" category an instance_id must be specified.')

        # Instance ID key validation against known real-time keys
        elif instance_id and instance_id not in self.get_category_keys(
                category=category):
            msg = (
                'Instance ID "{inst}" is not one of {cat} real-time '
                'performance keys {uni_keys}'.format(
                    inst=instance_id, cat=category,
                    uni_keys=self.get_category_keys(category=category)))

        # Timestamp validation
        elif not isinstance(end_date, int) or not isinstance(start_date, int):
            msg = ('Start and end dates must be of type <int> and in '
                   'milliseconds since epoch format.')
        elif delta < pc.ONE_MINUTE:
            ct, one_min = int(time.time()) * 1000, pc.ONE_MINUTE
            if (ct - end_date < one_min) or (ct - start_date < one_min):
                msg = ('Real-time timestamps cannot be for intervals of less '
                       'than one minute if the start or end timestamps are '
                       'within one minute of local time.')
        elif delta > pc.ONE_HOUR:
            msg = ('It is not possible to query for more than one hour of '
                   'real-time performance data in one request.')
        elif self.recency:
            if not self.is_timestamp_current(int(end_date), self.recency):
                msg = ('Timestamp "{t}" failed recency check of {rec} '
                       'minutes.'.format(t=end_date, rec=self.recency))

        if msg:
            LOG.error(msg)
            raise exception.InvalidInputException(msg)

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
            if metrics.lower() == pc.ALL:
                metrics = pc.All_CAP
            input_list = [metrics]
        elif isinstance(metrics, list):
            input_list = metrics
        else:
            msg = ('Unknown input parameter type, please pass in '
                   '<string> or <list> input type.')
            LOG.error(msg)
            raise exception.InvalidInputException(msg)
        return input_list

    def get_performance_data(
            self, start_date, end_date, category, metrics, array_id=None,
            instance_id=None):
        """Retrieve real-time performance statistics for a given category.

        :param start_date: timestamp in milliseconds since epoch -- int
        :param end_date: timestamp in milliseconds since epoch -- int
        :param category: category id -- str
        :param metrics: performance metrics, options are individual metrics,
                        a list of metrics, or 'ALL' for all metrics -- str/list
        :param array_id: array serial number -- str
        :param instance_id: instance id -- str
        :returns: real-time performance data -- dict
        """
        array_id = self.array_id if not array_id else array_id
        metrics = self.format_metrics(metrics)
        self._validate_real_time_input(start_date, end_date, category, metrics,
                                       instance_id)

        request_params = {
            pc.SYMM_ID: array_id, pc.START_DATE: start_date,
            pc.END_DATE: end_date, pc.CATEGORY: category,
            pc.METRICS: metrics}
        if instance_id:
            request_params[pc.INSTANCE_ID] = instance_id

        response = self.post_request(
            no_version=True, category=pc.PERFORMANCE,
            resource_level=pc.REAL_TIME, resource_type=pc.METRICS,
            payload=request_params)
        if not response:
            return None

        return_response = {
            pc.ARRAY_ID: array_id, pc.START_DATE_SN: start_date,
            pc.END_DATE_SN: end_date, pc.TIMESTAMP: end_date,
            pc.REAL_TIME_SN: True,
            pc.REP_LEVEL: self.common.convert_to_snake_case(category),
            pc.RESULT: self.common.get_iterator_results(response)}

        if instance_id:
            return_response[pc.INSTANCE_ID_SN] = instance_id

        return return_response

    # Real-time category specific calls

    def get_array_metrics(self):
        """Get array real-time performance metrics.

        :returns: metrics -- list
        """
        return self.get_category_metrics(pc.ARRAY)

    def get_array_keys(self):
        """Get array IDs which are registered for real-time data.

        :returns: array IDs -- list
        """
        return self.get_category_keys(pc.ARRAY)

    def get_array_stats(self, start_date, end_date, metrics, array_id=None):
        """List real-time data for specified array.

        :param start_date: timestamp in milliseconds since epoch -- int
        :param end_date: timestamp in milliseconds since epoch -- int
        :param metrics: performance metrics, options are individual metrics,
                        a list of metrics, or 'ALL' for all metrics -- str/list
        :param array_id: array serial number -- str
        :returns: real-time performance data -- dict
        """
        return self.get_performance_data(
            start_date=start_date, end_date=end_date, category=pc.ARRAY,
            metrics=metrics, array_id=array_id)

    def get_backend_director_metrics(self):
        """Get backend director real-time performance metrics.

        :returns: metrics -- list
        """
        return self.get_category_metrics(pc.BE_DIR)

    def get_backend_director_keys(self, array_id=None):
        """Get backend director IDs which are registered for real-time data.

        :param array_id: array serial number -- str
        :returns: backend director IDs -- list
        """
        return self.get_category_keys(pc.BE_DIR, array_id)

    def get_backend_director_stats(self, start_date, end_date, metrics,
                                   instance_id, array_id=None):
        """List real-time data for specified backend director.

        :param start_date: timestamp in milliseconds since epoch -- int
        :param end_date: timestamp in milliseconds since epoch -- int
        :param metrics: performance metrics, options are individual metrics,
                        a list of metrics, or 'ALL' for all metrics -- str/list
        :param instance_id: backend director id -- str
        :param array_id: array serial number -- str
        :returns: real-time performance data -- dict
        """
        return self.get_performance_data(
            start_date=start_date, end_date=end_date, category=pc.BE_DIR,
            metrics=metrics, array_id=array_id, instance_id=instance_id)

    def get_backend_port_metrics(self):
        """Get backend port real-time performance metrics.

        :returns: metrics -- list
        """
        return self.get_category_metrics(pc.BE_PORT)

    def get_backend_port_keys(self, array_id=None):
        """Get backend dir/port IDs which are registered for real-time data.

        :param array_id: array serial number -- str
        :returns: backend port IDs -- list
        """
        return self.get_category_keys(pc.BE_PORT, array_id)

    def get_backend_port_stats(self, start_date, end_date, metrics,
                               instance_id, array_id=None):
        """List real-time data for specified backend port.

        :param start_date: timestamp in milliseconds since epoch -- int
        :param end_date: timestamp in milliseconds since epoch -- int
        :param metrics: performance metrics, options are individual metrics,
                        a list of metrics, or 'ALL' for all metrics -- str/list
        :param instance_id: backend dir/port id -- str
        :param array_id: array serial number -- str
        :returns: real-time performance data -- dict
        """
        return self.get_performance_data(
            start_date=start_date, end_date=end_date, category=pc.BE_PORT,
            metrics=metrics, array_id=array_id, instance_id=instance_id)

    def get_external_director_metrics(self):
        """Get external director real-time performance metrics.

        :returns: metrics -- list
        """
        return self.get_category_metrics(pc.EXT_DIR)

    def get_external_director_keys(self, array_id=None):
        """Get external director IDs which are registered for real-time data.

        :param array_id: array serial number -- str
        :returns: external director IDs -- list
        """
        return self.get_category_keys(pc.EXT_DIR, array_id)

    def get_external_director_stats(self, start_date, end_date, metrics,
                                    instance_id, array_id=None):
        """List real-time data for specified external director.

        :param start_date: timestamp in milliseconds since epoch -- int
        :param end_date: timestamp in milliseconds since epoch -- int
        :param metrics: performance metrics, options are individual metrics,
                        a list of metrics, or 'ALL' for all metrics -- str/list
        :param instance_id: external director id -- str
        :param array_id: array serial number -- str
        :returns: real-time performance data -- dict
        """
        return self.get_performance_data(
            start_date=start_date, end_date=end_date, category=pc.EXT_DIR,
            metrics=metrics, array_id=array_id, instance_id=instance_id)

    def get_frontend_director_metrics(self):
        """Get frontend director real-time performance metrics.

        :returns: metrics -- list
        """
        return self.get_category_metrics(pc.FE_DIR)

    def get_frontend_director_keys(self, array_id=None):
        """Get frontend director IDs which are registered for real-time data.

        :param array_id: array serial number -- str
        :returns: frontend director IDs -- list
        """
        return self.get_category_keys(pc.FE_DIR, array_id)

    def get_frontend_director_stats(self, start_date, end_date, metrics,
                                    instance_id, array_id=None):
        """List real-time data for specified frontend director.

        :param start_date: timestamp in milliseconds since epoch -- int
        :param end_date: timestamp in milliseconds since epoch -- int
        :param metrics: performance metrics, options are individual metrics,
                        a list of metrics, or 'ALL' for all metrics -- str/list
        :param instance_id: frontend director id -- str
        :param array_id: array serial number -- str
        :returns: real-time performance data -- dict
        """
        return self.get_performance_data(
            start_date=start_date, end_date=end_date,
            category=pc.FE_DIR, metrics=metrics, array_id=array_id,
            instance_id=instance_id)

    def get_frontend_port_metrics(self):
        """Get frontend port real-time performance metrics.

        :returns: metrics -- list
        """
        return self.get_category_metrics(pc.FE_PORT)

    def get_frontend_port_keys(self, array_id=None):
        """Get frontend dir/port IDs which are registered for real-time data.

        :param array_id: array serial number -- str
        :returns: frontend port IDs -- list
        """
        return self.get_category_keys(pc.FE_PORT, array_id)

    def get_frontend_port_stats(self, start_date, end_date, metrics,
                                instance_id, array_id=None):
        """List real-time data for specified frontend port.

        :param start_date: timestamp in milliseconds since epoch -- int
        :param end_date: timestamp in milliseconds since epoch -- int
        :param metrics: performance metrics, options are individual metrics,
                        a list of metrics, or 'ALL' for all metrics -- str/list
        :param instance_id: frontend dir/port id -- str
        :param array_id: array serial number -- str
        :returns: real-time performance data -- dict
        """
        return self.get_performance_data(
            start_date=start_date, end_date=end_date, category=pc.FE_PORT,
            metrics=metrics, array_id=array_id, instance_id=instance_id)

    def get_rdf_director_metrics(self):
        """Get rdf director real-time performance metrics.

        :returns: metrics -- list
        """
        return self.get_category_metrics(pc.RDF_DIR)

    def get_rdf_director_keys(self, array_id=None):
        """Get rdf director IDs which are registered for real-time data.

        :param array_id: array serial number -- str
        :returns: rdf director IDs -- list
        """
        return self.get_category_keys(pc.RDF_DIR, array_id)

    def get_rdf_director_stats(self, start_date, end_date, metrics,
                               instance_id, array_id=None):
        """List real-time data for specified backend director.

        :param start_date: timestamp in milliseconds since epoch -- int
        :param end_date: timestamp in milliseconds since epoch -- int
        :param metrics: performance metrics, options are individual metrics,
                        a list of metrics, or 'ALL' for all metrics -- str/list
        :param instance_id: rdf director id -- str
        :param array_id: array serial number -- str
        :returns: real-time performance data -- dict
        """
        return self.get_performance_data(
            start_date=start_date, end_date=end_date, category=pc.RDF_DIR,
            metrics=metrics, array_id=array_id, instance_id=instance_id)

    def get_rdf_port_metrics(self):
        """Get rdf port real-time performance metrics.

        :returns: metrics -- list
        """
        return self.get_category_metrics(pc.RDF_PORT)

    def get_rdf_port_keys(self, array_id=None):
        """Get rdf dir/port IDs which are registered for real-time data.

        :param array_id: array serial number -- str
        :returns: rdf port IDs -- list
        """
        return self.get_category_keys(pc.RDF_PORT, array_id)

    def get_rdf_port_stats(self, start_date, end_date, metrics,
                           instance_id, array_id=None):
        """List real-time data for specified rdf port.

        :param start_date: timestamp in milliseconds since epoch -- int
        :param end_date: timestamp in milliseconds since epoch -- int
        :param metrics: performance metrics, options are individual metrics,
                        a list of metrics, or 'ALL' for all metrics -- str/list
        :param instance_id: rdf dir/port id -- str
        :param array_id: array serial number -- str
        :returns: real-time performance data -- dict
        """
        return self.get_performance_data(
            start_date=start_date, end_date=end_date, category=pc.RDF_PORT,
            metrics=metrics, array_id=array_id, instance_id=instance_id)

    def get_storage_group_metrics(self):
        """Get storage group real-time performance metrics.

        :returns: metrics -- list
        """
        return self.get_category_metrics(pc.SG)

    def get_storage_group_keys(self, array_id=None):
        """Get storage group IDs which are registered for real-time data.

        :param array_id: array serial number -- str
        :returns: backend director IDs -- list
        """
        return self.get_category_keys(pc.SG, array_id)

    def get_storage_group_stats(self, start_date, end_date, metrics,
                                instance_id, array_id=None):
        """List real-time data for specified storage group.

        :param start_date: timestamp in milliseconds since epoch -- int
        :param end_date: timestamp in milliseconds since epoch -- int
        :param metrics: performance metrics, options are individual metrics,
                        a list of metrics, or 'ALL' for all metrics -- str/list
        :param instance_id: storage group id -- str
        :param array_id: array serial number -- str
        :returns: real-time performance data -- dict
        """
        return self.get_performance_data(
            start_date=start_date, end_date=end_date, category=pc.SG,
            metrics=metrics, array_id=array_id, instance_id=instance_id)
