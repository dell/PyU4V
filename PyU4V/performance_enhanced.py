# Copyright (c) 2026 Dell Inc. or its subsidiaries.
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
"""performance_enhanced.py."""

import logging

from PyU4V.common import CommonFunctions
from PyU4V.utils import constants

LOG = logging.getLogger(__name__)


class EnhancedPerformanceFunctions:
    """Enhanced Functions for retrieving latest diagnostic level
    performance Metrics."""

    def __init__(self, array_id, rest_client):
        """__init__."""
        self.common = CommonFunctions(rest_client)
        self.array_id = array_id
        self.enhanced_api_version = constants.ENHANCED_API_VERSION

    @staticmethod
    def _build_filter_query(filters):
        """Build the optional filter query string.

        :param filters: list of filter expressions -- list
        :returns: filter query string or empty string -- str
        """
        if filters:
            return '?filter=' + ','.join(filters)
        return ''

    def _perf_uri(self, array_id, category=None):
        """Construct the performance-categories URI.

        :param array_id: 12 Digit Serial Number of Array -- str
        :param category: optional performance category name -- str
        :returns: URI path -- str
        """
        base = (f"/{self.enhanced_api_version}/systems"
                f"/{array_id}/performance-categories")
        if category:
            return f"{base}/{category}"
        return base

    def get_performance_categories_list(self, array_id=None):
        """Get a list of performance categories and metrics that will be
        returned for each category.

        :param array_id: 12 Digit Serial Number of Array -- int
        :returns: a list of categories available for querying, returned list
                 has dictionary of category represented by 'id' key and
                 'metrics' key detailing what will be returned for the given
                 array represented by 'system' key -- list
        """
        array_id = array_id if array_id else self.array_id
        response = self.common.get_request(
            target_uri=self._perf_uri(array_id),
            resource_type=None)
        if response:
            category_list = response['performance_categories']
        else:
            category_list = []
        return category_list

    def get_all_performance_metrics_for_system(self, array_id=None,
                                               filters=None):
        """Get latest data for all KPI metrics.

        :param array_id: 12 Digit Serial Number of Array -- int
        :param filters: users can filter on the time_range and component id,
                        these can be combined in single query,
                        e.g. filters=['time_range eq 1','id ilike Oracle',
                        'data_format eq Maximum']
                        valid values for time range are 1,2,4,8,12,
                        24 in hours, you can also specify data_format to
                        return Average or Maximum values, note for max
                        values to be retuned you must be registered for
                        realtime statistics -- list
        :returns: data for all available categories for the specified PowerMax
                 Array diagnostic level metrics only, 5 min interval -- dict
        """
        array_id = array_id if array_id else self.array_id
        category_list = self.get_performance_categories_list(
            array_id=array_id)
        full_metric_collection = []
        # Build the optional filter part – empty string when no filters.
        filter_part = self._build_filter_query(filters)
        for category in category_list:
            response = self.common.get_request(
                target_uri=(self._perf_uri(array_id, category['id'])
                            + filter_part),
                resource_type=None)
            if response is not None:
                full_metric_collection.append(response)
        return full_metric_collection

    def get_category_metrics(self, category: str, array_id=None, filters=None,
                             all_metrics=False):
        """Get latest data for KPI metrics for specificied performance
        category.

        :param category: performance category name -- str
        :param array_id: 12 Digit Serial Number of Array -- int
        :param filters: users can filter on the time_range and component id,
                        these can be combined in single query,
                        e.g. filters=['time_range eq 1','id ilike Oracle',
                        'data_format eq Maximum']
                        valid values for time range are 1,2,4,8,12,
                        24 in hours, you can also specify data_format to
                        return Average or Maximum values, note for max
                        values to be retuned you must be registered for
                        realtime statistics -- list
        :param all_metrics: when True adds 'metric_type eq All' filter to
                            return all available metrics instead of KPI
                            metrics only, default is False -- bool
        :returns: full list of all KPI metrics for latest diagnostic
                 timestamp for the specified array and performance category --
                 dict
        """
        array_id = array_id if array_id else self.array_id
        effective_filters = list(filters) if filters else []
        if all_metrics:
            effective_filters.append('metric_type eq All')
        # Build the optional filter part – empty string when no filters.
        filter_part = self._build_filter_query(
            effective_filters if effective_filters else None)
        response = self.common.get_request(
            target_uri=(self._perf_uri(array_id, category)
                        + filter_part),
            resource_type=None)
        return response
